import hashlib
import os

app_name = "erp_ai_assistant"
app_title = "ERP AI Assistant"
app_publisher = "Sumit"
app_description = "Chat assistant that creates ERPNext transactions from plain-language commands"
app_email = "admin@sumit.local"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]


def _versioned(path):
	"""Add a content hash so browsers fetch the new file after every update instead of a cached copy."""
	file = os.path.join(os.path.dirname(__file__), "public", path)
	try:
		with open(file, "rb") as f:
			version = hashlib.md5(f.read()).hexdigest()[:10]
	except OSError:
		version = "0"
	return f"/assets/erp_ai_assistant/{path}?v={version}"


app_include_js = _versioned("js/ai_assistant.js")
app_include_css = _versioned("css/ai_assistant.css")

# Keep the built-in user manual (ERP Help Article) in step with every customization.
_refresh = {"on_update": "erp_ai_assistant.manual.on_meta_change", "on_trash": "erp_ai_assistant.manual.on_meta_change"}
doc_events = {
	dt: _refresh
	for dt in ("DocType", "Custom Field", "Property Setter", "Client Script", "Server Script", "Workflow", "Report", "Notification")
}
scheduler_events = {"daily": ["erp_ai_assistant.manual.schedule_full_rebuild"]}
after_migrate = ["erp_ai_assistant.manual.schedule_full_rebuild"]
