"""One place that combines every knowledge file used by the Help Guide.

- GUIDES:      step-by-step processes (knowledge.GUIDES + guides_extra.GUIDES_EXTRA)
- PROBLEMS:    troubleshooting entries: error text -> cause -> fix (problems_*.py)
- CONCEPTS:    how ERPNext works internally and its data model (concepts.py)
- FIELD_NOTES: plain-English meaning of fields (knowledge.FIELD_NOTES + fields_extra.FIELD_NOTES_EXTRA)

A knowledge file that is missing or broken is skipped (and logged) instead of breaking Help."""

import importlib

from erp_ai_assistant.knowledge import FIELD_NOTES as _BASE_FIELD_NOTES
from erp_ai_assistant.knowledge import GUIDES as _BASE_GUIDES


def _load(module, attr, default):
	try:
		return getattr(importlib.import_module(f"erp_ai_assistant.{module}"), attr)
	except Exception as e:  # keep Help working even if one content file is bad
		try:
			import frappe

			frappe.log_error(title=f"Help knowledge file {module} not loaded", message=repr(e))
		except Exception:
			pass
		return default


def _unique(entries):
	seen, out = set(), []
	for e in entries:
		if isinstance(e, dict) and e.get("id") and e["id"] not in seen:
			seen.add(e["id"])
			out.append(e)
	return out


GUIDES = _unique(list(_BASE_GUIDES) + list(_load("guides_extra", "GUIDES_EXTRA", [])) + list(_load("guides_more", "GUIDES_MORE", [])))
PROBLEMS = _unique(
	list(_load("problems_stock", "PROBLEMS", []))
	+ list(_load("problems_accounts", "PROBLEMS", []))
	+ list(_load("problems_trade", "PROBLEMS", []))
	+ list(_load("problems_hr_system", "PROBLEMS", []))
	+ list(_load("problems_extra", "PROBLEMS", []))
)
REPORT_HINTS = list(_load("report_hints", "REPORT_HINTS", []))
PHRASE_ALIASES = dict(_load("report_hints", "PHRASE_ALIASES", {}))
REPORT_DESCRIPTIONS = dict(_load("report_hints", "REPORT_DESCRIPTIONS", {}))
DT_FIELD_NOTES = dict(_load("dt_field_notes", "DT_FIELD_NOTES", {}))
CONCEPTS = _unique(list(_load("concepts", "CONCEPTS", [])))
FIELD_NOTES = {**_load("fields_extra", "FIELD_NOTES_EXTRA", {}), **_BASE_FIELD_NOTES}
