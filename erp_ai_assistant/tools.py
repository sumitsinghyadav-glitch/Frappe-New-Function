"""Tools the assistant can call. Every tool runs as the logged-in user, so ERPNext
permissions apply exactly as they would in the UI."""

import json

import frappe
from frappe.utils import cint, strip_html

# Standard ERPNext "Create ->" mappings, keyed by (source doctype, target doctype).
MAPPERS = {
	("Material Request", "Purchase Order"): "erpnext.stock.doctype.material_request.material_request.make_purchase_order",
	("Material Request", "Request for Quotation"): "erpnext.stock.doctype.material_request.material_request.make_request_for_quotation",
	("Supplier Quotation", "Purchase Order"): "erpnext.buying.doctype.supplier_quotation.supplier_quotation.make_purchase_order",
	("Purchase Order", "Purchase Receipt"): "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt",
	("Purchase Order", "Purchase Invoice"): "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_invoice",
	("Purchase Receipt", "Purchase Invoice"): "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
	("Purchase Receipt", "Purchase Return"): "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_return",
	("Quotation", "Sales Order"): "erpnext.selling.doctype.quotation.quotation.make_sales_order",
	("Quotation", "Sales Invoice"): "erpnext.selling.doctype.quotation.quotation.make_sales_invoice",
	("Sales Order", "Delivery Note"): "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
	("Sales Order", "Sales Invoice"): "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
	("Sales Order", "Material Request"): "erpnext.selling.doctype.sales_order.sales_order.make_material_request",
	("Delivery Note", "Sales Invoice"): "erpnext.stock.doctype.delivery_note.delivery_note.make_sales_invoice",
	("Delivery Note", "Sales Return"): "erpnext.stock.doctype.delivery_note.delivery_note.make_sales_return",
	("Delivery Note", "Purchase Receipt"): "erpnext.stock.doctype.delivery_note.delivery_note.make_inter_company_purchase_receipt",
	("Sales Invoice", "Purchase Invoice"): "erpnext.accounts.doctype.sales_invoice.sales_invoice.make_inter_company_purchase_invoice",
	("Sales Invoice", "Delivery Note"): "erpnext.accounts.doctype.sales_invoice.sales_invoice.make_delivery_note",
}
PAYMENT_SOURCES = ("Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order")

SUMMARY_FIELDS = (
	"customer", "supplier", "party_name", "company", "posting_date", "transaction_date", "schedule_date",
	"delivery_date", "status", "net_total", "total_taxes_and_charges", "grand_total", "outstanding_amount",
	"paid_amount", "set_warehouse", "set_target_warehouse", "purpose", "taxes_and_charges",
)
ITEM_FIELDS = ("item_code", "qty", "rate", "amount", "warehouse", "s_warehouse", "t_warehouse", "uom")

FLOW_ITEMS_SCHEMA = {
	"type": "array",
	"description": "Items exactly as the user said them",
	"items": {
		"type": "object",
		"properties": {
			"item": {"type": "string", "description": "Item code or item name"},
			"qty": {"type": "number"},
			"rate": {"type": "number", "description": "Optional price per unit"},
		},
		"required": ["item", "qty"],
	},
}

PURCHASE_UPTO = ["order", "order+receipt", "order+receipt+invoice", "order+receipt+invoice+payment"]
SALES_UPTO = ["order", "order+delivery", "order+delivery+invoice", "order+delivery+invoice+payment"]

