import frappe

from erp_ai_assistant.agent import CUSTOM, LOCAL, cache_key, cancel_key, settings


@frappe.whitelist()
def test_ai_connection():
	"""Try every configured model once with a tiny tool-call request; report speed and whether tools work."""
	frappe.only_for("System Manager")
	import time

	from erp_ai_assistant.agent import ANTHROPIC, AgentStop, ModelRouter, Turn, openai_tools

	s = settings()
	if s.provider == ANTHROPIC:
		import anthropic

		t = time.time()
		try:
			anthropic.Anthropic(api_key=s.api_key, timeout=s.timeout or 25).messages.create(
				model=s.model, max_tokens=50, messages=[{"role": "user", "content": "Reply with OK"}]
			)
			return [{"model": s.model, "ok": True, "seconds": round(time.time() - t, 1), "tools": True, "note": "connected"}]
		except Exception as e:
			return [{"model": s.model, "ok": False, "seconds": round(time.time() - t, 1), "tools": False, "note": str(e)[:200]}]
	turn = Turn(frappe.session.user, "test", 5)
	turn.publish = lambda *a, **k: None
	try:
		router = ModelRouter(s, turn)
	except AgentStop as e:
		return [{"model": s.model, "ok": False, "seconds": 0, "tools": False, "note": str(e)}]
	tools = openai_tools({"get_stock_balance"})
	out = []
	for i, (provider, client, model, extra) in enumerate(router.candidates):
		# a local model may need a minute to load into memory on its first request
		is_local = provider == LOCAL or "11434" in str(getattr(client, "base_url", ""))
		local_timeout = max(120, s.timeout or 25)
		t = time.time()
		try:
			r = client.chat.completions.create(
				model=model, tools=tools, temperature=0.1, timeout=local_timeout if is_local else (s.timeout or 25), **extra,
				messages=[{"role": "user", "content": "What is the stock of item STEEL-PIPE-2IN? Use the tool."}],
			)
			used_tool = bool(r.choices[0].message.tool_calls)
			out.append({"model": f"{model} ({provider})", "ok": True, "seconds": round(time.time() - t, 1), "tools": used_tool,
						"note": "ready" if used_tool else "answered, but did not call the tool"})
		except Exception as e:
			out.append({"model": f"{model} ({provider})", "ok": False, "seconds": round(time.time() - t, 1), "tools": False, "note": str(e)[:160]})
	return out


@frappe.whitelist()
def get_status():
	s = settings()
	return {
		"enabled": bool(s.enabled),
		"configured": s.provider in (LOCAL, CUSTOM) or bool(s.api_key),
		"provider": s.provider,
		"model": s.model,
		"can_configure": "System Manager" in frappe.get_roles(),
	}


@frappe.whitelist()
def help_answer(query):
	"""Help mode: instant answer, no AI involved."""
	from erp_ai_assistant.help import answer

	return answer((query or "")[:500])


@frappe.whitelist()
def send_message(message, conversation_id=None):
	message = (message or "").strip()
	if not message:
		frappe.throw("Please type a message.")
	status = get_status()
	if not (status["enabled"] and status["configured"]):
		frappe.throw("The AI assistant is not set up yet. Ask a System Manager to fill AI Assistant Settings.")
	conversation_id = conversation_id or frappe.generate_hash(length=12)
	run_id = frappe.generate_hash(length=10)
	frappe.enqueue(
		"erp_ai_assistant.agent.run",
		queue="long",
		timeout=1800,
		conversation_id=conversation_id,
		message=message[:8000],
		run_id=run_id,
	)
	return {"conversation_id": conversation_id, "run_id": run_id}


@frappe.whitelist()
def send(message, conversation_id=None, mode="auto"):
	"""Unified entrypoint: seamlessly blends instant Help Guide and AI Agent."""
	mode = mode or "auto"
	message = (message or "").strip()
	if not message:
		frappe.throw("Please type a message.")

	conversation_id = conversation_id or frappe.generate_hash(length=12)

	if mode == "auto":
		from erp_ai_assistant.help import answer, find_doctype, is_action_intent

		if is_action_intent(message):
			target = "agent"
		else:
			ans = answer(message[:500])
			if ans.get("is_fallback"):
				status = get_status()
				if status["enabled"] and status["configured"]:
					target = "agent"
				else:
					return {"source": "help", "conversation_id": conversation_id, "data": ans}
			else:
				dt = find_doctype(message)
				if dt:
					sugg = ans.get("suggestions") or []
					action_chip = f"⚡ Create {dt} with AI"
					if action_chip not in sugg:
						ans["suggestions"] = [action_chip] + sugg
				return {"source": "help", "conversation_id": conversation_id, "data": ans}

	elif mode == "help":
		from erp_ai_assistant.help import answer, find_doctype

		ans = answer(message[:500])
		dt = find_doctype(message)
		if dt:
			sugg = ans.get("suggestions") or []
			action_chip = f"⚡ Create {dt} with AI"
			if action_chip not in sugg:
				ans["suggestions"] = [action_chip] + sugg
		return {"source": "help", "conversation_id": conversation_id, "data": ans}

	else:
		target = "agent"

	res = send_message(message, conversation_id=conversation_id)
	return {"source": "agent", "conversation_id": res["conversation_id"], "run_id": res["run_id"]}


@frappe.whitelist()
def rebuild_manual():
	frappe.only_for("System Manager")
	from erp_ai_assistant.manual import schedule_full_rebuild

	schedule_full_rebuild()
	return True


@frappe.whitelist()
def manual_stats():
	return {
		"manuals": frappe.db.count("ERP Help Article", {"article_type": "DocType Manual"}),
		"customized": frappe.db.count("ERP Help Article", {"article_type": "DocType Manual", "is_custom": 1}),
		"sops": frappe.db.count("ERP Help Article", {"article_type": ["!=", "DocType Manual"]}),
		"last_built": frappe.db.get_value("ERP Help Article", {"article_type": "DocType Manual"}, "max(last_built)"),
	}


@frappe.whitelist()
def cancel_run(run_id):
	"""Ask a running turn to stop. The key is per user, so a user can only stop their own runs."""
	if run_id:
		frappe.cache.set_value(cancel_key(frappe.session.user, run_id), 1, expires_in_sec=3600)
	return True


@frappe.whitelist()
def reset_conversation(conversation_id, run_id=None):
	cancel_run(run_id)
	frappe.cache.delete_value(cache_key(frappe.session.user, conversation_id))
	return True
