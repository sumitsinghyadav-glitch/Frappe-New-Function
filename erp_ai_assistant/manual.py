"""Builds the ERP user manual (ERP Help Article, type "DocType Manual") from this site's own metadata.

Every screen gets an article: purpose, where to find it, how to create it, every field (custom ones marked),
linkage (masters it uses, documents that use it, Create-flows), reports, workflow, customizations
(custom fields, property setters, client/server scripts, notifications) and who can use it.

Rebuilt automatically: one screen when its DocType / Custom Field / Property Setter / Workflow / Report /
Client Script / Server Script / Notification changes, and everything nightly and after migrate."""

import json
from collections import defaultdict

import frappe
from frappe.utils import now_datetime, strip_html

from erp_ai_assistant.kb import FIELD_NOTES
from erp_ai_assistant.tools import MAPPERS

LAYOUT = ("Section Break", "Column Break", "Tab Break", "HTML", "Button", "Fold", "Heading", "Image")
# Frappe framework screens that business users actually work with
FRAPPE_KEEP = {
	"User", "Role", "Role Profile", "Address", "Contact", "System Settings", "Data Import", "Data Export", "Print Settings",
	"Print Format", "Letter Head", "Email Account", "Email Template", "Notification", "Workflow", "Custom Field",
	"Property Setter", "Client Script", "Server Script", "Report", "Number Card", "Dashboard Chart", "Auto Repeat",
	"Assignment Rule", "Document Naming Settings", "Currency", "Country", "ToDo", "File", "Customize Form", "Web Form",
}
TYPE_TEXT = {
	"Data": "text", "Small Text": "text", "Text": "text", "Long Text": "text", "Text Editor": "formatted text",
	"Markdown Editor": "formatted text", "Code": "code", "Int": "whole number", "Float": "number", "Currency": "amount",
	"Percent": "percentage", "Date": "date", "Datetime": "date & time", "Time": "time", "Check": "tick box",
	"Attach": "file", "Attach Image": "image", "Signature": "signature", "Phone": "phone", "Password": "secret",
	"Rating": "rating", "Duration": "duration", "Geolocation": "map location", "JSON": "data", "Color": "colour",
	"Read Only": "display only", "Autocomplete": "text with suggestions",
}
WATCHED = {
	# doctype changed -> attribute holding the affected screen
	"DocType": "name", "Custom Field": "dt", "Property Setter": "doc_type", "Client Script": "dt",
	"Server Script": "reference_doctype", "Workflow": "document_type", "Report": "ref_doctype",
	"Notification": "document_type",
}


def slug(doctype):
	return frappe.scrub(doctype).replace("_", "-")


# ------------------------------------------------------------------ system-wide indexes (one pass)
class SiteIndex:
	def __init__(self):
		from erp_ai_assistant.help import sidebar_index

		self.sidebar = sidebar_index()
		self.apps = dict(frappe.get_all("Module Def", fields=["name", "app_name"], as_list=True))
		self.child_parents = defaultdict(set)
		self.used_in = defaultdict(set)  # master doctype -> doctypes that link to it
		links = frappe.db.sql(
			"""select parent, options, fieldtype from `tabDocField` where fieldtype in ('Link','Table','Table MultiSelect') and ifnull(options,'')!=''
			union all
			select dt, options, fieldtype from `tabCustom Field` where fieldtype in ('Link','Table','Table MultiSelect') and ifnull(options,'')!=''""",
			as_dict=True,
		)
		for r in links:
			if r.fieldtype != "Link":
				self.child_parents[r.options].add(r.parent)
		for r in links:
			if r.fieldtype == "Link":
				owners = self.child_parents.get(r.parent) or {r.parent}
				for o in owners:
					if o != r.options:
						self.used_in[r.options].add(o)
		self.reports = defaultdict(list)
		for r in frappe.get_all("Report", filters={"disabled": 0}, fields=["name", "ref_doctype", "report_type", "is_standard"]):
			self.reports[r.ref_doctype].append(r)
		# Only the company's own changes count as customizations; fields/properties that installed apps
		# (India Compliance, HRMS...) add are marked is_system_generated and are part of standard behaviour.
		self.custom_fields = defaultdict(list)
		for r in frappe.get_all("Custom Field", filters={"is_system_generated": 0}, fields=["dt", "label", "fieldname", "fieldtype", "options", "description", "reqd"]):
			self.custom_fields[r.dt].append(r)
		self.props = defaultdict(list)
		for r in frappe.get_all("Property Setter", filters={"is_system_generated": 0}, fields=["doc_type", "field_name", "property", "value"]):
			self.props[r.doc_type].append(r)
		self.client_scripts = defaultdict(list)
		for r in frappe.get_all("Client Script", fields=["name", "dt", "enabled", "view"]):
			self.client_scripts[r.dt].append(r)
		self.server_scripts = defaultdict(list)
		for r in frappe.get_all("Server Script", fields=["name", "reference_doctype", "doctype_event", "script_type", "disabled"]):
			if r.reference_doctype:
				self.server_scripts[r.reference_doctype].append(r)
		self.notifications = defaultdict(list)
		for r in frappe.get_all("Notification", fields=["name", "document_type", "event", "enabled", "subject"]):
			self.notifications[r.document_type].append(r)
		self.workflows = {}
		for w in frappe.get_all("Workflow", filters={"is_active": 1}, fields=["name", "document_type"]):
			self.workflows[w.document_type] = frappe.get_doc("Workflow", w.name)


