import frappe
from frappe.model.document import Document


class ERPHelpArticle(Document):
	def before_insert(self):
		if not self.article_key:
			self.article_key = "sop:" + frappe.scrub(self.title or frappe.generate_hash(length=8)).replace("_", "-")[:120]

	def validate(self):
		# Articles typed by people are never overwritten by the automatic rebuild.
		if not self.flags.from_manual_builder:
			self.source = "Manual"
			if self.article_type == "DocType Manual":
				self.article_type = "Company SOP"
		frappe.cache.delete_value("eaa_help_articles")
