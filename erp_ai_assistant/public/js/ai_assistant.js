/* ERP AI Assistant: unified chat blending instant Help Guide and AI Agent together. */
(() => {
	const STORE = "erp_ai_assistant_state";
	const HELP_EXAMPLES = [
		"How to create a purchase order",
		"Sales cycle: Order → Delivery → Invoice",
		"What is Set Target Warehouse in Purchase Order?",
		"Where is Stock Entry?",
		"How to transfer stock between warehouses?",
		"Stock of MS Steel Pipe",
		"How to apply leave",
	];
	const AGENT_EXAMPLES = [
		"Create a purchase order for 10 MS Steel Pipe 2 inch from Summit Traders Ltd. at ₹800 for Gwalior Plant",
		"Create a sales order for Grant Plastics Ltd. for 20 Fermented Organic Manure bags, deliver it and make invoice",
		"Transfer 50 MS Steel Pipe from Gwalior Plant to Indore Depot",
	];

	const load = () => {
		try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch (e) { return {}; }
	};
	const save = (state) => {
		try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* storage unavailable */ }
	};

	let state = load();
	state.items = state.items || [];
	state.mode = state.mode || "auto"; // "auto" (both at once), "help", or "agent"
	let busy = false;
	let $panel, $log, $input, $send, $status, $modes;

	const esc = (s) => frappe.utils.escape_html(s || "");
	const md = (s) => (frappe.markdown ? frappe.markdown(s || "") : esc(s));

	function render_item(item) {
		if (item.kind === "user") return `<div class="eaa-msg eaa-user">${esc(item.text)}</div>`;
		if (item.kind === "bot") {
			const badge = item.source === "help"
				? `<span class="eaa-src eaa-src-help">💡 ${__("Help Guide")}</span>`
				: `<span class="eaa-src eaa-src-agent">🤖 ${__("AI Agent")}</span>`;

			let html = `<div class="eaa-msg eaa-bot">${badge}${md(item.text)}`;

			if (item.suggestions && item.suggestions.length) {
				html += `<div class="eaa-suggestions">
					${item.suggestions.map((s) => `<button class="eaa-chip ${s.startsWith("⚡") ? "eaa-chip-action" : ""}">${esc(s)}</button>`).join("")}
				</div>`;
			}
			if (item.source === "help" && item.user_query) {
				html += `<div class="eaa-msg-footer">
					<button class="eaa-ask-ai" data-query="${esc(item.user_query)}">⚡ ${__("Ask AI Agent instead")}</button>
				</div>`;
			}
			html += `</div>`;
			return html;
		}
		if (item.kind === "error") return `<div class="eaa-msg eaa-error">${esc(item.text)}</div>`;
		if (item.kind === "note") return `<div class="eaa-note">${md(item.text)}</div>`;
		if (item.kind === "step") return `<div class="eaa-step ${item.error ? "eaa-step-err" : ""}">${esc(item.text)}</div>`;
		if (item.kind === "doc") {
			const d = item.doc;
			const total = d.grand_total ? ` · ₹${format_number(d.grand_total)}` : "";
			return `<a class="eaa-doc" href="${esc(d.url)}"><span class="eaa-doc-state eaa-${esc(d.state.toLowerCase())}">${esc(d.state)}</span>
				<b>${esc(d.doctype)}</b> ${esc(d.name)}${total}</a>`;
		}
		return "";
	}

	function format_number(v) {
		try { return Number(v).toLocaleString("en-IN", { maximumFractionDigits: 2 }); } catch (e) { return v; }
	}

	function push(item) {
		state.items.push(item);
		if (state.items.length > 200) state.items = state.items.slice(-200);
		save(state);
		$log.find(".eaa-empty").remove();
		$log.append(render_item(item));
		$log.scrollTop($log[0].scrollHeight);
	}

	function set_busy(on, status_text) {
		busy = on;
		$send.prop("disabled", on);
		$input.prop("disabled", on);
		$status.find(".eaa-status-text").text(status_text || __("Working…"));
		$status.toggle(on);
		if (!on) $input.trigger("focus");
	}

	function empty_html() {
		if (state.mode === "help") {
			return `<div class="eaa-empty">
				<p class="eaa-empty-desc">${__("Ask anything about ERPNext: step-by-step processes, field explanations, where to find screens, or current stock. (Instant & Free)")}</p>
				<div class="eaa-examples-title">${__("Frequently asked topics:")}</div>
				${HELP_EXAMPLES.map((e) => `<button class="eaa-example">${esc(e)}</button>`).join("")}
			</div>`;
		}
		if (state.mode === "agent") {
			return `<div class="eaa-empty">
				<p class="eaa-empty-desc">${__("Tell me what to create. The AI agent will inspect your masters and build/submit transactions for you.")}</p>
				<div class="eaa-examples-title">${__("Example action commands:")}</div>
				${AGENT_EXAMPLES.map((e) => `<button class="eaa-example">${esc(e)}</button>`).join("")}
			</div>`;
		}
		// Default: Both (Auto)
		return `<div class="eaa-empty">
			<div class="eaa-hero-badge">⚡ ${__("Simple AI: Help Guide + AI Agent")}</div>
			<p class="eaa-empty-desc">${__("Ask any question for an instant guide, or give an action command to create documents automatically.")}</p>
			<div class="eaa-examples-title">💡 ${__("Ask a Question (Instant Guide):")}</div>
			${HELP_EXAMPLES.slice(0, 4).map((e) => `<button class="eaa-example">${esc(e)}</button>`).join("")}
			<div class="eaa-examples-title" style="margin-top:10px">⚡ ${__("Give a Command (AI Agent):")}</div>
			${AGENT_EXAMPLES.slice(0, 2).map((e) => `<button class="eaa-example">${esc(e)}</button>`).join("")}
		</div>`;
	}

	function update_mode_ui() {
		$modes.find(".eaa-mode-btn").removeClass("active");
		$modes.find(`.eaa-mode-btn[data-mode="${state.mode}"]`).addClass("active");
		if (state.mode === "help") {
			$input.attr("placeholder", __("Ask about any process, field, screen or stock... (Instant)"));
		} else if (state.mode === "agent") {
			$input.attr("placeholder", __("e.g. Make a PO for 10 pipes from Summit Traders and receive it"));
		} else {
			$input.attr("placeholder", __("Ask a question or give a command (PO, Invoice, Stock, Guide)..."));
		}
	}

	function switch_mode(mode) {
		if (state.mode === mode) return;
		state.mode = mode;
		save(state);
		update_mode_ui();
		if (!$log.find(".eaa-msg").length) {
			$log.html(empty_html());
		}
		check_status();
	}

	function build() {
		const $btn = $(`<button class="eaa-launcher" title="${__("Simple AI")}">
			<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
		</button>`).appendTo("body");

		$panel = $(`<div class="eaa-panel" style="display:none">
			<div class="eaa-head">
				<span>${__("Simple AI")}<small class="eaa-model"></small></span>
				<span class="eaa-head-actions">
					<button class="eaa-new" title="${__("Start a new conversation")}">＋ ${__("New chat")}</button>
					<button class="eaa-close" title="${__("Close")}">✕</button>
				</span>
			</div>
			<div class="eaa-modes">
				<button class="eaa-mode-btn ${state.mode === "auto" ? "active" : ""}" data-mode="auto" title="${__("Intelligently uses Help Guide for instant answers and AI Agent for document creation")}">
					⚡ ${__("Both (Auto)")}
				</button>
				<button class="eaa-mode-btn ${state.mode === "help" ? "active" : ""}" data-mode="help" title="${__("Instant offline knowledge and guides")}">
					💡 ${__("Help Guide")}
				</button>
				<button class="eaa-mode-btn ${state.mode === "agent" ? "active" : ""}" data-mode="agent" title="${__("AI model for automated document generation")}">
					🤖 ${__("AI Agent")}
				</button>
			</div>
			<div class="eaa-log"></div>
			<div class="eaa-status" style="display:none">
				<span><span class="eaa-dot"></span><span class="eaa-status-text">${__("Working…")}</span></span>
				<button class="eaa-stop" title="${__("Stop this operation")}">■ ${__("Stop")}</button>
			</div>
			<div class="eaa-compose">
				<textarea rows="2" placeholder="${__("Ask a question or give a command (PO, Invoice, Stock, Guide)...")}"></textarea>
				<button class="btn btn-primary btn-sm eaa-send">${__("Send")}</button>
			</div>
		</div>`).appendTo("body");

		$log = $panel.find(".eaa-log");
		$input = $panel.find("textarea");
		$send = $panel.find(".eaa-send");
		$status = $panel.find(".eaa-status");
		$modes = $panel.find(".eaa-modes");

		$log.html(state.items.length ? state.items.map(render_item).join("") : empty_html());
		update_mode_ui();

		$btn.on("click", () => {
			$panel.toggle();
			if ($panel.is(":visible")) { check_status(); $log.scrollTop($log[0].scrollHeight); $input.trigger("focus"); }
		});
		$panel.find(".eaa-close").on("click", () => $panel.hide());
		$panel.find(".eaa-new").on("click", reset);
		$panel.find(".eaa-stop").on("click", stop);
		$modes.on("click", ".eaa-mode-btn", function() {
			switch_mode($(this).data("mode"));
		});
		$send.on("click", () => send());
		$input.on("keydown", (e) => {
			if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
		});
		$log.on("click", ".eaa-example, .eaa-chip", function() {
			let txt = $(this).text().trim();
			if (txt.startsWith("⚡ Create ") && txt.endsWith(" with AI")) {
				txt = txt.replace(/^⚡\s*/, "").replace(/\s*with AI$/, "");
			} else if (txt.startsWith("⚡ ")) {
				txt = txt.replace(/^⚡\s*/, "");
			}
			$input.val(txt);
			send(txt);
		});
		$log.on("click", ".eaa-ask-ai", function() {
			const query = $(this).data("query");
			if (query) {
				send(query, "agent");
			}
		});
		$log.on("click", "a.eaa-doc, .eaa-bot a", (e) => {
			const href = $(e.currentTarget).attr("href") || "";
			if (href.startsWith("/app/")) { e.preventDefault(); frappe.set_route(href.replace("/app/", "").split("/")); }
		});

		frappe.realtime.on("erp_ai_assistant", on_event);
		if (state.pending && state.mode !== "help") set_busy(true, __("AI Agent working…"));
	}

	function check_status() {
		frappe.call({ method: "erp_ai_assistant.api.get_status", callback: (r) => {
			const s = r.message || {};
			$panel.find(".eaa-setup").remove();
			$panel.find(".eaa-model").text(s.model ? `${s.provider} · ${s.model}` : "");
			if (state.mode === "agent" && (!s.enabled || !s.configured)) {
				const link = s.can_configure ? ` <a href="/app/ai-assistant-settings">${__("Open AI Assistant Settings")}</a>` : "";
				const why = s.enabled ? __("The selected AI provider needs an API key.") : __("The assistant is disabled.");
				$log.prepend(`<div class="eaa-msg eaa-error eaa-setup">${why}${link}</div>`);
			}
		}});
	}

	const FINAL = ["done", "error", "cancelled"];

	function on_event(data) {
		if (!data || data.conversation_id !== state.conversation_id) return;
		const from_stopped = data.run_id && data.run_id === state.stopping_run;
		if (!from_stopped && data.run_id && state.run_id && data.run_id !== state.run_id) return;

		if (from_stopped) {
			if (data.type === "doc") push({ kind: "doc", doc: data.doc });
			else if (FINAL.includes(data.type)) {
				push({ kind: data.type === "error" ? "error" : "bot", source: "agent", text: data.text });
				state.stopping_run = null;
				save(state);
			}
			return;
		}
		if (data.type === "step") push({ kind: "step", text: data.text, error: data.error });
		else if (data.type === "note") push({ kind: "note", text: data.text });
		else if (data.type === "doc") push({ kind: "doc", doc: data.doc });
		else if (FINAL.includes(data.type)) {
			push({ kind: data.type === "error" ? "error" : "bot", source: "agent", text: data.text });
			finish_run();
		}
	}

	function finish_run() {
		state.pending = false;
		state.run_id = null;
		save(state);
		set_busy(false);
	}

	function send(forced_text, forced_mode) {
		const text = (forced_text !== undefined ? forced_text : $input.val() || "").trim();
		if (!text || busy) return;
		if (forced_text === undefined) $input.val("");
		push({ kind: "user", text });

		const effective_mode = forced_mode || state.mode || "auto";
		set_busy(true, effective_mode === "help" ? __("Finding guide…") : __("Processing…"));

		state.cancel_requested = false;
		frappe.call({
			method: "erp_ai_assistant.api.send",
			args: {
				message: text,
				conversation_id: state.conversation_id,
				mode: effective_mode,
			},
			callback: (r) => {
				const res = r.message || {};
				state.conversation_id = res.conversation_id || state.conversation_id;

				if (res.source === "help") {
					// Instant response from Help Guide
					set_busy(false);
					const data = res.data || {};
					push({
						kind: "bot",
						source: "help",
						user_query: text,
						text: data.text || __("No guide found."),
						suggestions: data.suggestions || [],
					});
				} else if (res.source === "agent") {
					// Background execution by AI Agent
					if (state.cancel_requested) {
						cancel_on_server(res.run_id);
						state.stopping_run = res.run_id;
					} else {
						state.run_id = res.run_id;
						state.pending = true;
						set_busy(true, __("AI Agent working…"));
					}
					save(state);
				}
			},
			error: () => set_busy(false),
		});
	}

	function cancel_on_server(run_id) {
		if (run_id) frappe.call({ method: "erp_ai_assistant.api.cancel_run", args: { run_id } });
	}

	function stop() {
		if (!busy) return;
		if (state.run_id) {
			cancel_on_server(state.run_id);
			state.stopping_run = state.run_id;
		} else {
			state.cancel_requested = true;
		}
		push({ kind: "step", text: __("Stopping… anything already created is kept."), error: 1 });
		finish_run();
	}

	function reset() {
		cancel_on_server(state.run_id);
		if (state.conversation_id) {
			frappe.call({ method: "erp_ai_assistant.api.reset_conversation", args: { conversation_id: state.conversation_id } });
		}
		state = { items: [], mode: state.mode || "auto" };
		save(state);
		set_busy(false);
		$log.html(empty_html());
		check_status();
	}

	$(document).on("app_ready", () => {
		if (frappe.session && frappe.session.user !== "Guest" && !$(".eaa-launcher").length) build();
	});
})();
