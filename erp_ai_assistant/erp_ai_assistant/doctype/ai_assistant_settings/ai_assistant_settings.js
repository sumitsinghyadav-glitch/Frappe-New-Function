frappe.ui.form.on("AI Assistant Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Test Connection"), () => test_connection(frm));
		frm.add_custom_button(__("Rebuild User Manual"), () => {
			frappe.call("erp_ai_assistant.api.rebuild_manual").then(() =>
				frappe.show_alert({ message: __("The user manual is being rebuilt. It takes about a minute."), indicator: "green" })
			);
		}, __("User Manual"));
		frm.add_custom_button(__("Open User Manual"), () => frappe.set_route("List", "ERP Help Article"), __("User Manual"));
		frappe.call("erp_ai_assistant.api.manual_stats").then((r) => {
			const s = r.message || {};
			frm.dashboard.set_headline(
				__("User manual: {0} screens ({1} customized), {2} SOPs and guides. Last built: {3}", [
					s.manuals || 0, s.customized || 0, s.sops || 0, s.last_built ? frappe.datetime.str_to_user(s.last_built) : __("never"),
				])
			);
		});
	},
});

function test_connection(frm) {
	const run = () => frappe.call({
		method: "erp_ai_assistant.api.test_ai_connection",
		freeze: true,
		freeze_message: __("Testing every configured model…"),
	}).then((r) => {
		const rows = (r.message || []).map((x) => `<tr>
			<td>${frappe.utils.escape_html(x.model)}</td>
			<td>${x.ok ? "✅" : "❌"}</td>
			<td style="text-align:right">${x.seconds}s</td>
			<td>${x.tools ? "✅" : "—"}</td>
			<td>${frappe.utils.escape_html(x.note || "")}</td></tr>`).join("");
		frappe.msgprint({
			title: __("AI connection test"),
			wide: true,
			message: `<table class="table table-bordered table-sm">
				<thead><tr><th>${__("Model")}</th><th>${__("Reached")}</th><th>${__("Time")}</th><th>${__("Tools")}</th><th>${__("Note")}</th></tr></thead>
				<tbody>${rows}</tbody></table>
				<p class="text-muted small">${__("Models are tried in this order. A model that answers but does not call tools cannot create documents.")}</p>`,
		});
	});
	if (frm.is_dirty()) frm.save().then(run); else run();
}