TOOLS = [
	{
		"name": "purchase_flow",
		"description": (
			"One call for a whole buying flow: Purchase Order -> Purchase Receipt -> Purchase Invoice -> Payment Entry. "
			"Pass names as the user wrote them; they are matched to masters automatically. "
			"Set 'upto' to all the steps requested. Use this for any purchase request, and with continue_from for follow-ups on an existing document."
		),
		"input_schema": {
			"type": "object",
			"properties": {
				"supplier": {"type": "string"},
				"items": FLOW_ITEMS_SCHEMA,
				"warehouse": {"type": "string", "description": "Optional receiving warehouse"},
				"company": {"type": "string", "description": "Optional, default company if empty"},
				"required_by": {"type": "string", "description": "Optional date YYYY-MM-DD"},
				"upto": {"type": "string", "enum": PURCHASE_UPTO, "description": "All the steps the user asked for, e.g. order+receipt+invoice when they want the PO received and invoiced"},
				"continue_from": {"type": "string", "description": "Optional: name of an existing submitted PO / receipt / invoice to continue from instead of creating a new order (supplier and items can then be left out)"},
				"submit": {"type": "boolean", "description": "Submit the documents. Default true when upto is beyond order."},
			},
			"required": ["upto"],
		},
	},
	{
		"name": "sales_flow",
		"description": (
			"One call for a whole selling flow: Sales Order -> Delivery Note -> Sales Invoice -> Payment Entry. "
			"Pass names as the user wrote them; they are matched to masters automatically. "
			"Set 'upto' to all the steps requested. Use this for any sales request, and with continue_from for follow-ups on an existing document."
		),
		"input_schema": {
			"type": "object",
			"properties": {
				"customer": {"type": "string"},
				"items": FLOW_ITEMS_SCHEMA,
				"warehouse": {"type": "string", "description": "Optional warehouse to deliver from"},
				"company": {"type": "string", "description": "Optional, default company if empty"},
				"delivery_date": {"type": "string", "description": "Optional date YYYY-MM-DD"},
				"upto": {"type": "string", "enum": SALES_UPTO, "description": "All the steps the user asked for, e.g. order+delivery+invoice when they want the order delivered and invoiced"},
				"continue_from": {"type": "string", "description": "Optional: name of an existing submitted sales order / delivery note / invoice to continue from instead of creating a new order (customer and items can then be left out)"},
				"submit": {"type": "boolean", "description": "Submit the documents. Default true when upto is beyond order."},
			},
			"required": ["upto"],
		},
	},
	{
		"name": "stock_transfer",
		"description": (
			"One call to move stock between two warehouses of the same company (Stock Entry, Material Transfer). "
			"Pass names as the user wrote them; they are matched automatically. Submitted unless submit is false."
		),
		"input_schema": {
			"type": "object",
			"properties": {
				"from_warehouse": {"type": "string"},
				"to_warehouse": {"type": "string"},
				"items": FLOW_ITEMS_SCHEMA,
				"submit": {"type": "boolean", "description": "Default true"},
			},
			"required": ["from_warehouse", "to_warehouse", "items"],
		},
	},
	{
		"name": "search_records",
		"description": (
			"Find existing records (masters or transactions) in ERPNext. Use this before creating anything "
			"to resolve real names of customers, suppliers, items, warehouses, companies, tax templates, "
			"price lists, accounts, etc. Never guess a name that you have not found with this tool."
		),
		"input_schema": {
			"type": "object",
			"properties": {
				"doctype": {"type": "string", "description": "DocType to search, e.g. Customer, Item, Warehouse"},
				"search_text": {"type": "string", "description": "Partial text matched against name and title fields"},
				"filters": {
					"type": "object",
					"description": 'Exact filters, e.g. {"company": "Sumit", "is_group": 0} or {"docstatus": 1}',
				},
				"fields": {"type": "array", "items": {"type": "string"}, "description": "Extra fields to return"},
				"limit": {"type": "integer", "description": "Max rows, default 20, max 50"},
			},
			"required": ["doctype"],
		},
	},
	{
		"name": "get_doctype_schema",
		"description": (
			"Get the important fields of a DocType: mandatory fields, link fields with their target doctype, "
			"select options and child tables with their key columns. Use before creating a doctype you are not sure about."
		),
		"input_schema": {
			"type": "object",
			"properties": {"doctype": {"type": "string"}},
			"required": ["doctype"],
		},
	},
	{
		"name": "get_document",
		"description": "Read one document with its child tables, e.g. to check status, items or totals.",
		"input_schema": {
			"type": "object",
			"properties": {"doctype": {"type": "string"}, "name": {"type": "string"}},
			"required": ["doctype", "name"],
		},
	},
	{
		"name": "get_stock_balance",
		"description": "Current stock quantity and value of an item, per warehouse.",
		"input_schema": {
			"type": "object",
			"properties": {
				"item_code": {"type": "string"},
				"warehouse": {"type": "string", "description": "Optional, limit to one warehouse"},
			},
			"required": ["item_code"],
		},
	},
	{
		"name": "create_document",
		"description": (
			"Create a new document as Draft. Pass the full document as JSON including 'doctype' and child tables "
			'(e.g. "items": [{"item_code": ..., "qty": ..., "rate": ...}]). ERPNext fills defaults such as '
			"price, accounts and taxes. Returns the saved document summary or the validation error to fix."
		),
		"input_schema": {
			"type": "object",
			"properties": {"doc": {"type": "object", "description": "Document fields, must include doctype"}},
			"required": ["doc"],
		},
	},
	{
		"name": "make_mapped_document",
		"description": (
			"Create the next document in a flow from a SUBMITTED source document using ERPNext's standard "
			"'Create' button mapping, so links and pending quantities are carried over. Supported: "
			+ "; ".join(f"{s} -> {t}" for s, t in MAPPERS)
			+ "; Sales Invoice/Purchase Invoice/Sales Order/Purchase Order -> Payment Entry. "
			"Optional 'values' overrides header fields; to change item rows pass "
			'"items": [{"idx": 1, "qty": 5, "warehouse": "..."}] (matched by idx or item_code). Saved as Draft.'
		),
		"input_schema": {
			"type": "object",
			"properties": {
				"source_doctype": {"type": "string"},
				"source_name": {"type": "string"},
				"target_doctype": {"type": "string"},
				"values": {"type": "object", "description": "Optional field overrides for the new document"},
			},
			"required": ["source_doctype", "source_name", "target_doctype"],
		},
	},
	{
		"name": "update_document",
		"description": (
			"Change fields of a Draft document. Child rows can be updated with "
			'"items": [{"idx": 1, "qty": 5}] (matched by idx or item_code).'
		),
		"input_schema": {
			"type": "object",
			"properties": {
				"doctype": {"type": "string"},
				"name": {"type": "string"},
				"values": {"type": "object"},
			},
			"required": ["doctype", "name", "values"],
		},
	},
	{
		"name": "submit_document",
		"description": (
			"Submit a Draft document (final posting to stock and accounts). Only do this when the user asked "
			"to submit / complete / post, or when a later step of a flow they requested needs it submitted."
		),
		"input_schema": {
			"type": "object",
			"properties": {"doctype": {"type": "string"}, "name": {"type": "string"}},
			"required": ["doctype", "name"],
		},
	},
]