def wanted(dt, idx):
	app = idx.apps.get(dt.module)
	return bool(dt.custom) or (app and app != "frappe") or dt.name in FRAPPE_KEEP


# ------------------------------------------------------------------ article
def field_text(df):
	note = FIELD_NOTES.get(df.fieldname) or strip_html(df.description or "").strip()
	ft = df.fieldtype
	if ft == "Link":
		kind = f"pick a **{df.options}**"
	elif ft == "Dynamic Link":
		kind = "pick a record (type chosen in another field)"
	elif ft == "Select":
		opts = [o for o in (df.options or "").split("\n") if o]
		kind = "choose: " + ", ".join(opts[:8]) + ("…" if len(opts) > 8 else "")
	elif ft in ("Table", "Table MultiSelect"):
		kind = f"table of **{df.options}** rows"
	else:
		kind = TYPE_TEXT.get(ft, ft.lower())
	flags = []
	if df.reqd:
		flags.append("mandatory")
	if df.fetch_from:
		flags.append(f"auto-filled from {df.fetch_from.split('.')[0].replace('_', ' ')}")
	elif df.read_only:
		flags.append("system-filled")
	if df.depends_on:
		flags.append("shown only in some cases")
	if df.allow_on_submit:
		flags.append("editable after submit")
	return f"{note + ' ' if note else ''}_({kind}{'; ' + ', '.join(flags) if flags else ''})_"


