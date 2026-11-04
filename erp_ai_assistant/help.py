"""Help Guide: instant answers about this ERP without any AI or internet.

Sources:
- the knowledge base (kb.py): process guides, troubleshooting (error -> cause -> fix), concepts, field notes, report hints
- the self-updating user manual (ERP Help Article): one article per screen, including customizations
- live metadata: fields, child tables, links, reports, settings, menu paths
- live data for quick lookups: stock of an item or warehouse, a document by its number, global search

answer(question) returns {"text": markdown, "suggestions": [...], "is_fallback": bool}."""

import difflib
import json
import math
import os
import re
from collections import Counter
from urllib.parse import quote

import frappe

from erp_ai_assistant.kb import (
	CONCEPTS,
	DT_FIELD_NOTES,
	FIELD_NOTES,
	GUIDES,
	PHRASE_ALIASES,
	PROBLEMS,
	REPORT_DESCRIPTIONS,
	REPORT_HINTS,
)
from erp_ai_assistant.tools import MAPPERS, doc_url, resolve_name

# ------------------------------------------------------------------ vocabulary
SYNONYMS = {
	"kaise": "how", "kese": "how", "kaisa": "how", "kaisey": "how",
	"kahan": "where", "kaha": "where", "kidhar": "where", "milega": "where", "milta": "where", "dikhega": "where", "dikhta": "where",
	"kya": "what", "kyaa": "what", "kaun": "which", "kaunsa": "which", "konsa": "which", "kon": "which", "kis": "which",
	"kaunsi": "which", "konsi": "which", "kisse": "which",
	"kyu": "why", "kyun": "why", "kyon": "why",
	"matlab": "meaning", "mtlb": "meaning", "arth": "meaning", "batao": "tell", "samjhao": "explain", "sikhao": "explain",
	"banana": "create", "banaye": "create", "banao": "create", "bnana": "create", "banate": "create", "banau": "create",
	"bnaye": "create", "banta": "create", "banti": "create", "banega": "create", "banaen": "create",
	"karna": "do", "kare": "do", "karein": "do", "karu": "do", "karun": "do", "karte": "do",
	"dikhao": "show", "dekhna": "show", "dekhe": "show", "dekhu": "show",
	"nahi": "not", "nhi": "not", "nahin": "not",
	"chutti": "leave", "chhutti": "leave", "chuttiyan": "leave", "kharid": "purchase", "kharidi": "purchase",
	"becho": "sales", "bikri": "sales", "galti": "error", "dikkat": "problem", "pareshani": "problem", "samasya": "problem",
	"hisab": "ledger", "khata": "account", "bhugtan": "payment", "godown": "warehouse", "allot": "allocate",
	"galat": "wrong", "galt": "wrong", "thik": "fix", "theek": "fix", "sahi": "correct", "badlu": "change", "badalna": "change",
	"hota": "is", "hoti": "is", "use": "use", "kab": "when", "kyon": "why"
}
ALIASES = {
	"po": "Purchase Order", "so": "Sales Order", "pr": "Purchase Receipt", "grn": "Purchase Receipt",
	"pi": "Purchase Invoice", "dn": "Delivery Note", "challan": "Delivery Note", "si": "Sales Invoice",
	"je": "Journal Entry", "jv": "Journal Entry", "pe": "Payment Entry", "mr": "Material Request",
	"se": "Stock Entry", "rfq": "Request for Quotation", "sq": "Supplier Quotation", "bom": "BOM",
	"quotation": "Quotation", "invoice": "Sales Invoice", "bill": "Purchase Invoice", "leave": "Leave Application",
	"item": "Item", "customer": "Customer", "supplier": "Supplier", "employee": "Employee", "warehouse": "Warehouse",
	"sle": "Stock Ledger Entry", "gle": "GL Entry", "bin": "Bin", "pos": "POS Invoice", "lead": "Lead",
	"opportunity": "Opportunity", "asset": "Asset", "timesheet": "Timesheet", "project": "Project",
}
STOP = set(
	"a an the is are was were be of for to in on at by with from as me mein mai main ka ki ke ko se hai hain ho h and or aur "
	"what how where which why who tell show explain do does did can could should would i we you my our your this that it its "
	"please plz pls bhai yaar sir hi hello want need know about any some get getting using use there here when then than also just "
	"not meaning".split()
)
GENERIC_DOCTYPES = {
	"Report", "Workflow", "Comment", "Note", "Event", "File", "Page", "Communication", "Activity Log", "Version", "Tag",
	"Process", "Flow", "Setting", "Error Log", "Access Log", "Data", "Number Card", "List View Settings", "Module Def",
	"Custom Field", "Property Setter", "DocType", "DocField", "Role", "Contact", "Address", "Payment", "Unit",
	"Transaction Log", "Dashboard", "Industry Type", "Designation", "Branch", "Department", "Holiday", "Status",
}
GENERIC_NOISE = {"process", "flow", "steps", "procedure", "cycle", "how", "tell", "explain", "create", "make", "new", "entry", "document", "erpnext", "erp", "system"}
TXN_DOCTYPES = [
	"Purchase Order", "Purchase Receipt", "Purchase Invoice", "Sales Order", "Delivery Note", "Sales Invoice",
	"Quotation", "Supplier Quotation", "Material Request", "Stock Entry", "Stock Reconciliation", "Payment Entry",
	"Journal Entry", "Leave Application", "Leave Allocation", "Employee", "Item", "Customer", "Supplier", "Leave Type",
]
FIELDTYPE_TEXT = {
	"Data": "a text field", "Small Text": "a text box", "Text": "a text box", "Long Text": "a text box",
	"Text Editor": "a formatted text box", "Markdown Editor": "a formatted text box", "Int": "a whole number",
	"Float": "a number", "Currency": "an amount", "Percent": "a percentage", "Date": "a date", "Datetime": "a date and time",
	"Time": "a time", "Check": "a tick box (Yes/No)", "Attach": "a file attachment", "Attach Image": "an image",
	"Duration": "a duration", "Rating": "a rating", "Phone": "a phone number", "Password": "a hidden secret",
	"Read Only": "a display-only value", "Autocomplete": "a text field with suggestions", "Code": "code", "JSON": "structured data",
}
LAYOUT = ("Section Break", "Column Break", "Tab Break", "HTML", "Button", "Fold", "Heading", "Image")
LEDGER_IMPACT = {
	"Purchase Receipt": ["Stock Ledger Entry", "GL Entry"], "Delivery Note": ["Stock Ledger Entry", "GL Entry"],
	"Stock Entry": ["Stock Ledger Entry", "GL Entry"], "Stock Reconciliation": ["Stock Ledger Entry", "GL Entry"],
	"Sales Invoice": ["GL Entry", "Payment Ledger Entry", "Stock Ledger Entry (only when Update Stock is ticked)"],
	"Purchase Invoice": ["GL Entry", "Payment Ledger Entry", "Stock Ledger Entry (only when Update Stock is ticked)"],
	"Payment Entry": ["GL Entry", "Payment Ledger Entry"], "Journal Entry": ["GL Entry", "Payment Ledger Entry (for party rows)"],
	"Leave Application": ["Leave Ledger Entry"], "Leave Allocation": ["Leave Ledger Entry"], "Asset": ["GL Entry (depreciation and disposal)"],
	"Sales Order": ["no ledger (it only plans and reserves)"], "Purchase Order": ["no ledger (it only plans)"],
}
APP_MODULES = {"india compliance": ("GST India", "Income Tax India", "Audit Trail"), "gst": ("GST India",), "hrms": ("HR", "Payroll"), "hr": ("HR", "Payroll")}

FIELD_WORDS = ("field", "fields", "meaning", "mean", "means", "what is", "what does", "purpose of", "use of", "used for", "column", "columns", "checkbox", "tick")
WHERE_WORDS = ("where", "find", "open", "location", "located", "menu", "locate", "navigate", "get to", "go to")
HOW_WORDS = ("how", "create", "make", "process", "steps", "flow", "procedure", "setup", "set up", "configure", "record", "enter")
TROUBLE_WORDS = (
	"error", "errors", "issue", "issues", "problem", "problems", "not working", "not", "cannot", "can't", "cant", "unable", "failed",
	"fails", "failing", "fail", "why", "wrong", "stuck", "missing", "mismatch", "exceeded", "exceeds", "not allowed", "invalid",
	"not found", "frozen", "insufficient", "throws", "throwing", "message", "fix", "solve", "resolve", "blocked", "denied", "won't", "wont",
	"aa raha", "ho raha", "crossed", "already exists", "mandatory", "not set",
)
DATA_WORDS = (
	"table name", "which table", "which tables", "what tables", "database table", "tables involved", "tables behind", "tables and fields", "schema", "data structure", "structure", "database", "db", "stored", "store", "stores", "storage",
	"child table", "child tables", "child doctype", "doctype name", "fieldname", "fieldnames", "primary key", "sql", "data model", "relationship", "relationships", "backend", "saved",
)
MECHANISM_RE = re.compile(r"\b(?:how|where|which)\s+(?:is|are|does|do(?!\s+(?:i|we|you)\b)|fields?|tables?)\b.*\b(?:stored|store|saved|save|calculated|kept|recorded|maintained|updated|linked|link|connected|hold|involved)\b")
CONCEPT_WORDS = ("what is", "what are", "explain", "difference between", "difference", "how does", "concept", "understand", "works", "vs", "versus")
REPORT_WORDS = ("report", "reports", "analysis", "ageing", "aging", "trial balance", "balance sheet", "statement")
COMPARE_WORDS = ("difference between", "difference", "vs", "versus", "compare", "in what order", "which order", "which comes first", "comes first", "sequence")
CUSTOM_WORDS = ("custom","customization", "customisation", "customized", "customised", "customizations", "script", "scripts")
LINK_WORDS = ("linkage", "linked", "link", "links", "connection", "connections", "connected", "relation", "related", "comes after", "comes before", "created from", "followed by", "next document")
WORKFLOW_WORDS = ("workflow", "approval", "approve", "approver", "states")
SETTINGS_WORDS = ("setting", "settings", "configuration", "config", "configure", "enable", "disable", "allow", "turn on", "turn off", "default", "prevent", "restrict", "stop users", "where can i set", "where to set", "where do i set", "how do i set", "how to set", "allowance", "threshold")

ACTION_PATTERNS = [
	r"^\s*(?:please\s+)?(?:create|make|generate|raise|issue|receive|deliver|transfer|submit|post|pay|book|apply|amend|sell|buy|draft|record|move)\b",
	r"\b(?:create|make|generate|raise|transfer|submit|deliver|receive)\s+(?:a|an|the|\d+)\b",
	r"\b(?:bana\s*(?:do|de|diya)|banao|kardo|kar\s*do|order\s*karo|entry\s*karo|bhej\s*(?:do|de)|bhejo|daal\s*do|becho|bech\s*do|kharido|kharid\s*lo|transfer\s*karo)\b",
]
QUESTION_PATTERNS = [
	r"\b(?:how|what|where|why|who|which|when|whats|wheres|whether|can i|is it|is there|should)\b",
	r"\b(?:kaise|kese|kaisa|kahan|kaha|kidhar|kya|kyun|kyu|kaun|kaunsa|konsa|kis|kisse|kisko|konsi|kaunsi)\b",
	r"\b(?:meaning|matlab|mtlb|explain|samjhao|batao|sikhao|guide|process|procedure|steps|flow|error|issue|problem|report)\b",
	r"\b(?:field|fields|column|screen|menu|difference|table|schema|linked)\b",
	r"\bstock\s+(?:of|for|ka|ki)\b",
]
TROUBLE_RE = re.compile(r"\b(?:not|cannot|can't|cant|won't|wont|unable|fail(?:s|ed|ing)?|error|mandatory|required|missing|crossed|exceeded|already exists|invalid|frozen|insufficient|stuck)\b")