WRITE_TOOLS = {"create_document", "make_mapped_document", "update_document", "submit_document", "purchase_flow", "sales_flow", "stock_transfer"}


def doc_url(doctype, name):
	return f"/app/{frappe.scrub(doctype).replace('_', '-')}/{name}"


def summarize(doc):
	out = {
		"doctype": doc.doctype,
		"name": doc.name,
		"state": {0: "Draft", 1: "Submitted", 2: "Cancelled"}[doc.docstatus],
		"url": doc_url(doc.doctype, doc.name),
	}
	for f in SUMMARY_FIELDS:
		v = doc.get(f)
		if v not in (None, "", 0, 0.0):
			out[f] = str(v) if not isinstance(v, (int, float)) else v
	for table in ("items", "accounts", "references"):
		rows = doc.get(table)
		if rows:
			out[table] = [
				{k: r.get(k) for k in (*ITEM_FIELDS, "account", "debit", "credit", "reference_doctype", "reference_name", "allocated_amount") if r.get(k) not in (None, "", 0)}
				for r in rows[:30]
			]
	if doc.get("taxes"):
		out["taxes"] = [{"account": t.account_head, "amount": t.tax_amount} for t in doc.taxes]
	return out


def compact(value):
	"""Drop empty values so documents fit comfortably in the model's context."""
	if isinstance(value, dict):
		return {k: compact(v) for k, v in value.items() if v not in (None, "", [], {}, 0, 0.0) and not k.startswith("_")}
	if isinstance(value, list):
		return [compact(v) for v in value]
	return value