def build_article(doctype, idx):
	meta = frappe.get_meta(doctype)
	custom_fieldnames = {c.fieldname for c in idx.custom_fields.get(doctype, [])}
	kind = "Settings" if meta.issingle else "Transaction" if meta.is_submittable else "Master / record"
	paths = idx.sidebar.get(doctype) or []
	path = next((p for p in paths if p[0] == meta.module), paths[0] if paths else None)
	app = idx.apps.get(meta.module) or ""
	parts, data = [], {"kind": kind, "module": meta.module, "app": app, "custom_doctype": bool(meta.custom)}

	# Purpose
	purpose = strip_html(meta.description or "").strip()
	parts.append(f"# {doctype}\n\n**Type:** {kind} · **Module:** {meta.module}" + (f" · **App:** {app}" if app else "")
				 + (" · 🛠 **Custom screen (built for this company)**" if meta.custom else ""))
	if purpose:
		parts.append(purpose)

	# Where
	where = " → ".join(path) if path else f"module {meta.module}"
	data["where"] = path or [meta.module]
	parts.append(
		f"## Where to find it\n- Menu: **{where}**\n- Search bar (Ctrl+G): type *{doctype}*\n- Link: [/app/{slug(doctype)}](/app/{slug(doctype)})"
		+ ("" if meta.issingle else f" · New: [/app/{slug(doctype)}/new](/app/{slug(doctype)}/new)")
	)

	# How to create
	mandatory = [df for df in meta.fields if df.reqd and df.fieldtype not in LAYOUT and not df.read_only]
	data["mandatory"] = [df.label for df in mandatory]
	prev = sorted({s for (s, t) in MAPPERS if t == doctype})
	nxt = sorted({t for (s, t) in MAPPERS if s == doctype})
	if doctype in ("Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order"):
		nxt.append("Payment Entry")
	data["prev"], data["next"] = prev, nxt
	how = ["## How to create / use it"]
	if meta.issingle:
		how.append(f"This is a settings page: open [/app/{slug(doctype)}](/app/{slug(doctype)}), change values, **Save**.")
	else:
		how.append(f"1. Open [+ New {doctype}](/app/{slug(doctype)}/new)" + (f" or create it from {', '.join(prev)} (**Create → {doctype}**)" if prev else "") + ".")
		if mandatory:
			how.append("2. Fill the mandatory fields: " + ", ".join(f"**{df.label}**" for df in mandatory[:15]) + ".")
		how.append("3. **Save**" + (" (Draft), then **Submit** to post it. To change after submit: Cancel → Amend." if meta.is_submittable else "."))
		if nxt:
			how.append(f"4. Next steps from the submitted document: **Create →** {', '.join(nxt)}.")
	parts.append("\n".join(how))

	# Workflow
	wf = idx.workflows.get(doctype)
	if wf:
		states = [s.state for s in wf.states]
		trans = [f"- {t.state} → **{t.action}** → {t.next_state} _(role: {t.allowed})_" for t in wf.transitions]
		data["workflow"] = {"name": wf.name, "states": states}
		parts.append(f"## Approval workflow: {wf.name}\nStates: {' → '.join(states)}\n" + "\n".join(trans[:20]))

	# Linkage
	links = [df for df in meta.fields if df.fieldtype == "Link" and df.options and not df.hidden]
	used_in = sorted(idx.used_in.get(doctype, set()))
	data["uses"] = sorted({df.options for df in links})
	data["used_in"] = used_in[:40]
	link_part = ["## Linkage"]
	if links:
		link_part.append("**Uses these masters:** " + ", ".join(sorted({f"{df.options}" for df in links})[:30]))
	if used_in:
		link_part.append("**Used in / linked from:** " + ", ".join(used_in[:30]) + (" …" if len(used_in) > 30 else ""))
	try:
		dash = meta.get_dashboard_data()
		groups = [f"{g.get('label')}: {', '.join(g.get('items', []))}" for g in (dash.get("transactions") or []) if g.get("items")]
		if groups:
			data["connections"] = groups
			link_part.append("**Connections tab shows:**\n" + "\n".join(f"- {g}" for g in groups))
	except Exception:
		pass
	if len(link_part) > 1:
		parts.append("\n\n".join(link_part))

	# Reports
	reports = idx.reports.get(doctype, [])
	data["reports"] = [[r.name, r.report_type, r.is_standard] for r in reports]
	if reports or not meta.issingle:
		rep = ["## Reports", f"- List / Report view: [/app/{slug(doctype)}/view/report](/app/{slug(doctype)}/view/report) (choose columns, filter, export)"] if not meta.issingle else ["## Reports"]
		for r in reports[:25]:
			url = f"/app/query-report/{r.name}" if r.report_type in ("Script Report", "Query Report") else f"/app/{slug(doctype)}/view/report/{r.name}"
			rep.append(f"- [{r.name}]({url}) _({r.report_type}{', custom' if r.is_standard == 'No' else ''})_")
		parts.append("\n".join(rep))

	# Fields grouped by tab/section
	fields_md, tab, section, fdata = ["## Fields"], None, None, []
	for df in meta.fields:
		if df.fieldtype == "Tab Break":
			tab = df.label
			continue
		if df.fieldtype == "Section Break":
			section = df.label
			continue
		if df.fieldtype in LAYOUT or not df.label or (df.hidden and df.fieldname not in custom_fieldnames):
			continue
		head = " / ".join(x for x in (tab, section) if x)
		if head and (not fields_md or fields_md[-1] != f"**{head}**") and not any(l == f"**{head}**" for l in fields_md[-30:]):
			fields_md.append(f"**{head}**")
		is_custom = df.fieldname in custom_fieldnames
		fields_md.append(f"- **{df.label}** (`{df.fieldname}`){' 🛠' if is_custom else ''}: {field_text(df)}")
		fdata.append([df.label, df.fieldname, df.fieldtype, int(df.reqd or 0), int(is_custom)])
	data["fields"] = fdata
	parts.append("\n".join(fields_md[:400]))

	# Customizations
	cust = ["## Customizations on this screen"]
	cfs = idx.custom_fields.get(doctype, [])
	if cfs:
		cust.append("**Custom fields:** " + ", ".join(f"{c.label or c.fieldname} ({c.fieldtype})" for c in cfs[:40]))
	props = [p for p in idx.props.get(doctype, []) if p.property not in ("idx", "field_order", "options") or p.field_name]
	if props:
		cust.append("**Changed properties:** " + "; ".join(f"{p.field_name or 'form'}.{p.property} = {str(p.value)[:30]}" for p in props[:25]))
	cs = idx.client_scripts.get(doctype, [])
	if cs:
		cust.append("**Client scripts (form behaviour):** " + ", ".join(f"{c.name}{'' if c.enabled else ' (disabled)'}" for c in cs))
	ss = idx.server_scripts.get(doctype, [])
	if ss:
		cust.append("**Server scripts (automatic actions):** " + ", ".join(f"{s.name} on *{s.doctype_event or s.script_type}*{' (disabled)' if s.disabled else ''}" for s in ss))
	ns = idx.notifications.get(doctype, [])
	if ns:
		cust.append("**Notifications:** " + ", ".join(f"{n.name} ({n.event}){'' if n.enabled else ' (disabled)'}" for n in ns))
	data["customizations"] = {"fields": len(cfs), "properties": len(props), "client_scripts": len(cs), "server_scripts": len(ss), "notifications": len(ns)}
	if len(cust) > 1:
		parts.append("\n\n".join(cust))

	# Permissions
	roles = []
	for p in meta.permissions:
		if p.permlevel == 0 and p.read:
			rights = [r for r in ("create", "write", "submit", "cancel") if p.get(r)]
			roles.append(f"{p.role}" + (f" ({', '.join(rights)})" if rights else " (read)"))
	if roles:
		parts.append("## Who can use it\n" + ", ".join(sorted(set(roles))[:20]))

	is_custom = bool(meta.custom or cfs or props or cs or ss)
	keywords = " ".join([doctype, meta.module, *data["uses"][:10], *[r.name for r in reports[:10]]])
	return {
		"title": f"{doctype}: user manual",
		"content": "\n\n".join(parts),
		"data": data,
		"module": meta.module,
		"is_custom": is_custom,
		"keywords": keywords,
	}