IMPERATIVE_START = re.compile(
	r"^\s*(?:please\s+)?(?:create|make|generate|raise|issue|receive|deliver|transfer|submit|post|pay|book|apply|amend|sell|buy|draft|record|move|"
	r"add|set up|setup|schedule|send|assign|allocate|enter|cancel)\b")


def is_action_intent(query):
	"""True for imperative commands ("Create a PO for 5 pipes", "Add a custom field …", "Grant Plastics ko 10 bag becho")."""
	ql = (query or "").lower().strip()
	if "?" in ql or TROUBLE_RE.search(ql):
		return False
	if IMPERATIVE_START.search(ql) and not any(re.search(p, ql) for p in QUESTION_PATTERNS[:2]):
		return True  # a sentence that starts with a command verb is a command, even if it mentions "field" or "report"
	if any(re.search(p, ql) for p in QUESTION_PATTERNS):
		return False
	return any(re.search(p, ql) for p in ACTION_PATTERNS)


# ------------------------------------------------------------------ text helpers
def normalize(text):
	text = re.sub(r"\be[\s\-]?way[\s\-]?bills?\b", "e-waybill", (text or "").lower())
	text = re.sub(r"\be[\s\-]?invoic(e|es|ing)\b", r"e-invoic\1", text)
	toks = re.findall(r"[\w\-'&]+|\?", text)
	return " ".join(SYNONYMS.get(w, w) for w in toks)


def stem(w):
	for suf, rep in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")):
		if len(w) > len(suf) + 3 and w.endswith(suf):
			return w[: -len(suf)] + rep
	return w


def words(text):
	return [w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in STOP]


def stems(text):
	return [stem(w) for w in words(text)]


def slug(doctype):
	return frappe.scrub(doctype).replace("_", "-")


def has_any(q, keys):
	return any(re.search(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])", q) for k in keys)


def manual_url(doctype):
	return "/app/erp-help-article/" + quote(f"doctype:{doctype}", safe="")


def strip_html(text):
	return frappe.utils.strip_html(text or "").strip()


# ------------------------------------------------------------------ cached indexes
def doctype_names():
	names = frappe.cache.get_value("eaa_help_doctypes")
	if names is None:
		names = frappe.get_all("DocType", filters={"istable": 0}, pluck="name")
		frappe.cache.set_value("eaa_help_doctypes", names, expires_in_sec=3600)
	return names


def single_names():
	names = frappe.cache.get_value("eaa_help_singles")
	if names is None:
		names = frappe.get_all("DocType", filters={"issingle": 1}, pluck="name")
		frappe.cache.set_value("eaa_help_singles", names, expires_in_sec=3600)
	return names


def sidebar_index():
	"""{doctype: [["Buying", "Purchase Order"], ...]} from the v16 workspace sidebar files of installed apps."""
	index = frappe.cache.get_value("eaa_help_sidebar_v2")
	if index is not None:
		return index
	index = {}
	for app in frappe.get_installed_apps():
		folder = os.path.join(frappe.get_app_path(app), "workspace_sidebar")
		if not os.path.isdir(folder):
			continue
		for f in sorted(os.listdir(folder)):
			if not f.endswith(".json"):
				continue
			try:
				data = json.load(open(os.path.join(folder, f)))
			except Exception:
				continue
			section = None
			for it in data.get("items") or []:
				if it.get("type") == "Section Break":
					section = it.get("label")
				elif it.get("link_type", "DocType") == "DocType" and it.get("link_to"):
					path = [data.get("name") or f[:-5]]
					if section and it.get("child"):
						path.append(section)
					path.append(it.get("label") or it["link_to"])
					index.setdefault(it["link_to"], []).append(path)
	frappe.cache.set_value("eaa_help_sidebar_v2", index, expires_in_sec=3600)
	return index


def sidebar_path(doctype):
	paths = sidebar_index().get(doctype) or []
	if not paths:
		return None
	module = frappe.db.get_value("DocType", doctype, "module")
	return next((p for p in paths if p[0] == module), paths[0])


def child_names():
	names = frappe.cache.get_value("eaa_help_children")
	if names is None:
		names = frappe.get_all("DocType", filters={"istable": 1}, pluck="name")
		frappe.cache.set_value("eaa_help_children", names, expires_in_sec=3600)
	return names


def child_in(q):
	"""A child table named in the question ("Timesheet Detail", "Job Card Time Log"), longest first.
	Also "job card ka time log": the parent name and the rest of the child name both appear."""
	padded = " " + re.sub(r"[^a-z0-9]+", " ", q.lower()) + " "
	has = lambda t: f" {t} " in padded or f" {t}s " in padded
	best = None
	for name in child_names():
		n = name.lower()
		if len(n) > 6 and has(n) and (not best or len(n) > len(best)):
			best = name
	if best:
		return best
	for name in child_names():
		parts = name.lower().split()
		for i in range(1, len(parts) - 1):
			head, tail = " ".join(parts[:i]), " ".join(parts[i:])
			if len(head) >= 3 and len(tail) >= 6 and has(head) and has(tail) and (not best or len(name) > len(best)):
				best = name
	return best

def label_lookup():
	"""lowercase field label -> [(doctype, fieldname)] for every field and custom field (quoted field names)."""
	idx = frappe.cache.get_value("eaa_help_labels")
	if idx is None:
		idx = {}
		rows = frappe.db.sql(
			"""select parent, fieldname, label from `tabDocField` where ifnull(label,'')!='' and fieldtype not in
			('Section Break','Column Break','Tab Break','HTML','Button','Fold','Heading')
			union all select dt, fieldname, label from `tabCustom Field` where ifnull(label,'')!=''""")
		for parent, fieldname, label in rows:
			idx.setdefault(label.strip().lower(), []).append((parent, fieldname))
		frappe.cache.set_value("eaa_help_labels", idx, expires_in_sec=6 * 3600)
	return idx


QUOTE_RE = re.compile(r"(?<![A-Za-z])['\"“”‘’`]([^'\"“”‘’`]{3,90})['\"“”‘’`](?![A-Za-z])")  # the ' in "there's" is not a quote


def quoted_fields(raw, cand):
	"""Quoted text that is exactly a field label → [(meta, df)], preferring the screens named in the question."""
	idx = label_lookup()
	out, plain_quotes = [], []
	for text in QUOTE_RE.findall(raw or ""):
		key = text.strip().rstrip("?.").lower()
		hits = idx.get(key) or []
		if not hits:
			plain_quotes.append(text)
			continue
		related = set(cand)
		for c in cand:
			try:
				related.update(df.options for df in frappe.get_meta(c).fields if df.fieldtype in ("Table", "Table MultiSelect"))
			except Exception:
				pass
		ranked = sorted(hits, key=lambda h: (h[0] not in related, h[0] not in TXN_DOCTYPES))
		dt, fieldname = ranked[0]
		meta = frappe.get_meta(dt)
		df = meta.get_field(fieldname)
		if df and all(df.fieldname != o[1].fieldname or o[0].name != meta.name for o in out):
			out.append((meta, df))
	return out, plain_quotes


# Extra words added to a question so different wording reaches the same answer (the original words are kept)
EXPANSIONS = [
	(r"\block(?:s|ed)?\b.*\brate\b|\bsame rate\b|\brate .*(?:change|changing).*(?:po|purchase order).*invoice", "maintain same rate throughout the purchase cycle"),
	(r"\bcompulsory\b", "mandatory"),
	(r"\bsession time\b|\blogged out\b|\blog(?:s|ged)? out automatically\b|\bauto logout\b", "session expiry"),
	(r"\bprefix\b|\bnumbering\b|\binvoice numbers?\b|\bdocument numbers?\b", "naming series"),
	(r"\btds\b", "tax withholding category"),
	(r"\bbest sell\w*|\btop sell\w*|\bsell the most\b|\bmost sold\b", "item-wise sales history"),
	(r"\bpresent\b.*\babsent\b|\battendance grid\b", "monthly attendance sheet"),
	(r"\bvariants?\b", "item variant item attribute"),
	(r"\bconsum(?:ption|ed|es)\b.*\btransferred\b|\btransferred\b.*\bconsum", "backflush raw materials based on"),
	(r"\bauto(?:matic(?:ally)?)? email\b|\bemail\w* .*\bevery (?:day|week|monday|tuesday|wednesday|thursday|friday|month)\b", "auto email report"),
	(r"\bexport\b.*\bcustomi[sz]", "export customizations"),
	(r"\bquality inspection (?:parameters?|template|checks?)\b|\binspection parameters?\b", "quality inspection template"),
	(r"\bdepreciation schedule\b", "asset depreciation schedule"),
	(r"\bdepreciation\b.*\bnot\b.*\b(?:book|post)", "book asset depreciation entry automatically"),
	(r"\bbudget\b.*\b(?:block|stop|warn)\w*|\b(?:block|stop)\w*\b.*\bbudget\b", "action if annual budget exceeded"),
	(r"\bwip warehouse\b|\bwork in progress warehouse\b", "work in progress warehouse"),
	(r"\bbank reconciliation tool\b|\bmatch bank\b|\bbank statement\b", "bank reconciliation tool"),
	(r"\bdate format\b", "date format system settings"),
	(r"\btransfer\w*\b.*\bassets?\b|\bassets?\b.*\b(?:transfer\w*|move|moving|shift\w*)\b", "asset movement"),
]


def expand(q):
	extra = [add for pat, add in EXPANSIONS if re.search(pat, q) and add not in q]
	return q + (" " + " ".join(extra) if extra else "")


_KB_INDEX = {}


def kb_index():
	"""BM25-style index over guides, problems and concepts (built once per process)."""
	if _KB_INDEX:
		return _KB_INDEX
	docs = []
	for kind, entries in (("guide", GUIDES), ("problem", PROBLEMS), ("concept", CONCEPTS)):
		for e in entries:
			fields = {
				"title": Counter(stems(e.get("title", ""))),
				"tags": Counter(stems(e.get("tags", ""))),
				"dt": Counter(stems(" ".join(e.get("doctypes") or []))),
				"errors": Counter(stems(" ".join(e.get("errors") or []))),
				"body": Counter(stems((e.get("body") or "") + " " + (e.get("cause") or "") + " " + (e.get("solution") or ""))),
			}
			dts = {n.lower() for n in doctype_names()}
			errors = [x.lower().strip() for x in e.get("errors") or [] if (len(x.split()) >= 3 or len(x) >= 20) and x.lower().strip() not in dts]
			docs.append({"kind": kind, "entry": e, "fields": fields, "errors": errors})
	df = Counter()
	for d in docs:
		for t in set().union(*[set(c) for c in d["fields"].values()]):
			df[t] += 1
	n = max(1, len(docs))
	vocab = set(df) | {"where", "which", "what", "how", "report", "reports", "field", "fields", "setting", "settings", "table", "process"}
	for name in doctype_names():
		vocab.update(words(name))
	_KB_INDEX.update(docs=docs, idf={t: math.log(1 + n / (1 + c)) for t, c in df.items()}, vocab=vocab)
	return _KB_INDEX


WEIGHTS = {"title": 3.0, "tags": 2.0, "errors": 2.5, "dt": 1.5, "body": 0.35}


HINGLISH_KEEP = set("hote hota hoti hain karte karna karein karo banaya banega banta dikhega dikhta milega milta jata jati jaata hone wala wali sirf batao bhai chahiye raha rahi kaise kaisa kitna kitne pata lagta lagega dena dete".split())