def resolve_name(doctype, value):
	"""Map a display name ("MS Steel Pipe") to the record name ("STEEL-PIPE-2IN") when exactly one record matches.
	Small models often pass names instead of codes; this keeps them on track without guessing."""
	if not value or not isinstance(value, str) or frappe.db.exists(doctype, value):
		return value
	meta = frappe.get_meta(doctype)
	fields = [f for f in [meta.title_field, *(meta.search_fields or "").split(",")] if f and meta.has_field(f.strip())]
	for op, pattern in (("=", value), ("like", f"%{value}%")):
		for f in fields:
			rows = frappe.get_list(doctype, filters={f.strip(): [op, pattern]}, pluck="name", limit_page_length=2)
			if len(rows) == 1:
				return rows[0]
		rows = frappe.get_list(doctype, filters={"name": ["like", f"%{value}%"]}, pluck="name", limit_page_length=2)
		if len(rows) == 1:
			return rows[0]
	return value


def fill_taxes(doc):
	"""A document built with frappe.get_doc() is not 'new' to set_taxes(), so ERPNext/India Compliance pick the
	tax template but leave the tax rows empty. Fill them from the template like the form does."""
	if not doc.meta.has_field("taxes_and_charges"):
		return doc
	if hasattr(doc, "set_missing_values"):
		doc.set_missing_values()
	if doc.get("taxes_and_charges") and not doc.get("taxes"):
		doc.append_taxes_from_master()
	return doc


def resolve_links(doctype, data):
	meta = frappe.get_meta(doctype)
	for key, val in list(data.items()):
		df = meta.get_field(key)
		if not df:
			continue
		if df.fieldtype == "Link" and df.options and isinstance(val, str):
			data[key] = resolve_name(df.options, val)
		elif df.fieldtype in ("Table", "Table MultiSelect") and isinstance(val, list):
			for row in val:
				if isinstance(row, dict):
					resolve_links(df.options, row)
	return data


def apply_values(doc, values):
	values = resolve_links(doc.doctype, dict(values or {}))
	for key, val in (values or {}).items():
		if isinstance(val, list) and doc.meta.get_field(key) and doc.meta.get_field(key).fieldtype in ("Table", "Table MultiSelect"):
			existing = doc.get(key) or []
			for patch in val:
				row = None
				if patch.get("idx"):
					row = next((r for r in existing if r.idx == cint(patch["idx"])), None)
				elif patch.get("item_code"):
					row = next((r for r in existing if r.get("item_code") == patch["item_code"]), None)
				if row:
					row.update({k: v for k, v in patch.items() if k != "idx"})
				else:
					doc.append(key, {k: v for k, v in patch.items() if k != "idx"})
		else:
			doc.set(key, val)