def save_article(doctype, art):
	key = f"doctype:{doctype}"
	values = {
		"title": art["title"], "article_type": "DocType Manual", "source": "Auto", "ref_doctype": doctype,
		"module": art["module"], "is_custom": int(art["is_custom"]), "keywords": art["keywords"],
		"content": art["content"], "data": json.dumps(art["data"], default=str), "last_built": now_datetime(),
	}
	if frappe.db.exists("ERP Help Article", key):
		doc = frappe.get_doc("ERP Help Article", key)
		if doc.source == "Manual":
			return  # someone took this article over by hand; keep their version
		doc.update(values)
	else:
		doc = frappe.get_doc({"doctype": "ERP Help Article", "article_key": key, **values})
	doc.flags.from_manual_builder = True
	doc.flags.ignore_permissions = True
	doc.save() if not doc.is_new() else doc.insert()


# ------------------------------------------------------------------ entry points
def rebuild_all():
	idx = SiteIndex()
	doctypes = frappe.get_all("DocType", filters={"istable": 0}, fields=["name", "module", "custom"])
	built, failed, keep = 0, [], set()
	for dt in doctypes:
		if not wanted(dt, idx):
			continue
		try:
			save_article(dt.name, build_article(dt.name, idx))
			keep.add(f"doctype:{dt.name}")
			built += 1
			if built % 50 == 0:
				frappe.db.commit()
		except Exception as e:
			failed.append(f"{dt.name}: {str(e)[:80]}")
	# remove manuals of screens that no longer exist
	for name in frappe.get_all("ERP Help Article", filters={"article_type": "DocType Manual", "source": "Auto"}, pluck="name"):
		if name not in keep:
			frappe.delete_doc("ERP Help Article", name, ignore_permissions=True, force=True)
	frappe.db.commit()
	frappe.cache.delete_value("eaa_help_articles")
	frappe.cache.delete_value("eaa_help_field_index")
	if failed:
		frappe.log_error(title="ERP Help manual: some screens failed", message="\n".join(failed))
	return {"built": built, "failed": len(failed)}


def rebuild_one(doctype):
	if not doctype or not frappe.db.exists("DocType", doctype):
		return
	meta = frappe.get_meta(doctype)
	target = doctype
	if meta.istable:  # a child table changed: rebuild the screens that contain it
		parents = frappe.get_all("DocField", filters={"options": doctype, "fieldtype": ["in", ["Table", "Table MultiSelect"]]}, pluck="parent")
		for p in set(parents):
			rebuild_one(p)
		return
	idx = SiteIndex()
	if wanted(frappe._dict(name=target, module=meta.module, custom=meta.custom), idx):
		save_article(target, build_article(target, idx))
		frappe.db.commit()
		frappe.cache.delete_value("eaa_help_articles")
		frappe.cache.delete_value("eaa_help_field_index")


def on_meta_change(doc, method=None):
	"""doc_events hook: refresh the manual for the screen that was customized."""
	attr = WATCHED.get(doc.doctype)
	target = doc.get(attr) if attr else None
	if not target or frappe.flags.in_install or frappe.flags.in_migrate:
		return
	frappe.enqueue(
		"erp_ai_assistant.manual.rebuild_one", doctype=target, queue="short",
		job_id=f"eaa_manual::{target}", deduplicate=True, enqueue_after_commit=True,
	)


def schedule_full_rebuild():
	frappe.enqueue("erp_ai_assistant.manual.rebuild_all", queue="long", timeout=3600,
				   job_id="eaa_manual::all", deduplicate=True, enqueue_after_commit=True)