def correct_typos(q):
	"""Fix misspelt words against the knowledge vocabulary ("purchse ordr" -> "purchase order")."""
	vocab = kb_index()["vocab"]
	out = []
	for w in q.split():
		if len(w) >= 4 and w.isalpha() and w not in vocab and stem(w) not in vocab and w not in STOP and w not in SYNONYMS.values():
			m = [x for x in difflib.get_close_matches(w, vocab, n=3, cutoff=0.8)
				 if x[0] == w[0] and abs(len(x) - len(w)) <= max(1, len(w) // 4)]  # typos keep the first letter and roughly the length
			out.append(m[0] if m and w not in HINGLISH_KEEP else w)
		else:
			out.append(w)
	return " ".join(out)


def kb_search(q, raw, kinds=None, doctype=None, limit=5, context=None):
	idx = kb_index()
	qs = [t for t in stems(q) if t not in GENERIC_NOISE]
	ctx = set(stems(" ".join(context))) if context else set()  # for problems: screen names are context, not the question
	raw_l = " ".join((raw or "").lower().split())
	scored = []
	for d in idx["docs"]:
		if kinds and d["kind"] not in kinds:
			continue
		s = 0.0
		for t in qs:
			idf = idx["idf"].get(t, 0) * (0.25 if t in ctx else 1.0)
			for f, w in WEIGHTS.items():
				c = d["fields"][f].get(t)
				if c:
					s += idf * w * (1 + math.log(c)) / (1 if f != "body" else 1.5)
		hit = max((len(e) for e in d["errors"] if e in raw_l), default=0)
		if hit:
			s += 45 + min(hit, 60) / 2  # an exact error text is the strongest evidence; longer = stronger
		dts_e = d["entry"].get("doctypes") or []
		if doctype and doctype in dts_e:
			s += 2.5
		elif doctype and d["kind"] == "problem" and dts_e and frappe.db.get_value("DocType", doctype, "is_submittable"):
			s -= 4  # a problem about other documents (e.g. invoices) is less likely when the question names a different document
		if s > 0:
			scored.append((s, d, bool(hit)))
	scored.sort(key=lambda x: -x[0])
	return scored[:limit]


# ------------------------------------------------------------------ screen detection
def doctype_matches(q):
	"""All screens named in the question as (position, name), using phrase aliases and DocType names."""
	found = {}
	for phrase, dt in PHRASE_ALIASES.items():
		m = re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", q)
		if m and frappe.db.exists("DocType", dt):
			found[dt] = (m.start(), len(phrase) + 100)
	for name in doctype_names():
		n = name.lower()
		if name in GENERIC_DOCTYPES or len(n) <= 3:
			continue
		m = re.search(rf"(?<![a-z0-9]){re.escape(n)}s?(?![a-z0-9])", q)
		if m and name not in found:
			found[name] = (m.start(), len(n))
	# drop names contained in a longer match at an overlapping position ("Warehouse" inside "Target Warehouse"-less cases kept)
	items = sorted(found.items(), key=lambda kv: (-kv[1][1], kv[1][0]))
	kept = []
	for name, (pos, ln) in items:
		if any(pos >= p and pos < p + (l if l < 100 else l - 100) for _, (p, l) in kept):
			continue
		kept.append((name, (pos, ln)))
	return kept


def find_doctype(q):
	"""The screen the question is about: the longest name (earliest on a tie), then short aliases, then typo-tolerant."""
	kept = doctype_matches(q)
	if kept:
		kept.sort(key=lambda kv: (-kv[1][1], kv[1][0]))
		return kept[0][0]
	for w in re.findall(r"[a-z]+", q):
		if w in ALIASES and frappe.db.exists("DocType", ALIASES[w]):
			return ALIASES[w]
	return fuzzy_doctype(q)


def all_doctypes(q):
	return [name for name, _ in sorted(doctype_matches(q), key=lambda kv: kv[1][0])]


def fuzzy_doctype(q):
	toks = [t for t in re.findall(r"[a-z]+", q) if t not in STOP]
	lower = {n.lower(): n for n in doctype_names() if n not in GENERIC_DOCTYPES}
	best, best_ratio = None, 0
	for size in (3, 2):
		for i in range(len(toks) - size + 1):
			gram = " ".join(toks[i : i + size])
			for m in difflib.get_close_matches(gram, lower, n=1, cutoff=0.82):
				r = difflib.SequenceMatcher(None, gram, m).ratio()
				if r > best_ratio:
					best, best_ratio = lower[m], r
		if best:
			return best
	return None


# ------------------------------------------------------------------ manual articles
def article(doctype):
	row = frappe.db.get_value("ERP Help Article", f"doctype:{doctype}", ["content", "data"], as_dict=True)
	if not row:
		return None
	try:
		row.data = json.loads(row.data or "{}")
	except ValueError:
		row.data = {}
	return row


def section(content, title):
	m = re.search(rf"^## {re.escape(title)}[^\n]*\n(.*?)(?=^## |\Z)", content or "", re.S | re.M)
	return m.group(1).strip() if m else ""


def sop_articles():
	rows = frappe.cache.get_value("eaa_help_articles")
	if rows is None:
		rows = frappe.get_all(
			"ERP Help Article",
			filters={"article_type": ["in", ["Company SOP", "Process Guide"]]},
			fields=["name", "title", "keywords", "content", "article_type"],
		)
		rows = [dict(r, words=set(stems(f"{r.title} {r.keywords or ''}")), body=set(stems(r.content or ""))) for r in rows]
		frappe.cache.set_value("eaa_help_articles", rows, expires_in_sec=3600)
	return rows


def best_sop(q):
	qw = set(stems(q)) - GENERIC_NOISE
	if not qw:
		return None
	best, best_score = None, 0
	for r in sop_articles():
		score = 3 * len(qw & r["words"]) + len(qw & r["body"]) / 2
		if score > best_score:
			best, best_score = r, score
	return best if best_score >= 4 else None


def field_index():
	idx = frappe.cache.get_value("eaa_help_field_index")
	if idx is None:
		idx = []
		for r in frappe.get_all("ERP Help Article", filters={"article_type": "DocType Manual"}, fields=["ref_doctype", "data"]):
			try:
				fields = json.loads(r.data or "{}").get("fields", [])
			except ValueError:
				continue
			for label, fieldname, _ft, _reqd, custom in fields:
				lw = tuple(stems(label))
				if lw:
					idx.append((r.ref_doctype, lw, fieldname, custom))
		frappe.cache.set_value("eaa_help_field_index", idx, expires_in_sec=6 * 3600)
	return idx


# ------------------------------------------------------------------ fields
def iter_fields(doctype):
	meta = frappe.get_meta(doctype)
	yield meta, meta, None
	for df in meta.fields:
		if df.fieldtype in ("Table", "Table MultiSelect"):
			yield meta, frappe.get_meta(df.options), df


def wmatch(w, qs):
	"""Same word, or the same word in another form (deliver / delivery, allocate / allocation)."""
	return w in qs or (len(w) >= 5 and any(len(x) >= 5 and x[:5] == w[:5] and abs(len(x) - len(w)) <= 4 for x in qs))


COMMON_LABEL_WORDS = {"stock", "item", "sale", "sales", "purchase", "up", "set", "default", "account", "rate", "qty", "amount", "date",
					  "name", "type", "no", "number", "status", "detail", "details", "total", "value", "order", "invoice", "entry", "allow"}


def label_score(lw, qs, qseq=None):
	"""How well a field label matches the question: full match, or most of a multi-word label.
	A partial match must include a distinctive word (not just "stock", "item", "up"…).
	Labels whose words appear next to each other in the question get a bonus."""
	hits = [w for w in lw if wmatch(w, qs)]
	hit = len(hits)
	if hit == len(lw):
		score = hit * 10
	elif len(lw) >= 3 and hit >= 2 and hit / len(lw) >= 0.6 and any(w not in COMMON_LABEL_WORDS and len(w) >= 4 for w in hits):
		score = hit * 6
	else:
		return 0
	if qseq and len(lw) >= 2:
		pairs = {(a[:5], b[:5]) for a, b in zip(qseq, qseq[1:])}
		score += 4 * sum(1 for a, b in zip(lw, lw[1:]) if (a[:5], b[:5]) in pairs)
	return score


def tech_names(raw):
	return set(re.findall(r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b", (raw or "").lower()))


def find_fields(q, raw, doctype=None, limit=2, candidates=None, keep_subsets=False):
	"""Best-matching fields. candidates = the screens to search (every screen named in the question)."""
	qs = set(stems(q))
	qseq = stems(q)
	techs = tech_names(raw)
	candidates = [c for c in (candidates or ([doctype] if doctype else TXN_DOCTYPES)) if c]
	scored = {}
	for dt in candidates:
		try:
			metas = list(iter_fields(dt))
		except Exception:
			continue
		for parent, m, table_df in metas:
			for df in m.fields:
				if df.fieldtype in LAYOUT or not df.label or df.hidden:
					continue
				lw = stems(df.label)
				by_name = df.fieldname in techs
				ls = label_score(lw, qs, qseq) if set(lw) <= qs else label_score(lw, qs - set(stems(dt)), qseq)
				if not lw or (not by_name and not ls):
					continue
				score = ls + (40 if by_name else 0) + (4 if m.name == doctype else 0) + (3 if df.fieldname in FIELD_NOTES else 0) - (2 if table_df else 0)
				if df.fieldtype in ("Table", "Table MultiSelect"):
					score -= 12  # a whole table ("Items", "Accounting Entries") is rarely what is asked
				if table_df and re.search(r"\b(?:row|rows|item|items|line|table|grid)\b", q):
					score += 5
				key = (m.name, df.fieldname)
				if score > scored.get(key, (0,))[0]:
					scored[key] = (score, m, df)
	best = sorted(scored.values(), key=lambda x: -x[0])
	out = []
	for s, m, df in best:
		if s <= 4:
			continue
		if not keep_subsets and any(set(stems(df.label)) < set(stems(o[1].label)) and o[0].name == m.name for o in out):
			continue
		if out and s < 0.5 * best[0][0]:
			break  # much weaker than the best match: not what was asked
		out.append((m, df))
		if len(out) >= limit:
			break
	return out


def find_field_anywhere(q, raw, singles_only=False):
	qs = set(stems(q))
	qseq = stems(q)
	techs = tech_names(raw)
	singles = set(single_names()) if singles_only else None
	best, best_score = None, 0
	for dt, lw, fieldname, custom in field_index():
		if singles is not None and dt not in singles:
			continue
		by_name = fieldname in techs
		ls = label_score(lw, qs, qseq)
		if singles_only and len(lw) < 2 and not by_name:
			continue  # a one-word setting ("Customer", "Shift") is never a confident match
		if by_name or ls:
			score = ls + (40 if by_name else 0) + (2 if dt in TXN_DOCTYPES else 0) + (2 if fieldname in FIELD_NOTES else 0) + (1 if custom else 0)
			if score > best_score:
				best, best_score = (dt, fieldname), score
	if not best:
		return None
	meta = frappe.get_meta(best[0])
	df = meta.get_field(best[1])
	return (meta, df) if df else None


def clean_cond(cond):
	return re.sub(r"\beval:\s*|doc\.", "", cond or "")[:150]


def field_explanation(df, meta, short=False):
	note = DT_FIELD_NOTES.get((meta.name, df.fieldname)) or FIELD_NOTES.get(df.fieldname)
	desc = strip_html(df.description)
	if note:
		return note
	if desc and len(desc.split()) >= 4:
		return desc
	if short:
		return desc or "—"  # in tables, an empty cell reads better than repeating the label
	label = df.label
	if df.fieldtype == "Check":
		return f"Tick this box to turn on **{label}** for this {meta.name}."
	if df.fieldtype == "Link":
		return f"The **{df.options}** this {meta.name} refers to."
	if df.fieldtype in ("Table", "Table MultiSelect"):
		return f"The list of **{df.options}** rows in this {meta.name}."
	return f"The {label.lower()} of this {meta.name}."


def parent_of(child):
	return frappe.db.get_value("DocField", {"options": child, "fieldtype": ["in", ["Table", "Table MultiSelect"]]}, "parent")


def explain_field(df, meta):
	where = f"on **{meta.name}**"
	parent = parent_of(meta.name) if meta.istable else None
	if parent:
		where = f"in the rows table of **{parent}** (*{meta.name}*)"
	lines = [f"## {df.label}", f"Field {where} · fieldname `{df.fieldname}`" + field_location(df, meta), field_explanation(df, meta)]
	desc = strip_html(df.description)
	if desc and desc != lines[-1] and len(desc.split()) >= 4:
		lines.append(f"**ERPNext note:** {desc.rstrip('.')}.")
	ft = df.fieldtype
	if ft == "Link":
		lines.append(f"**Type:** pick an existing **{df.options}** ([{df.options} list](/app/{slug(df.options)})).")
	elif ft == "Dynamic Link":
		other = meta.get_field(df.options)
		lines.append(f"**Type:** a record whose type is chosen in **{other.label if other else df.options}**.")
	elif ft == "Select":
		opts = [o for o in (df.options or "").split("\n") if o]
		lines.append("**Type:** choose one of " + ", ".join(f"*{o}*" for o in opts[:15]) + ".")
	elif ft in ("Table", "Table MultiSelect"):
		child = frappe.get_meta(df.options)
		cols = [c.label for c in child.fields if c.in_list_view and c.label][:8]
		lines.append("**Type:** a table of rows" + (f" with the columns {', '.join(cols)}" if cols else "") + ".")
	else:
		lines.append(f"**Type:** {FIELDTYPE_TEXT.get(ft, ft)}.")
	flags = []
	if df.reqd:
		flags.append("- **Mandatory:** the document cannot be saved without it.")
	if df.mandatory_depends_on:
		flags.append(f"- **Mandatory when:** `{clean_cond(df.mandatory_depends_on)}`")
	if df.fetch_from:
		src, _, fld = df.fetch_from.partition(".")
		sdf = meta.get_field(src)
		flags.append(f"- **Filled automatically** from the selected **{sdf.label if sdf else src}** ({fld.replace('_', ' ')}).")
	elif df.read_only:
		flags.append("- **Calculated by the system:** you do not type it.")
	if df.depends_on:
		flags.append(f"- **Shown only when:** `{clean_cond(df.depends_on)}`")
	if df.default:
		dv = str(df.default)
		dv = f"your default {dv[1:]}" if dv.startswith(":") else ("today's date" if dv.lower() == "today" else dv)
		flags.append(f"- **Default:** {dv}")
	if df.allow_on_submit:
		flags.append("- **Editable after submit.**")
	if flags:
		lines.append("\n".join(flags))
	page = parent or meta.name
	if frappe.get_meta(page).issingle:
		lines.append(f"**Where to change it:** open [{page}](/app/{slug(page)}), find **{df.label}**, change it and **Save**.")
	lines.append(f"[Full manual for {page}]({manual_url(page)})")
	return "\n\n".join(lines)


def field_location(df, meta):
	tab = section = None
	for f in meta.fields:
		if f.fieldtype == "Tab Break":
			tab, section = f.label, None
		elif f.fieldtype == "Section Break":
			section = f.label
		elif f.fieldname == df.fieldname:
			break
	where = " → ".join(x for x in (tab, section) if x)
	return f" · on the form under **{where}**" if where else ""


def compare_fields(pairs, title=None):
	parts = [f"## {pairs[0][1].label} vs {pairs[1][1].label}" if title is None else title]
	for meta, df in pairs:
		opts = [o for o in (df.options or "").split("\n") if o] if df.fieldtype == "Select" else []
		extra = (" **Options:** " + ", ".join(f"*{o}*" for o in opts[:12]) + ".") if opts else ""
		parts.append(f"**{df.label}** (`{df.fieldname}` on {meta.name}{field_location(df, meta)}): {field_explanation(df, meta)}{extra}")
	return "\n\n".join(parts)


def explain_fields(pairs):
	"""Several fields asked together ("Received Qty and Billed Amt", "default company and currency").
	The same field on several screens (GST Category on Customer and Supplier) is explained once."""
	uniq, seen = [], {}
	for meta, df in pairs:
		if df.label in seen:
			seen[df.label].append(meta.name)
			continue
		seen[df.label] = [meta.name]
		uniq.append((meta, df))
	if len(uniq) == 1:
		text = explain_field(uniq[0][1], uniq[0][0])
		others = seen[uniq[0][1].label][1:]
		return text + (f"\n\nThe same field exists on {', '.join(others)} with the same meaning." if others else "")
	return compare_fields(uniq, title="## " + " and ".join(df.label for _, df in uniq))


# ------------------------------------------------------------------ answer builders
def where_text(doctype):
	path = sidebar_path(doctype)
	meta = frappe.get_meta(doctype)
	if path:
		menu = f"open the **{path[0]}** workspace in the sidebar → " + " → ".join(f"**{p}**" for p in path[1:])
	else:
		menu = f"the **{meta.module}** module"
	app = frappe.db.get_value("Module Def", meta.module, "app_name") or ""
	app_label = {"erpnext": "ERPNext", "hrms": "Frappe HR", "india_compliance": "India Compliance", "frappe": "Frappe"}.get(app, app)
	lines = [
		f"- **Module:** {meta.module}" + (f" (app: {app_label})" if app_label else ""),
		f"- **Menu:** {menu}",
		f"- **Search bar (awesome bar):** press **Ctrl+G** and type *{doctype}*",
		f"- **Direct link:** [/app/{slug(doctype)}](/app/{slug(doctype)})" + ("" if meta.issingle else f" · [New {doctype}](/app/{slug(doctype)}/new)"),
	]
	if meta.is_tree:
		lines.append(f"- **Tree view:** [/app/{slug(doctype)}/view/tree](/app/{slug(doctype)}/view/tree)")
	return "\n".join(lines)


def schema_answer(doctype, q=""):
	meta = frappe.get_meta(doctype)
	kind = "Settings (single record)" if meta.issingle else "Child table" if meta.istable else "Transaction (submittable)" if meta.is_submittable else "Master / record"
	table = "tabSingles (one row per field)" if meta.issingle else f"tab{doctype}"
	naming = meta.autoname or "random hash"
	if naming.startswith("naming_series:"):
		naming = "naming series, e.g. " + ((meta.get_field("naming_series").options if meta.get_field("naming_series") else "") or "").split("\n")[0]
	elif naming.startswith("field:"):
		naming = f"the value of the **{naming[6:]}** field"
	parts = [
		f"## Data structure of {doctype}",
		f"- **Type:** {kind} · **Module:** {meta.module}",
		f"- **Database table:** `{table}`",
		f"- **Primary key:** `name` (set by {naming})",
		"- **Standard columns:** `name`, `owner`, `creation`, `modified`, `modified_by`, `docstatus` (0 Draft, 1 Submitted, 2 Cancelled), `idx`"
		+ (", plus `parent`, `parenttype`, `parentfield` linking each row to its parent" if meta.istable else ""),
	]
	fields = [df for df in meta.fields if df.fieldtype not in LAYOUT and df.fieldtype not in ("Table", "Table MultiSelect")]
	qs0 = set(stems(q))
	asked_f = [d for d in fields if d.label and any(wmatch(w, qs0) for w in stems(d.label + " " + d.fieldname.replace("_", " "))) and not set(stems(d.label)) <= set(stems(doctype))]
	key = (asked_f + sorted([d for d in fields if d not in asked_f], key=lambda d: (not d.reqd, d.fieldtype != "Link", not d.in_list_view, d.fieldname not in FIELD_NOTES, d.idx)))[:30]
	key.sort(key=lambda d: d.idx)
	rows = ["| Field | Fieldname | Type | Links to / Options |", "|---|---|---|---|"]
	for df in key:
		opt = df.options if df.fieldtype in ("Link", "Dynamic Link") else (df.options or "").replace("\n", ", ")[:40] if df.fieldtype == "Select" else ""
		rows.append(f"| {df.label or df.fieldname}{' *' if df.reqd else ''} | `{df.fieldname}` | {df.fieldtype} | {opt} |")
	parts.append(f"### Key fields ({len(key)} of {len(fields)}; * = mandatory)\n" + "\n".join(rows))
	tables = [df for df in meta.fields if df.fieldtype in ("Table", "Table MultiSelect")]
	if tables:
		lines = []
		for df in tables:
			child = frappe.get_meta(df.options)
			qs_ = set(stems(q))
			asked = [c for c in child.fields if c.fieldtype not in LAYOUT and c.label and any(wmatch(w, qs_) for w in stems(c.label + " " + c.fieldname.replace("_", " ")))]
			cols = [f"`{c.fieldname}`" for c in (asked + sorted(
				[c for c in child.fields if c.fieldtype not in LAYOUT and (c.in_list_view or c.reqd or c.fieldtype == "Link") and c not in asked],
				key=lambda c: (not c.reqd, not c.in_list_view, c.idx)))][:12]
			lines.append(f"- **{df.label}** → child DocType *{df.options}*, table `tab{df.options}`, joined by `parent` = {doctype}.name and `parentfield` = `{df.fieldname}`" + (f"; key columns {', '.join(cols)}" if cols else ""))
		parts.append("### Child tables\n" + "\n".join(lines))
	links = sorted({df.options for df in meta.fields if df.fieldtype == "Link" and df.options})
	if links:
		parts.append("### Links to other records\n" + ", ".join(links[:25]))
	impact = LEDGER_IMPACT.get(doctype)
	if impact:
		parts.append("### Ledger impact on submit\n" + "\n".join(f"- {x}" for x in impact))
	if not meta.issingle and not meta.istable:
		sel = ", ".join(["name"] + [df.fieldname for df in key[:4]])
		parts.append(f"### Example query\n`SELECT {sel} FROM \\`tab{doctype}\\` WHERE docstatus = 1`")
	if not meta.istable:
		parts.append(f"[Full manual for {doctype}]({manual_url(doctype)}) · [Report view](/app/{slug(doctype)}/view/report)")
	return "\n\n".join(parts)


def fields_listing(doctype):
	meta = frappe.get_meta(doctype)
	rows = ["| Field | Fieldname | Type | Meaning |", "|---|---|---|---|"]
	shown = 0
	for df in meta.fields:
		if df.fieldtype in LAYOUT or not df.label or df.hidden:
			continue
		rows.append(f"| {df.label}{' *' if df.reqd else ''} | `{df.fieldname}` | {df.fieldtype} | {field_explanation(df, meta, short=True)[:140]} |")
		shown += 1
		if shown >= 45:
			break
	return (f"## Fields of {doctype}\n(* = mandatory)\n\n" + "\n".join(rows)
			+ f"\n\nAsk *what is <field> in {doctype}* for details, or open the [full manual]({manual_url(doctype)}).")


def link_fields_between(a, b):
	"""Fields in screen A (and its child tables) that point to screen B or its rows."""
	b_words = set(stems(b))
	out = []
	for parent, m, table_df in iter_fields(a):
		for df in m.fields:
			if df.fieldtype in LAYOUT or not df.label:
				continue
			points = (df.fieldtype in ("Link", "Dynamic Link") and df.options in (b, f"{b} Item")) or (
				df.fieldtype in ("Data", "Link") and b_words <= set(stems(df.label + " " + df.fieldname.replace("_", " ")))
			)
			if points:
				where = f"{m.name} (rows)" if table_df else m.name
				out.append(f"- `{df.fieldname}` on **{where}**: {df.label}" + (f" → links to *{df.options}*" if df.fieldtype == "Link" else " (row reference)"))
	return out


def link_answer(names):
	"""How the first screen is linked to the others: table, link fields, and where to see connections."""
	a, others = names[0], names[1:3]
	meta = frappe.get_meta(a)
	parts = [f"## How {a} is linked to {' and '.join(others)}",
			 f"- **Table:** `tab{a}`" + (" (a custom DocType built for this company)" if meta.custom else "")]
	found = False
	for b in others:
		lines, src, dst = link_fields_between(a, b), a, b
		if not lines:
			lines, src, dst = link_fields_between(b, a), b, a
		if lines:
			found = True
			parts.append(f"**{src} → {dst}** (fields on {src} that point to {dst}):\n" + "\n".join(lines[:8]))
	if not found:
		return None
	parts.append("These are **Link** fields (fieldtype *Link*, whose *options* name the target DocType); row references such as `dn_detail` or `purchase_order_item` store the exact row they came from.")
	parts.append("When a document is made with **Create →** from another, these fields are filled automatically, and on submit the source document's progress (*% Received*, *% Billed*, *% Delivered*) is updated.")
	parts.append(f"**See it in the app:** open any {a} and use the **Connections** section (the dashboard at the top of the form) to list and open every linked record.")
	return "\n\n".join(parts)


def render_entry(kind, e):
	if kind == "problem":
		return f"## {e['title']}\n\n**Cause:** {e.get('cause', '').strip()}\n\n**How to fix:**\n\n{e.get('solution', '').strip()}"
	return f"## {e['title']}\n\n{(e.get('body') or '').strip()}"


def related_suggestions(hits, current):
	out = []
	for _, d, _ in hits:
		e = d["entry"]
		if e is not current and e["title"] not in out:
			out.append(e["title"])
		if len(out) >= 3:
			break
	return out


# ------------------------------------------------------------------ live data lookups
STOCK_Q = re.compile(r"\b(?:how much|how many|quantity of|qty of|stock of|stock for|units of|balance of|stock balance of|in stock|available stock|stock level|ka stock|ki stock|ke stock|stock kitna|kitna stock|stock in)\b")


def warehouse_in(raw_l):
	names = frappe.cache.get_value("eaa_help_warehouses")
	if names is None:
		names = frappe.get_all("Warehouse", filters={"is_group": 0}, pluck="name")
		frappe.cache.set_value("eaa_help_warehouses", names, expires_in_sec=3600)
	# the full name ("Finished Goods - Ssy") wins over a short-name match, so "- Ssy" never picks "- SsyD"
	exact = [n for n in names if re.search(rf"(?<![a-z0-9]){re.escape(n.lower())}(?![a-z0-9])", raw_l)]
	if exact:
		return max(exact, key=len)
	default_company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
	matches = [n for n in names if re.search(rf"\b{re.escape(re.sub(r'\s+-\s+\w+$', '', n).lower())}\b", raw_l)]
	if not matches:
		return None
	own = [n for n in matches if frappe.db.get_value("Warehouse", n, "company") == default_company]
	return (own or matches)[0]


def item_in(raw, q):
	for tok in re.findall(r"\b[A-Za-z0-9][A-Za-z0-9\-_.]{2,}\b", raw or ""):
		if any(c.isdigit() for c in tok) and frappe.db.exists("Item", tok):
			return tok
	m = re.search(r"\(([^)]+)\)", raw or "")
	if m and frappe.db.exists("Item", m.group(1).strip()):
		return m.group(1).strip()
	m = re.search(r"(?:stock|quantity|qty|units|balance)\s+(?:of|for)\s+(?:the\s+)?(?:item\s+)?(.+?)(?:\s+(?:in|at|do|is|are|we|me|mein)\b|\?|$)", q) or re.search(
		r"how (?:much|many)\s+(?:units of\s+|of\s+)?(?:the\s+)?(.+?)\s+(?:do|is|are|we|in|at)\b", q) or re.search(r"^(.+?)\s+(?:ka|ki|ke)\s+stock\b", q)
	if m:
		text = re.sub(r"^(?:item|the)\s+", "", m.group(1).strip())
		name = resolve_name("Item", text)
		if frappe.db.exists("Item", name):
			return name
	return None


def stock_answer(raw, q):
	raw_l = (raw or "").lower()
	wh = warehouse_in(raw_l)
	item = item_in(raw, q)
	if not item and not wh:
		return None
	if not item:
		rows = frappe.get_list("Bin", filters={"warehouse": wh, "actual_qty": ["!=", 0]}, fields=["item_code", "actual_qty", "projected_qty", "stock_value"], order_by="actual_qty desc", limit_page_length=50)
		if not rows:
			return f"## Stock in {wh}\nNo items have stock in **{wh}** right now (actual qty is 0 for every item).\n\n[Stock Balance](/app/query-report/Stock Balance?warehouse={quote(wh)})"
		lines = [f"## Stock in {wh}", "| Item Code | Actual Qty | Projected | Value |", "|---|---:|---:|---:|"]
		for r in rows:
			lines.append(f"| {r.item_code} | {r.actual_qty:g} | {r.projected_qty:g} | ₹{r.stock_value:,.0f} |")
		lines.append(f"\n[Stock Balance report for this warehouse](/app/query-report/Stock Balance?warehouse={quote(wh)})")
		return "\n".join(lines)
	filters = {"item_code": item}
	if wh:
		filters["warehouse"] = wh
	rows = frappe.get_list("Bin", filters=filters, fields=["warehouse", "actual_qty", "projected_qty", "reserved_qty", "stock_value"], order_by="actual_qty desc")
	name = frappe.db.get_value("Item", item, "item_name")
	if not rows or not any(r.actual_qty for r in rows):
		return (f"## Stock of {name} (`{item}`)\nThere is no stock of **{name}** (`{item}`)" + (f" in **{wh}**" if wh else "")
				+ f" right now (actual qty 0).\n\n[Stock Ledger](/app/query-report/Stock Ledger?item_code={quote(item)})")
	lines = [f"## Stock of {name} (`{item}`)", "| Warehouse | Actual Qty | Reserved | Projected | Value |", "|---|---:|---:|---:|---:|"]
	for r in rows:
		lines.append(f"| {r.warehouse} | {r.actual_qty:g} | {r.reserved_qty:g} | {r.projected_qty:g} | ₹{r.stock_value:,.0f} |")
	if len(rows) > 1:
		lines.append(f"\n**Total actual qty:** {sum(r.actual_qty for r in rows):g}")
	lines.append(f"\n[Stock Ledger](/app/query-report/Stock Ledger?item_code={quote(item)}) · [Stock Balance](/app/query-report/Stock Balance?item_code={quote(item)})")
	return "\n".join(lines)


DOCNAME_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,8}(?:-[A-Z0-9]{2,10})*-\d{3,6}(?:-\d{1,2})?)\b")
RECORD_DOCTYPES = TXN_DOCTYPES + ["Leave Policy Assignment", "Leave Policy", "POS Invoice", "Asset", "Work Order", "Delivery Note", "Stock Entry", "Material Request"]


def find_record(raw):
	for name in DOCNAME_RE.findall(raw or ""):
		for dt in RECORD_DOCTYPES:
			if frappe.db.exists(dt, name):
				return dt, name
	return None


def record_answer(dt, name):
	doc = frappe.get_doc(dt, name)
	if not doc.has_permission("read"):
		return None
	state = {0: "Draft", 1: "Submitted", 2: "Cancelled"}[doc.docstatus]
	bits = [f"## {dt} {name}", f"**State:** {state}" + (f" · **Status:** {doc.status}" if doc.get("status") else "")]
	for f in ("stock_entry_type", "purpose", "customer", "supplier", "employee_name", "leave_type", "company", "posting_date", "transaction_date",
			  "from_date", "to_date", "from_warehouse", "to_warehouse", "grand_total", "outstanding_amount", "per_received", "per_billed",
			  "per_delivered", "total_leave_days"):
		if doc.get(f) not in (None, "", 0):
			bits.append(f"- **{doc.meta.get_label(f)}:** {doc.get(f)}")
	if doc.get("items"):
		bits.append("- **Items:** " + ", ".join(f"{r.item_code} × {r.qty:g}" for r in doc.items[:6]))
		links = {}
		for r in doc.items:
			for f, label in (("sales_order", "Sales Order"), ("against_sales_order", "Sales Order"), ("delivery_note", "Delivery Note"),
							 ("purchase_order", "Purchase Order"), ("purchase_receipt", "Purchase Receipt"), ("material_request", "Material Request"),
							 ("against_sales_invoice", "Sales Invoice"), ("prevdoc_docname", "Quotation")):
				if r.get(f):
					links.setdefault(label, set()).add(r.get(f))
		if links:
			bits.append("- **Linked documents:** " + "; ".join(f"{k}: {', '.join(sorted(v))}" for k, v in links.items()))
	bits.append(f"\n[Open {name}]({doc_url(dt, name)}) · the **Connections** tab of the document lists every linked record.")
	return "\n".join(bits)


def search_answer(raw):
	try:
		from frappe.utils.global_search import search

		rows = search(raw, limit=8)
	except Exception:
		rows = []
	if not rows:
		return None
	lines = ["## Matching records"]
	for r in rows:
		lines.append(f"- [{r.get('doctype')} {r.get('name')}]({doc_url(r.get('doctype'), r.get('name'))}): {strip_html(r.get('content'))[:90]}")
	return "\n".join(lines)


# ------------------------------------------------------------------ reports / customizations / settings / overview
def report_rows():
	rows = frappe.cache.get_value("eaa_help_reports")
	if rows is None:
		rows = frappe.get_all("Report", filters={"disabled": 0}, fields=["name", "ref_doctype", "report_type", "is_standard", "module"])
		frappe.cache.set_value("eaa_help_reports", rows, expires_in_sec=3600)
	return rows


def report_url(r):
	if r["report_type"] in ("Script Report", "Query Report"):
		return f"/app/query-report/{quote(r['name'])}"
	return f"/app/{slug(r['ref_doctype'])}/view/report/{quote(r['name'])}"


def hinted_reports(q, raw):
	text = " ".join([q, (raw or "").lower()]).replace("-", " ") + " " + " ".join([q, (raw or "").lower()])
	out = []
	for name, phrases in REPORT_HINTS:
		if any(re.search(rf"(?<![a-z0-9]){re.escape(p)}(?![a-z0-9])", text) for p in phrases):
			out.append(name)
	return out


def reports_answer(q, raw, doctype):
	rows = {r["name"]: r for r in report_rows()}
	hint_names = hinted_reports(q, raw)
	tool = next((n for n in hint_names if n not in rows and frappe.db.exists("DocType", n)), None)
	if tool and (not any(n in rows for n in hint_names) or hint_names[0] == tool):
		# some "reports" are really tools/screens (e.g. Purchase Reconciliation Tool for GSTR-2B)
		return (f"## {tool}\n\n{REPORT_DESCRIPTIONS.get(tool, '')}\n\n" + where_text(tool)
				+ f"\n\n[Manual for {tool}]({manual_url(tool)})")
	hinted = [rows[n] for n in hint_names if n in rows]
	qw = set(stems(q)) - {"report", "show", "which", "list", "see", "check", "want", "open"}
	scored = []
	for r in rows.values():
		nw = set(stems(r["name"]))
		score = 3 * len(qw & nw) + (5 if doctype and r["ref_doctype"] == doctype else 0) + len(qw & set(stems(r["ref_doctype"] or "")))
		if " ".join(stems(r["name"])) in " ".join(stems(q)):
			score += 8
		if r in hinted:
			score += 12
		if score >= 3:
			scored.append((score, r))
	scored.sort(key=lambda x: -x[0])
	if not scored:
		return None
	top = scored[0][1]
	lines = [f"## {top['name']}" if hinted or scored[0][0] >= 11 else "## Reports" + (f" for {doctype}" if doctype else "")]
	module = frappe.db.get_value("Report", top["name"], "module") or "Accounts"
	ws = {"Accounts": "Accounting", "Stock": "Stock", "Selling": "Selling", "Buying": "Buying", "HR": "HR", "Payroll": "Payroll", "Assets": "Assets"}.get(module, module)
	if REPORT_DESCRIPTIONS.get(top["name"]):
		lines.append(f"**What it shows:** {REPORT_DESCRIPTIONS[top['name']]}")
	lines.append(f"**Where:** open **[{top['name']}]({report_url(top)})**, found in the **{ws}** workspace under **Reports** (or press **Ctrl+G** and type *{top['name']}*).")
	others = [r for _, r in scored[1:7]]
	if others:
		lines.append("**Related reports:**\n" + "\n".join(f"- [{r['name']}]({report_url(r)}) on *{r['ref_doctype']}*{' (custom)' if r['is_standard'] == 'No' else ''}" for r in others))
	lines.append("**Tip:** set the filters at the top (company, date range, party, item, warehouse) and use the **⋯ → Export** menu to download it to Excel.")
	if doctype and doctype != top.get("ref_doctype"):
		lines.append(f"You can also build your own view: [{doctype} report view](/app/{slug(doctype)}/view/report).")
	return "\n\n".join(lines)


def customizations_answer(doctype):
	if doctype:
		art = article(doctype)
		text = section(art.content, "Customizations") if art else ""
		if art and art.data.get("custom_doctype"):
			return custom_module_answer(doctype, "")
		if not text:
			return f"## {doctype}\n**{doctype}** has no company-specific customizations; it works as standard ERPNext.\n\n[Full manual for {doctype}]({manual_url(doctype)})"
		return f"## Customizations on {doctype}\n\n{text}\n\n[Full manual for {doctype}]({manual_url(doctype)})"
	rows = frappe.get_all("ERP Help Article", filters={"article_type": "DocType Manual", "is_custom": 1}, fields=["ref_doctype", "data"], limit=200)
	if not rows:
		return "## Customizations\nNo company-specific customizations were found. If you changed something just now, the manual refreshes within a minute."
	custom_screens, changed = [], []
	for r in rows:
		try:
			d = json.loads(r.data or "{}")
		except ValueError:
			d = {}
		c = d.get("customizations") or {}
		bits = [f"{v} {k.replace('_', ' ')}" for k, v in c.items() if v]
		line = f"- [{r.ref_doctype}]({manual_url(r.ref_doctype)})" + (f": {', '.join(bits)}" if bits else "")
		(custom_screens if d.get("custom_doctype") else changed).append(line)
	lines = ["## Customizations in this ERP"]
	if custom_screens:
		lines.append("**Custom screens (custom DocTypes) built for this company:**\n" + "\n".join(custom_screens))
	if changed:
		lines.append("**Standard screens changed for this company:**\n" + "\n".join(changed))
	counts = {dt: frappe.db.count(dt, filt) for dt, filt in (("Client Script", {"enabled": 1}), ("Server Script", {"disabled": 0}),
																 ("Custom Field", {"is_system_generated": 0}), ("Property Setter", {"is_system_generated": 0}),
																 ("Workflow", {"is_active": 1}), ("Notification", {"enabled": 1}))}
	lines.append("**Where to see every customization:**\n" + "\n".join(
		f"- [{dt} list](/app/{slug(dt)}): {n} active" for dt, n in counts.items()))
	lines.append("Ask *customizations in <screen>* for details, or open [all customized screens](/app/erp-help-article?is_custom=1).")
	return "\n\n".join(lines)


def custom_module_answer(doctype, q):
	"""How the custom screens of one module work together, ordered so masters come before the documents that use them."""
	module = frappe.db.get_value("DocType", doctype, "module")
	screens = frappe.get_all("DocType", filters={"module": module, "custom": 1, "istable": 0}, pluck="name") or [doctype]
	links = {s: {df.options for df in frappe.get_meta(s).fields if df.fieldtype == "Link" and df.options in screens and df.options != s} for s in screens}
	order, done = [], set()
	while len(order) < len(screens):
		ready = [s for s in screens if s not in done and links[s] <= done] or [s for s in screens if s not in done]
		ready.sort()
		order.append(ready[0])
		done.add(ready[0])
	parts = [f"## {module}: custom screens built for this company", f"These screens are not part of standard ERPNext. Use them in this order:"]
	for i, s in enumerate(order, 1):
		meta = frappe.get_meta(s)
		mand = [df.label for df in meta.fields if df.reqd and df.fieldtype not in LAYOUT and not df.read_only][:6]
		uses = sorted(links[s])
		used_by = sorted(o for o in screens if s in links[o])
		desc = strip_html(meta.description)
		line = f"{i}. **[{s}](/app/{slug(s)})**" + (f": {desc}" if desc else "")
		details = []
		if mand:
			details.append("fill " + ", ".join(f"**{m}**" for m in mand))
		if uses:
			details.append("uses " + ", ".join(uses))
		if used_by:
			details.append("is used by " + ", ".join(used_by))
		parts.append(line + ("; " if desc else " — ") + "; ".join(details) + "." if details else line)
	if any("Registration" in s for s in order) and any("Allocation" in s for s in order):
		parts.append("**Typical flow:** first record the request in the *Registration* screen; once it is approved, create the *Allocation* from it, which assigns the room.")
	parts.append(f"[Manual for {doctype}]({manual_url(doctype)}) · open each screen from the search bar (**Ctrl+G**).")
	return "\n\n".join(parts)


def compare_doctypes(names):
	parts = ["## " + " vs ".join(names)]
	for n in names:
		art = article(n)
		meta = frappe.get_meta(n)
		d = art.data if art else {}
		desc = strip_html(meta.description)
		key = [df for df in meta.fields if df.fieldtype not in LAYOUT and df.label and not df.hidden and (df.reqd or df.fieldtype in ("Link", "Date", "Select"))][:8]
		lines = [f"**{n}**" + (f": {desc}" if desc else "") + (" (custom screen)" if meta.custom else "")]
		if key:
			lines.append("- **Records:** " + ", ".join(df.label for df in key))
		links = sorted({df.options for df in meta.fields if df.fieldtype == "Link" and df.options in names})
		if links:
			lines.append(f"- **Refers to:** {', '.join(links)} (so the {', '.join(links)} must exist first)")
		if d.get("prev"):
			lines.append(f"- **Made from:** {', '.join(d['prev'])}")
		if d.get("next"):
			lines.append(f"- **Leads to:** {', '.join(d['next'])}")
		parts.append("\n".join(lines))
	order = sorted(names, key=lambda n: sum(1 for df in frappe.get_meta(n).fields if df.fieldtype == "Link" and df.options in names))
	if len(order) == 2 and order[0] != order[1]:
		parts.append(f"**Order of use:** create the **{order[0]}** first, then the **{order[1]}** (it refers to the {order[0]}).")
	return "\n\n".join(parts)


def manual_overview(doctype, q):
	art = article(doctype)
	if not art:
		return None
	c, d = art.content, art.data
	if d.get("custom_doctype") and has_any(q, HOW_WORDS + ("use", "used", "purpose", "what is")):
		return custom_module_answer(doctype, q), [f"Fields of {doctype}", f"Data structure of {doctype}"]
	head = c.split("\n## ", 1)[0].replace(f"# {doctype}", f"## {doctype}", 1)
	parts = [head, "### Where to find it\n" + where_text(doctype)]
	if has_any(q, WORKFLOW_WORDS):
		wf = section(c, "Approval workflow")
		parts.append("### Approval workflow\n" + (wf or (
			f"No approval Workflow is configured for {doctype}. It follows the normal Draft → Submit flow"
			+ (" and is approved by the **Leave Approver**, who sets **Status** to Approved or Rejected before submitting." if doctype == "Leave Application" else ".")
			+ " A System Manager can add one in [Workflow](/app/workflow/new).")))
	if has_any(q, LINK_WORDS):
		bits = []
		if d.get("prev"):
			bits.append(f"- **Created from:** {', '.join(d['prev'])} (open it → **Create → {doctype}**)")
		if d.get("next"):
			bits.append(f"- **Next documents:** {', '.join(d['next'])} (from the submitted {doctype}: **Create → …**)")
		bits.append(f"- **Connections tab:** open any {doctype} and use the **Connections** section (the dashboard at the top) to see and open every linked record.")
		parts.append("### Linkage and connections\n" + "\n".join(bits) + "\n\n" + (section(c, "Linkage") or ""))
	else:
		parts.append("### How to create and use it\n" + section(c, "How to create"))
		guide = next((g for g in GUIDES if (g.get("doctypes") or [None])[0] == doctype), None) or next((g for g in GUIDES if doctype in (g.get("doctypes") or [])), None)
		if guide and has_any(q, HOW_WORDS):
			parts.append(f"### {guide['title']}\n{guide['body']}")
		if d.get("prev") or d.get("next"):
			bits = []
			if d.get("prev"):
				bits.append("comes from " + ", ".join(d["prev"]))
			if d.get("next"):
				bits.append("leads to " + ", ".join(d["next"]))
			parts.append("**Flow:** " + "; ".join(bits))
	reps = section(c, "Reports").split("\n")
	if len(reps) > 1:
		parts.append("### Reports\n" + "\n".join(reps[:7]))
	if d.get("workflow") and not has_any(q, WORKFLOW_WORDS):
		parts.append(f"**Approval workflow:** {' → '.join(d['workflow']['states'])}")
	cust = section(c, "Customizations")
	if cust:
		parts.append("### Customized for this company\n" + cust)
	parts.append(f"[Full manual for {doctype}]({manual_url(doctype)}): every field, permissions and connections.")
	return "\n\n".join(p for p in parts if p.strip()), [f"Fields of {doctype}", f"Reports of {doctype}", f"Data structure of {doctype}"]


def settings_answer(q, raw, allow_partial=False):
	found = find_field_anywhere(q, raw, singles_only=True)
	if found:
		second = None
		if re.search(r"\band\b", q):
			# "increase the session time and change the date format": answer every setting asked
			rest_q = " ".join(w for w in q.split() if w not in set(words(found[1].label)))
			s2 = find_field_anywhere(rest_q, raw, singles_only=True)
			if s2 and s2[1].fieldname != found[1].fieldname:
				second = s2
		if second:
			return explain_fields([found, second]), [found[0].name]
		return explain_field(found[1], found[0]), [found[0].name]
	if allow_partial:
		return None
	if not has_any(q, ("setting", "settings", "configuration", "config")):
		return None  # without the word "settings", only a specific setting field is a confident answer
	qw = set(stems(q)) - {"setting", "configuration", "config", "configure", "default", "allow", "enable", "disable", "prevent", "restrict"}
	scored = sorted(((len(qw & set(stems(n))), n) for n in single_names()), reverse=True)
	hits = [n for s, n in scored if s][:6]
	if not hits:
		return None
	if len(hits) == 1 or scored[0][0] > scored[1][0]:
		res = manual_overview(hits[0], q)
		if res:
			return res
	return "## Settings pages\n" + "\n".join(f"- [{n}](/app/{slug(n)}) · [manual]({manual_url(n)})" for n in hits), []


def app_fields_answer(q, doctype):
	modules = next((m for k, m in APP_MODULES.items() if has_any(q, (k,))), None)
	if not modules or not doctype:
		return None
	targets = [doctype] + [df.options for df in frappe.get_meta(doctype).fields if df.fieldtype in ("Table", "Table MultiSelect")]
	rows = frappe.get_all("Custom Field", filters={"dt": ["in", targets], "module": ["in", list(modules)]}, fields=["dt", "label", "fieldname", "fieldtype"], order_by="dt, idx")
	if not rows:
		return None
	lines = [f"## Fields added by {', '.join(modules)} on {doctype}", "| Screen | Field | Fieldname | Type |", "|---|---|---|---|"]
	for r in rows[:60]:
		lines.append(f"| {r.dt} | {r.label or ''} | `{r.fieldname}` | {r.fieldtype} |")
	lines.append("\nThese are **Custom Field** records created by the app (stored in `tabCustom Field`, columns added to the screen's table).")
	return "\n".join(lines)


# ------------------------------------------------------------------ main entry
# A question is treated as a problem report only when it is framed as one.
ERROR_RE = re.compile(
	r"\b(?:error|errors|issue|issues|problem|problems|not working|not showing|not coming|not getting|not fetch\w*|not updat\w*|not submitt\w*|"
	r"not saving|not allowed|not set|not found|not able|won't|wont|can't|cannot|cant|unable|fail\w*|throw\w*|blocked|stuck|mismatch\w*|invalid|"
	r"insufficient|exceed\w*|crossed|already exists|frozen|wrong|galat|aa raha|ho raha|nahi ho|nahi aa|doesn't|does not|isn't|is not|"
	r"is mandatory|are mandatory|is required|are required|required error|missing|denied|stops me|not permitted|permission denied|"
	r"has been modified|modified after|it says|says|saying|shows an?|showing an?|popup|pop-up|still see|still shows?|not reflecting|not visible|"
	r"not sent|not receiving|not reaching|sitting in|keeps? (?:showing|failing))\b")
NAV_CANT_FIND = re.compile(r"\b(?:can't|cannot|cant|unable to|not able to) (?:find|locate|see where|open)\b")
PROCESS_WORDS = ("process", "steps", "procedure", "cycle", "flow")
LIST_FIELDS_RE = re.compile(r"\b(?:which|what|list|all|show)\b[^?]*\bfields\b|\bfields\s+(?:are there|of|in|available)\b")
EXPLAIN_WORDS = ("what does", "mean", "meaning", "concept", "kya hota", "what happens", "explain", "difference", "how does", "work")
SETTING_Q = re.compile(r"\b(?:is there (?:a|any) (?:setting|option|way)|which setting|what setting|setting (?:that|which|controls)|controls this|"
					   r"make it (?:compulsory|mandatory)|how do i make|where do i change|where can i change|where to change|how (?:do i |to )?(?:increase|change|turn)|lock)\b")
HOWTO_NEW_FIELD = re.compile(r"\b(?:add|create|new|extra)\b[^?]*\bfields?\b|\bwithout (?:touching )?(?:code|coding)\b")


def _answer(text, suggestions=None):
	return {"text": text, "suggestions": suggestions or []}


def answer(query):
	raw = (query or "").strip()
	q = normalize(raw)
	if not q:
		return _answer("Ask me anything about this ERP: a process, a field, an error message, a report, where a screen is, or the stock of an item.", default_suggestions())
	q = expand(correct_typos(q))
	raw_l = raw.lower()

	doctype = find_doctype(q)
	names = all_doctypes(q)
	child = child_in(q)
	cand = list(dict.fromkeys(([doctype] if doctype else []) + names + ([child] if child else [])))
	record = find_record(raw)
	techs = tech_names(raw)
	qfields, plain_quotes = quoted_fields(raw, cand)
	quoted_msg = bool(plain_quotes) and any(len(t.split()) >= 3 for t in plain_quotes)
	no_quotes = QUOTE_RE.sub(" ", raw_l)  # error words inside a quoted field name do not count
	trouble = bool(ERROR_RE.search(no_quotes) or quoted_msg) and not NAV_CANT_FIND.search(raw_l)
	field_q = has_any(q, FIELD_WORDS) or bool(techs) or bool(qfields)
	mechanism = bool(MECHANISM_RE.search(q))
	explain_q = has_any(q, CONCEPT_WORDS + EXPLAIN_WORDS)
	process_q = has_any(q, PROCESS_WORDS) and not has_any(q, ("field", "fields", "checkbox"))
	setting_q = bool(SETTING_Q.search(q))
	rule_q = bool(re.search(r"(?<!how )(?<!where )\b(?:can i|can we)\b|\b(?:is it possible|possible to|without|directly|skip|bypass|allowed to)\b", q)) or setting_q
	howto_new_field = bool(HOWTO_NEW_FIELD.search(q)) and has_any(q, ("how", "add", "create", "without")) and (not qfields or has_any(q, ("add", "without")))
	rest = set(stems(q)) - set(stems(doctype or "")) - {"stock"}

	hits = kb_search(q, raw, doctype=doctype)
	concept_top = next((h for h in hits if h[1]["kind"] == "concept"), None)
	strong_concept = bool(concept_top and concept_top[0] >= 12 and explain_q)
	pool = hits if (trouble or rule_q) else [h for h in hits if h[1]["kind"] != "problem"]

	# 0. quoted field names ("what does 'Skip Material Transfer to WIP Warehouse' do") are field questions
	if qfields and not howto_new_field and not (trouble and not has_any(q, FIELD_WORDS)):
		top_kb = pool[0] if pool else None
		if top_kb and top_kb[0] >= 14 and top_kb[1]["kind"] in ("concept", "guide") and has_any(q, ("how do", "how does", "work", "which one", "wins", "explain")):
			e = top_kb[1]["entry"]  # a concept question that also names a field: explain the concept, then the field
			parts = [render_entry(top_kb[1]["kind"], e), explain_fields(qfields[:2])]
			if has_any(q, FIELD_WORDS + ("options", "option")):
				parts.reverse()  # the question is mainly about the field
			return _answer("\n\n".join(parts), related_suggestions(hits, e))
		return _answer(explain_fields(qfields[:3]))

	# 1. a document number: its details and links (unless the question is really about a field, a process, settings, the data model, an error or a concept)
	asks_record = bool(record) and bool(re.search(r"\b(?:status|details?|info|information|summary|state|submitted|draft|cancelled)\b", q))
	concept_about_record = strong_concept and has_any(q, ("concept", "mean", "meaning", "explain", "what does", "difference"))
	other_topic = techs or has_any(q, HOW_WORDS + DATA_WORDS + ("why", "change", "prefix", "naming series")) or (trouble and not has_any(q, LINK_WORDS)) or concept_about_record
	if record and (asks_record or not other_topic):
		asked_field = field_q and any(len(stems(df.label)) >= 2 for _, df in find_fields(q, raw, record[0], limit=1))
		if not asked_field:
			rec = record_answer(*record)
			if rec:
				return _answer(rec)

	# 2. live stock of an item or a warehouse
	if STOCK_Q.search(q) and not has_any(q, ("how to", "how do i", "report", "error", "where is", "setting", "permission", "restrict", "role", "access", "entries")) and not strong_concept:
		ans = stock_answer(raw, q)
		if ans:
			return _answer(ans)

	# 3. company SOPs written in the manual
	sop = best_sop(q)
	if sop and sop["article_type"] == "Company SOP":
		return _answer(f"## {sop['title']}\n\n{sop['content']}")

	# 3b. "how do I add a field without code": the Customize Form guide (plus print settings when asked)
	if howto_new_field and not trouble:
		ids = ["customize-form"] + (["print-format-letterhead"] if re.search(r"\bprint", q) else [])
		parts = [render_entry("guide", g) for i in ids for g in GUIDES if g["id"] == i]
		if parts:
			return _answer("\n\n".join(parts), [f"Fields of {doctype}"] if doctype else [])

	# 4. troubleshooting: a pasted error message or a problem description
	txn_context = [n for n in names if frappe.db.get_value("DocType", n, "is_submittable")]
	problem_hits = kb_search(q, raw, kinds=("problem",), doctype=doctype or (record[0] if record else None), context=txn_context)
	field_first = bool(techs) and field_q  # "what does Required By (schedule_date) mean" is about a field, not an error
	data_q = has_any(q, DATA_WORDS) and not trouble
	if problem_hits and not field_first:
		top_score, top_doc, exact = problem_hits[0]
		other_intent = data_q or process_q or (explain_q and not trouble) or has_any(q, REPORT_WORDS)
		if (exact and (trouble or not other_intent)) or (trouble and top_score >= 6):
			top = top_doc["entry"]
			return _answer(render_entry("problem", top), related_suggestions(hits, top))

	# 5. data structure and how data is stored or linked
	schema_words = ("child table", "child tables", "table", "tables", "fields", "doctype name", "which doctype", "what doctype", "stored", "store", "stores")
	q_nodt = q
	for n in names:
		q_nodt = re.sub(rf"(?<![a-z0-9]){re.escape(n.lower())}(?![a-z0-9])", " ", q_nodt)  # "salary structure" is not a data-structure question
	if has_any(q_nodt, DATA_WORDS) or mechanism or (child and has_any(q, schema_words)):
		if len(names) >= 2 and has_any(q, LINK_WORDS + ("linked", "link", "fields hold")):
			text = link_answer(names)
			if text:
				return _answer(text)
		app_ans = app_fields_answer(q, doctype)
		if app_ans:
			return _answer(app_ans)
		target = child or doctype
		concepts = [h for h in hits if h[1]["kind"] == "concept"]
		dt_l = (doctype or "").lower()
		structure_of = re.search(r"\b(?:structure|schema|tables?|columns?) of (?:a |an |the )?(.+)$", q)
		if child and doctype and structure_of and doctype.lower() in structure_of.group(1):
			target = doctype  # "table structure of Landed Cost Voucher" even when a child table is also named
		explicit_schema = target and (
			child or re.search(r"\b(?:table name|schema|data structure|database (?:table|schema)|structure of|columns? of|fieldnames?|child (?:table|doctype)s?|doctype name|which (?:table|doctype)|main fields|fields of|(?:what|which) tables|tables and fields|tables behind|table which)\b", q)
			or (dt_l and re.search(rf"\b{re.escape(dt_l)}\s+(?:data|records?)\b|\b(?:data|records?) of (?:a |an |the )?{re.escape(dt_l)}\b", q))
		)
		generic_target = target in ("Warehouse", "Item", "Company", "Customer", "Supplier") and mechanism and not child
		if concepts and concepts[0][0] >= 6 and (not explicit_schema or generic_target):
			top = concepts[0][1]["entry"]
			return _answer(render_entry("concept", top), related_suggestions(hits, top) + ([f"Data structure of {doctype}"] if doctype else []))
		if target:
			if re.search(r"\bfields?\b", q) and not re.search(r"\b(?:tables?|schema|structure|stored|store|doctype)\b", q):
				return _answer(fields_listing(target), [f"Data structure of {target}"])
			return _answer(schema_answer(target, q), [f"Fields of {target}", f"How to create {target}"])

	# 6. where is a screen that is named explicitly ("bank reconciliation tool kahan milega")
	explicit_dt = doctype and re.search(rf"(?<![a-z0-9]){re.escape(doctype.lower())}(?![a-z0-9])", q)
	nav_filler = set(stems("where find open locate location located menu navigate get go see screen page tool module kahan kaha milega milta hai is the a an i can do we how to which in of"))
	leftover = set(stems(q)) - set(stems(doctype or "")) - nav_filler - set(stems(" ".join(STOP)))
	if explicit_dt and has_any(q, WHERE_WORDS) and len(leftover) <= 1 and not has_any(q, ("report", "reports", "field", "fields") + LINK_WORDS) and not trouble and not setting_q:
		return _answer(f"## {doctype}\n\n" + where_text(doctype) + f"\n\n[Manual for {doctype}]({manual_url(doctype)})", [f"How to create {doctype}"])

	# 7. reports (by name, or by everyday phrases like "how much customers owe us")
	hinted = hinted_reports(q, raw)
	howto = has_any(q, ("how do i", "how to", "how can i", "steps", "process", "procedure")) and not has_any(q, ("report", "reports"))
	if hinted and has_any(q, ("see", "check", "view", "show", "know", "find out", "track", "list", "which", "reconcile")):
		howto = False  # "how do I see how much customers owe us" is a report question
	if (has_any(q, REPORT_WORDS) or hinted) and not howto and not has_any(q, ("field", "fields")) and not (hinted == [] and doctype and not has_any(q, REPORT_WORDS)):
		rep = reports_answer(q, raw, doctype)
		if rep:
			return _answer(rep, ["Accounts reports", "Stock reports"])

	# 8. customizations (but "how do I add a custom field" is a how-to)
	if has_any(q, CUSTOM_WORDS) and (not has_any(q, ("how", "add", "create", "make", "without coding")) or re.search(r"\bexport", q)) and not howto_new_field:
		qq = re.sub(r"\bcustom\s+(?:fields?|screens?|doctypes?)\b|\bcustomi[sz](?:ations?|ed)\b|\b(?:client|server)?\s*scripts?\b|\bcustom\b|\b(?:our|this|the|for)\s+company\b|\bexport\b", " ", q)
		text = customizations_answer(find_doctype(qq))
		if has_any(q, ("export", "move", "another site")):
			guide = next((g for g in GUIDES if g["id"] == "export-customizations"), None)
			if guide:
				text += "\n\n" + render_entry("guide", guide)
		return _answer(text)

	# 9. fields added by an installed app ("which GST fields does India Compliance add on Sales Invoice")
	if doctype and re.search(r"\bfields\b", q) and has_any(q, ("add", "added", "adds", "adding", "which", "list")):
		app_ans = app_fields_answer(q, doctype)
		if app_ans:
			return _answer(app_ans)

	# 10. comparisons: two fields ("Price List Rate vs Rate") or two screens ("Hostel Registration vs Hostel Allocation")
	if has_any(q, COMPARE_WORDS + ("different from", "differ", "differs", "different")):
		pair = find_fields(q, raw, doctype, limit=2, candidates=cand, keep_subsets=True) if cand else []
		qs_c = set(stems(q))
		both_named = all(all(wmatch(w, qs_c) for w in stems(df.label)) for _, df in pair)
		if len(pair) == 2 and any(len(stems(df.label)) >= 2 for _, df in pair) and (both_named or len(names) < 2):
			return _answer(compare_fields(pair))
		if len(names) >= 2 and not strong_concept:
			return _answer(compare_doctypes(names[:3]))

	# 11. "which fields are there in Hostel Allocation"
	if doctype and LIST_FIELDS_RE.search(q) and not howto_new_field:
		return _answer(fields_listing(child or doctype), [f"Data structure of {doctype}"])

	# 12. settings asked as a need ("is there a setting that locks the rate", "make it compulsory to pick a leave approver")
	if setting_q and not trouble:
		res = settings_answer(q, raw, allow_partial=True)
		if res:
			return _answer(res[0], res[1])

	# 13. specific fields ("what does Update Stock mean on Sales Invoice", "Received Qty and Billed Amt")
	kb_strong = bool(pool) and pool[0][0] >= 14 and not field_q
	if rest and not howto_new_field and not (process_q and not field_q) and not kb_strong and (
		field_q or (doctype and not has_any(q, HOW_WORDS + WHERE_WORDS + LINK_WORDS + WORKFLOW_WORDS))
	) and (not trouble or field_first):
		found = find_fields(q, raw, doctype, limit=3, candidates=cand) if cand else []
		if not found and (has_any(q, SETTINGS_WORDS) or not cand):
			s = find_field_anywhere(q, raw, singles_only=has_any(q, SETTINGS_WORDS))
			if s and (len(stems(s[1].label)) >= 2 or s[1].fieldname in techs):
				found = [s]
		qs = set(stems(q))
		full = [f for f in found if all(wmatch(w, qs) for w in stems(f[1].label))]
		single_word = bool(found) and len(stems(found[0][1].label)) == 1 and found[0][1].fieldname not in techs
		partial_only = bool(found) and not full and found[0][1].fieldname not in techs
		concept_wins = strong_concept and (not found or single_word or partial_only)
		if found and not concept_wins and (field_q or not single_word):
			if len(full) >= 2 and re.search(r"\band\b|,", q):
				return _answer(explain_fields(full[:3]))
			meta, df = (full or found)[0]
			return _answer(explain_field(df, meta), [f"Fields of {meta.name}"] if not meta.istable else [])

	# 14. settings ("how do I allow negative stock", "stop users selling below cost", "Stock Settings")
	s_any = find_field_anywhere(q, raw, singles_only=True) if (kb_strong and has_any(q, SETTINGS_WORDS)) else None
	incidental = bool(s_any) and set(stems(s_any[1].label)) <= set(stems(" ".join(cand)))  # "cost center" on Payment Reconciliation
	if has_any(q, SETTINGS_WORDS) and not trouble and not process_q and not incidental:
		res = settings_answer(q, raw)
		if res:
			return _answer(res[0], res[1])

	# 15. fields of a screen
	if doctype and re.search(r"\bfields?\b", q) and not howto_new_field:
		return _answer(fields_listing(child or doctype), [f"Data structure of {doctype}"])

	# 16. where is a screen / how do I open it
	navigation = has_any(q, WHERE_WORDS + ("which module",)) and not has_any(q, ("connection", "connections", "linked", "linkage")) and (
		not has_any(q, HOW_WORDS) or re.search(r"\bhow\b.*\b(?:open|get to|go to|find|reach|navigate|edit|access)\b", q))
	if doctype and navigation and (not trouble or NAV_CANT_FIND.search(raw_l)):
		fld = [f for f in find_fields(q, raw, doctype, limit=1, candidates=cand) if len(stems(f[1].label)) >= 2
			   and not set(stems(f[1].label)) <= set(stems(" ".join(cand)))]
		if kb_strong and len(leftover) > 1 and not has_any(q, ("screen", "module", "menu")):
			e = pool[0][1]["entry"]  # "customer ka credit limit kaha set karte": the topic, not just the screen
			return _answer(render_entry(pool[0][1]["kind"], e), related_suggestions(hits, e))
		if fld and not has_any(q, ("screen", "module", "menu", "list")) and not kb_strong:
			return _answer(explain_field(fld[0][1], fld[0][0]), [f"Fields of {doctype}"])
		if kb_strong and pool[0][1]["kind"] in ("guide", "concept") and doctype in (pool[0][1]["entry"].get("doctypes") or []) and has_any(q, SETTINGS_WORDS + ("define", "configure", "set up")):
			e = pool[0][1]["entry"]
			return _answer(render_entry(pool[0][1]["kind"], e), related_suggestions(hits, e))
		parts = []
		for n in (names[:3] if len(names) > 1 else [doctype]):
			parts.append(f"## {n}\n\n" + where_text(n))
		text = "\n\n".join(parts)
		if record:
			text += f"\n- **This document:** [{record[1]}]({doc_url(*record)})"
		if doctype == "Item":
			code = next((t for t in re.findall(r"\b[A-Za-z0-9][A-Za-z0-9\-_.]{2,}\b", raw) if any(ch.isdigit() for ch in t) and frappe.db.exists("Item", t)), None)
			if code:
				text += f"\n- **This item:** [{code}](/app/item/{quote(code)}): open it, edit the fields and **Save**."
		return _answer(text + f"\n\n[Manual for {doctype}]({manual_url(doctype)})", [f"How to create {doctype}", f"Fields of {doctype}"])

	# 17. linkage of a screen ("which documents can I create from a Sales Order")
	if doctype and has_any(q, LINK_WORDS + ("create from", "made from", "documents from", "make from")) and not has_any(q, ("how to",)):
		if record and has_any(q, LINK_WORDS):
			rec = record_answer(*record)
			if rec:
				return _answer(rec)
		res = manual_overview(doctype, q + " linkage")
		if res:
			return _answer(res[0], res[1])

	# 18. custom screens: explain how they work together
	if doctype and frappe.db.get_value("DocType", doctype, "custom") and not howto_new_field:
		return _answer(custom_module_answer(doctype, q), [f"Fields of {doctype}", f"Data structure of {doctype}"])

	# 19. guides, concepts (and, for problem reports or rule questions, troubleshooting) by relevance
	if pool:
		score, d, _ = pool[0]
		kind, e = d["kind"], d["entry"]
		concept_q = explain_q and not has_any(q, ("how to", "steps"))
		guide_hit = next((h for h in pool if h[1]["kind"] == "guide"), None)
		rule_hit = next((h for h in hits[:3] if h[1]["kind"] == "problem"), None)
		if concept_q and concept_top and concept_top[0] >= 0.8 * score:
			kind, e, score = "concept", concept_top[1]["entry"], concept_top[0]
		elif rule_q and rule_hit and rule_hit[0] >= 0.6 * score:
			kind, e, score = "problem", rule_hit[1]["entry"], rule_hit[0]  # "can I … without …" asks about a rule/setting
		elif has_any(q, HOW_WORDS) and guide_hit and guide_hit[0] >= 0.7 * score:
			kind, e, score = "guide", guide_hit[1]["entry"], guide_hit[0]
		strong = score >= 7 or (score >= 5 and not doctype)
		if strong and not (doctype and kind != "problem" and doctype not in (e.get("doctypes") or []) and score < 10):
			text = render_entry(kind, e)
			# a question about two things ("e-invoice and e-way bill") gets both guides
			if kind == "guide" and re.search(r"\band\b", q):
				other = next((h for h in pool if h[1]["kind"] == "guide" and h[1]["entry"] is not e and h[0] >= 0.5 * score), None)
				if other and (set(stems(other[1]["entry"]["title"])) - set(stems(e["title"]))) & (set(stems(q)) - GENERIC_NOISE):
					text += "\n\n" + render_entry("guide", other[1]["entry"])
			return _answer(text, related_suggestions(hits, e))
	if sop:
		return _answer(f"## {sop['title']}\n\n{sop['content']}")

	# 20. overview of a screen from the manual
	if doctype:
		res = manual_overview(doctype, q)
		if res:
			return _answer(res[0], res[1])
		return _answer(f"## {doctype}\n\n" + where_text(doctype))

	# 21. weaker knowledge match
	if pool and pool[0][0] >= 3.5:
		d = pool[0][1]
		return _answer(render_entry(d["kind"], d["entry"]), related_suggestions(hits, d["entry"]))

	# 22. records
	found = search_answer(raw)
	if found:
		return _answer(found)

	return {
		"text": "I could not find a direct answer to this question. Try rephrasing it with the screen name (for example *Purchase Order*) or the exact error message, choose a topic below, or ask the **AI Agent**.",
		"suggestions": [h[1]["entry"]["title"] for h in hits[:3]] or default_suggestions(),
		"is_fallback": True,
	}


def default_suggestions():
	return [
		"How to create a purchase order",
		"Sales cycle process",
		"Insufficient stock error",
		"What is Update Stock in Sales Invoice",
		"Data structure of Sales Invoice",
		"How to apply leave",
	]