# ------------------------------------------------------------------ tool implementations
def search_records(doctype, search_text=None, filters=None, fields=None, limit=20):
	meta = frappe.get_meta(doctype)
	# Small models often put the name into filters ({"name": "Summit Traders"}, {"warehouse": "Gwalior Plant"}).
	# Exact text filters that would miss, or fields that don't exist, become a partial-text search instead.
	clean = {}
	for k, v in (filters or {}).items():
		valid = k in ("name", "docstatus") or meta.has_field(k)
		if isinstance(v, str) and (not valid or not frappe.db.exists(doctype, {k: v})):
			search_text = search_text or v
		elif valid:
			clean[k] = v
	filters = clean
	cols = ["name"]
	for f in [meta.title_field, *(meta.search_fields or "").split(",")]:
		f = (f or "").strip()
		if f and meta.has_field(f) and f not in cols:
			cols.append(f)
	for f in fields or []:
		if (meta.has_field(f) or f in ("docstatus", "creation", "modified")) and f not in cols:
			cols.append(f)
	or_filters = None
	if search_text:
		or_filters = [[c, "like", f"%{search_text}%"] for c in cols if c == "name" or meta.get_field(c).fieldtype in ("Data", "Link", "Small Text", "Text")]
	rows = frappe.get_list(
		doctype, filters=filters or {}, or_filters=or_filters, fields=cols,
		limit_page_length=min(cint(limit) or 20, 50), order_by="modified desc",
	)
	return {"count": len(rows), "rows": rows}


def get_doctype_schema(doctype):
	meta = frappe.get_meta(doctype)

	def fields_of(m, child=False):
		out = []
		for df in m.fields:
			if df.fieldtype in ("Section Break", "Column Break", "Tab Break", "HTML", "Button", "Fold"):
				continue
			keep = df.reqd or df.fieldtype in ("Table", "Table MultiSelect") or (
				df.fieldtype in ("Link", "Date", "Select") and not df.hidden and not df.read_only
			) or (child and df.in_list_view)
			if not keep:
				continue
			f = {"fieldname": df.fieldname, "type": df.fieldtype}
			if df.reqd:
				f["mandatory"] = True
			if df.options and df.fieldtype in ("Link", "Select", "Table", "Table MultiSelect"):
				f["options"] = df.options
			if df.default:
				f["default"] = df.default
			if df.fieldtype in ("Table", "Table MultiSelect") and not child:
				f["columns"] = fields_of(frappe.get_meta(df.options), child=True)
			out.append(f)
		return out

	return {"doctype": doctype, "is_submittable": bool(meta.is_submittable), "fields": fields_of(meta)}


def get_document(doctype, name):
	doc = frappe.get_doc(doctype, name)
	doc.check_permission("read")
	data = compact(doc.as_dict(no_default_fields=True, convert_dates_to_str=True))
	data["name"], data["docstatus"], data["url"] = doc.name, doc.docstatus, doc_url(doctype, doc.name)
	return data


def get_stock_balance(item_code, warehouse=None):
	item_code = resolve_name("Item", item_code)
	if not frappe.db.exists("Item", item_code):
		raise frappe.ValidationError(f"Item '{item_code}' not found. Use search_records on Item to find the item code.")
	filters = {"item_code": item_code}
	if warehouse:
		filters["warehouse"] = resolve_name("Warehouse", warehouse)
	rows = frappe.get_list("Bin", filters=filters, fields=["warehouse", "actual_qty", "reserved_qty", "projected_qty", "stock_value"])
	return {"item_code": item_code, "warehouses": rows}


def create_document(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)
	if not doc.get("doctype"):
		raise frappe.ValidationError("doc must include 'doctype'")
	new = fill_taxes(frappe.get_doc(resolve_links(doc["doctype"], doc)))
	new.insert()
	return summarize(new)


def make_mapped_document(source_doctype, source_name, target_doctype, values=None):
	if target_doctype == "Payment Entry" and source_doctype in PAYMENT_SOURCES:
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		new = get_payment_entry(source_doctype, source_name)
	else:
		path = MAPPERS.get((source_doctype, target_doctype))
		if not path:
			raise frappe.ValidationError(f"No standard mapping from {source_doctype} to {target_doctype}")
		frappe.get_doc(source_doctype, source_name).check_permission("read")
		new = frappe.get_attr(path)(source_name)
	if isinstance(new, dict):
		new = frappe.get_doc(new)
	apply_values(new, values)
	new.insert()
	return summarize(new)


def update_document(doctype, name, values):
	doc = frappe.get_doc(doctype, name)
	if doc.docstatus != 0:
		raise frappe.ValidationError(f"{doctype} {name} is not a Draft and cannot be edited")
	apply_values(doc, values)
	doc.save()
	return summarize(doc)


def submit_document(doctype, name):
	doc = frappe.get_doc(doctype, name)
	doc.submit()
	return summarize(doc)


# ------------------------------------------------------------------ one-call flows
def must_resolve(doctype, value, label=None):
	name = resolve_name(doctype, value)
	if name and frappe.db.exists(doctype, name):
		return name
	word = (value or "").split()[0] if value else ""
	hints = frappe.get_list(doctype, filters={"name": ["like", f"%{word}%"]}, pluck="name", limit_page_length=5) if word else []
	raise frappe.ValidationError(
		f"{label or doctype} '{value}' not found or matches several records."
		+ (f" Did you mean: {', '.join(hints)}?" if hints else " Ask the user for the exact name.")
	)


def default_company(company=None, warehouse=None):
	if company:
		return must_resolve("Company", company)
	if warehouse:
		return frappe.db.get_value("Warehouse", warehouse, "company")
	return frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")


def flow_items(items, warehouse, date_field, date_value):
	rows = []
	for it in items or []:
		row = {"item_code": must_resolve("Item", it.get("item"), "Item"), "qty": it.get("qty") or 1, date_field: date_value}
		if it.get("rate"):
			row["rate"] = it["rate"]
		if warehouse:
			row["warehouse"] = warehouse
		rows.append(row)
	if not rows:
		raise frappe.ValidationError("No items given")
	return rows


def run_flow(steps, upto, submit, continue_from=None):
	"""steps: list of (key, doctype, make_doc(previous_doc) -> unsaved doc). Each finished step is committed,
	so a failure later keeps the documents already made and reports where it stopped.
	continue_from: an existing submitted document of one of the step doctypes to carry on from."""
	keys = [k for k, _, _ in steps]
	last_key = (upto or "").split("+")[-1].strip()
	if last_key not in keys:
		raise frappe.ValidationError(f"upto must end with one of {keys}")
	last = keys.index(last_key)
	if submit is None:
		submit = last > 0
	start, prev = 0, None
	if continue_from:
		for i, (_, doctype, _) in enumerate(steps):
			if frappe.db.exists(doctype, continue_from):
				prev = frappe.get_doc(doctype, continue_from)
				prev.check_permission("read")
				if prev.docstatus != 1:
					raise frappe.ValidationError(f"{doctype} {continue_from} must be submitted before continuing")
				start = i + 1
				break
		else:
			raise frappe.ValidationError(f"Document '{continue_from}' not found among {[d for _, d, _ in steps]}")
	done = []
	for i, (key, _, make) in enumerate(steps[: last + 1]):
		if i < start:
			continue
		try:
			doc = make(prev)
			doc.insert()
			if submit or i < last:
				doc.submit()
			frappe.db.commit()
			done.append(summarize(doc))
			prev = doc
		except Exception as e:
			frappe.db.rollback()
			return {"documents": done, "error": f"Stopped at '{key}': {error_text(e)}"}
	return {"documents": done}


def purchase_flow(upto, supplier=None, items=None, warehouse=None, company=None, required_by=None, submit=None, continue_from=None):
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
	from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
	from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice

	def new_order(_):
		if not supplier:
			raise frappe.ValidationError("supplier is required to create a new purchase order")
		wh = must_resolve("Warehouse", warehouse) if warehouse else None
		date = required_by or frappe.utils.add_days(frappe.utils.nowdate(), 7)
		po = {"doctype": "Purchase Order", "company": default_company(company, wh), "supplier": must_resolve("Supplier", supplier),
			  "schedule_date": date, "items": flow_items(items, wh, "schedule_date", date)}
		if wh:
			po["set_warehouse"] = wh
		return fill_taxes(frappe.get_doc(po))

	return run_flow([
		("order", "Purchase Order", new_order),
		("receipt", "Purchase Receipt", lambda prev: make_purchase_receipt(prev.name)),
		("invoice", "Purchase Invoice", lambda prev: make_purchase_invoice(prev.name)),
		("payment", "Payment Entry", lambda prev: get_payment_entry("Purchase Invoice", prev.name)),
	], upto, submit, continue_from)


def sales_flow(upto, customer=None, items=None, warehouse=None, company=None, delivery_date=None, submit=None, continue_from=None):
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
	from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
	from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice

	def new_order(_):
		if not customer:
			raise frappe.ValidationError("customer is required to create a new sales order")
		wh = must_resolve("Warehouse", warehouse) if warehouse else None
		date = delivery_date or frappe.utils.add_days(frappe.utils.nowdate(), 7)
		so = {"doctype": "Sales Order", "company": default_company(company, wh), "customer": must_resolve("Customer", customer),
			  "delivery_date": date, "items": flow_items(items, wh, "delivery_date", date)}
		if wh:
			so["set_warehouse"] = wh
		return fill_taxes(frappe.get_doc(so))

	return run_flow([
		("order", "Sales Order", new_order),
		("delivery", "Delivery Note", lambda prev: make_delivery_note(prev.name)),
		("invoice", "Sales Invoice", lambda prev: make_sales_invoice(prev.name)),
		("payment", "Payment Entry", lambda prev: get_payment_entry("Sales Invoice", prev.name)),
	], upto, submit, continue_from)


def stock_transfer(from_warehouse, to_warehouse, items, submit=True):
	src = must_resolve("Warehouse", from_warehouse, "Source warehouse")
	dst = must_resolve("Warehouse", to_warehouse, "Target warehouse")
	company = frappe.db.get_value("Warehouse", src, "company")
	if company != frappe.db.get_value("Warehouse", dst, "company"):
		raise frappe.ValidationError("Both warehouses must belong to the same company; use the internal transfer flow between companies/GSTINs.")
	rows = [
		{"item_code": must_resolve("Item", it.get("item"), "Item"), "qty": it.get("qty") or 1, "s_warehouse": src, "t_warehouse": dst}
		for it in items or []
	]
	if not rows:
		raise frappe.ValidationError("No items given")

	def make(_):
		return frappe.get_doc({"doctype": "Stock Entry", "stock_entry_type": "Material Transfer", "purpose": "Material Transfer",
							   "company": company, "from_warehouse": src, "to_warehouse": dst, "items": rows})

	return run_flow([("transfer", "Stock Entry", make)], "transfer", True if submit is None else bool(submit))


def error_text(e):
	messages = []
	for m in frappe.local.message_log or []:
		if isinstance(m, str):
			try:
				m = json.loads(m)
			except ValueError:
				m = {"message": m}
		messages.append(strip_html(str(m.get("message", ""))))
	frappe.clear_messages()
	return ("; ".join(m for m in messages if m) or strip_html(str(e)) or e.__class__.__name__)[:1500]


IMPLEMENTATIONS = {
	"purchase_flow": purchase_flow,
	"sales_flow": sales_flow,
	"stock_transfer": stock_transfer,
	"search_records": search_records,
	"get_doctype_schema": get_doctype_schema,
	"get_document": get_document,
	"get_stock_balance": get_stock_balance,
	"create_document": create_document,
	"make_mapped_document": make_mapped_document,
	"update_document": update_document,
	"submit_document": submit_document,
}


def run_tool(name, args):
	"""Run one tool. Returns (result_json_text, is_error, summary_or_None)."""
	fn = IMPLEMENTATIONS.get(name)
	if not fn:
		return json.dumps({"error": f"Unknown tool {name}"}), True, None
	frappe.clear_messages()
	try:
		result = fn(**(args or {}))
		if name in WRITE_TOOLS:
			frappe.db.commit()
		return json.dumps(result, default=str), False, result if name in WRITE_TOOLS else None
	except Exception as e:
		frappe.db.rollback()
		return json.dumps({"error": error_text(e)}), True, None
