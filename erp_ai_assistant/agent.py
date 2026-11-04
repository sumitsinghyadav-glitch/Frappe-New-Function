"""Agent loop: the model decides which ERPNext tools to call; we run them as the user and feed results back.
Runs as a background job and streams progress to the user's browser over realtime events.

Two back-ends:
- Anthropic (Claude) through the Anthropic SDK
- Any OpenAI-compatible server through the OpenAI SDK: local Ollama (free, no key), Google Gemini,
  Groq, OpenRouter, OpenAI."""

import json
import re

import frappe
from frappe.utils import nowdate

from erp_ai_assistant.tools import TOOLS, WRITE_TOOLS, run_tool

EVENT = "erp_ai_assistant"
HISTORY_TTL = 6 * 60 * 60

LOCAL = "Free - Local AI (Ollama)"
ANTHROPIC = "Anthropic (Claude)"
PROVIDERS = {
	# provider: (default base_url, default model)
	LOCAL: ("http://erp-ollama:11434/v1", "qwen3:4b-instruct"),
	"Google Gemini (free API key)": ("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-flash-lite-latest"),
	"Groq (free API key)": ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
	"OpenRouter (free models)": ("https://openrouter.ai/api/v1", "openrouter/auto"),
	"OpenAI (ChatGPT)": ("https://api.openai.com/v1", "gpt-4.1-mini"),
	ANTHROPIC: (None, "claude-opus-5-5"),
}
CUSTOM = "Custom (any OpenAI-compatible API)"
PROVIDERS[CUSTOM] = (None, None)  # server URL and model come from the settings

SYSTEM_PROMPT = """You are Simple AI, the assistant built into this company's ERPNext v16 system (with India Compliance and Frappe HR).
Users give you commands in English or Hindi; you carry them out by calling tools, then report what you did.

How to work:
- Buying or selling requests (purchase/sales order, receipt/delivery, invoice, payment): call purchase_flow or sales_flow
  directly as your FIRST action. Do not search first: these tools match supplier, customer, item, warehouse and company names themselves.
  Pass names, items and quantities as the user wrote them, and 'upto' = every step the user asked for
  (e.g. "make a PO, receive it and make the invoice" -> upto "order+receipt+invoice").
  For follow-ups on a document that already exists ("now receive PUR-ORD-2026-00011"), pass continue_from with its name.
  If the tool returns an error with suggestions, call it again with the suggested name, or ask the user.
- Moving stock between warehouses: call stock_transfer directly as your first action.
- Questions about stock: call get_stock_balance with the item name as the user wrote it.
- For other documents, find masters with search_records first and use only names you actually found.
  If a master is missing or several match and the choice matters, ask the user instead of guessing,
  and do not create new masters unless the user asks you to.
- If you are unsure about a doctype's fields, call get_doctype_schema first.
- Build downstream documents with make_mapped_document from the submitted source (PO -> Purchase Receipt -> Purchase Invoice,
  SO -> Delivery Note -> Sales Invoice, invoice -> Payment Entry). Never re-type a downstream document by hand: the mapping keeps links and pending quantities.
- Documents are created as Draft. Submit only when the user asked to submit/post/complete, or asked for a multi-step flow,
  because each next step needs its source submitted. A single "create X" request stays Draft.
- When a tool returns an error, read it, fix the input and retry. If it needs information only the user has, ask.
- Dates are YYYY-MM-DD. Today is {today}. Default company: {company}.
- For Indian GST, pick the tax template that matches the case (In-state vs Out-state) for the company, when the user wants taxes.
- Never delete or cancel anything; you have no tools for that.

When finished, reply briefly: one line per document with a markdown link [NAME](url) using the url returned by the tool,
its state (Draft/Submitted) and grand total, then anything the user should check. Reply in the user's language.
{extra}"""

def openai_tools(names=None):
	return [
		{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["input_schema"]}}
		for t in TOOLS
		if names is None or t["name"] in names
	]


# Small local models choose better from a short list; the one-call flows cover buying and selling.
LOCAL_TOOL_NAMES = {"purchase_flow", "sales_flow", "get_stock_balance", "search_records", "get_document"}


class AgentStop(Exception):
	"""Ends the turn with a message for the user (bad key, rate limit, ...)."""


def settings():
	s = frappe.get_cached_doc("AI Assistant Settings")
	provider = s.provider or LOCAL
	default_url, default_model = PROVIDERS.get(provider, PROVIDERS[LOCAL])
	model = (s.model or "").strip()
	if not model or (provider != ANTHROPIC and model.startswith("claude-")):
		model = default_model
	fallbacks = [m.strip() for m in (s.get("fallback_models") or "").splitlines() if m.strip() and m.strip() != model]
	return frappe._dict(
		provider=provider,
		model=model,
		base_url=(s.base_url or "").strip() or default_url,
		api_key=s.get_password("api_key", raise_exception=False),
		effort=s.effort or "medium",
		max_steps=s.max_steps or 30,
		instructions=s.instructions,
		enabled=s.enabled,
		fallback_models=fallbacks,
		timeout=s.get("request_timeout") or 25,
		reasoning=s.get("reasoning_effort") or "Low",
		all_tools=(s.get("tool_set") or "").startswith("All"),
		local_fallback=bool(s.get("use_local_fallback", 1)),
	)


def cache_key(user, conversation_id):
	return f"erp_ai_assistant:{user}:{conversation_id}"


def cancel_key(user, run_id):
	return f"erp_ai_assistant:cancel:{user}:{run_id}"


class Cancelled(Exception):
	"""The user pressed Stop; end the turn at the next safe point."""


def publish(user, conversation_id, kind, **data):
	frappe.publish_realtime(EVENT, {"conversation_id": conversation_id, "type": kind, **data}, user=user)


def describe_step(name, args):
	if name in ("purchase_flow", "sales_flow"):
		party = args.get("supplier") or args.get("customer")
		kind = "Purchase" if name == "purchase_flow" else "Sales"
		return f"{kind} flow for {party} up to {args.get('upto')}"
	if name == "search_records":
		return f"Searching {args.get('doctype')}" + (f" for “{args.get('search_text')}”" if args.get("search_text") else "")
	if name == "get_doctype_schema":
		return f"Reading {args.get('doctype')} fields"
	if name == "get_document":
		return f"Reading {args.get('doctype')} {args.get('name')}"
	if name == "get_stock_balance":
		return f"Checking stock of {args.get('item_code')}"
	if name == "create_document":
		return f"Creating {(args.get('doc') or {}).get('doctype', 'document')}"
	if name == "make_mapped_document":
		return f"Making {args.get('target_doctype')} from {args.get('source_doctype')} {args.get('source_name')}"
	if name == "update_document":
		return f"Updating {args.get('doctype')} {args.get('name')}"
	if name == "submit_document":
		return f"Submitting {args.get('doctype')} {args.get('name')}"
	return name


class Turn:
	"""Runs tool calls for one user message and reports progress."""

	def __init__(self, user, conversation_id, max_steps, run_id=None):
		self.user, self.conversation_id, self.max_steps, self.run_id = user, conversation_id, max_steps, run_id
		self.steps = 0
		self.created = []
		self.cancelled = False

	def check(self):
		# exists() reads Redis directly; get_value() could return a value cached earlier in this process
		if self.run_id and frappe.cache.exists(cancel_key(self.user, self.run_id)):
			raise Cancelled

	def tool(self, name, args):
		self.check()
		self.steps += 1
		if not isinstance(args, dict):
			args = {}
		self.publish("step", text=describe_step(name, args))
		if self.steps > self.max_steps:
			return json.dumps({"error": "Step limit reached; stop and report progress."}), True
		out, is_error, summary = run_tool(name, args)
		if summary and "documents" in summary:
			for d in summary["documents"]:
				self.created.append(d)
				self.publish("doc", doc=d, action=name)
			if summary.get("error"):
				self.publish("step", text="↳ " + summary["error"][:200], error=1)
		elif summary:
			self.created.append(summary)
			self.publish("doc", doc=summary, action=name)
		elif is_error and name in WRITE_TOOLS:
			self.publish("step", text="↳ " + json.loads(out).get("error", "")[:200], error=1)
		return out, is_error

	def publish(self, kind, **data):
		publish(self.user, self.conversation_id, kind, run_id=self.run_id, **data)


def run(conversation_id, message, run_id=None):
	user = frappe.session.user
	turn = None
	try:
		final, turn = _run(user, conversation_id, message, run_id)
		# Models sometimes prefix links with an invented domain; keep them pointing at this ERP.
		final = re.sub(r"https?://[^\s/()\]]+(/app/[^\s)]*)", r"\1", final or "")
		if not turn.cancelled:
			turn.publish("done", text=final)
	except AgentStop as e:
		publish(user, conversation_id, "error", run_id=run_id, text=str(e))
	except Exception:
		frappe.log_error(title="ERP AI Assistant")
		publish(user, conversation_id, "error", run_id=run_id, text="Something went wrong. Details are in the Error Log.")
	finally:
		if run_id:
			frappe.cache.delete_value(cancel_key(user, run_id))


def _run(user, conversation_id, message, run_id=None):
	s = settings()
	system = SYSTEM_PROMPT.format(
		today=nowdate(),
		company=frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company") or "not set",
		extra=("\nCompany instructions:\n" + s.instructions) if s.instructions else "",
	)
	key = cache_key(user, conversation_id)
	saved = frappe.cache.get_value(key) or {}
	history = saved.get("messages", []) if saved.get("provider") == (s.provider, s.model) else []
	before = len(history)
	history.append({"role": "user", "content": message})
	turn = Turn(user, conversation_id, s.max_steps, run_id)

	try:
		turn.check()
		if s.provider == ANTHROPIC:
			final = run_anthropic(s, system, history, turn)
		else:
			final = run_openai_compatible(s, system, history, turn)
	except Cancelled:
		made = ", ".join(f"{d['doctype']} {d['name']} ({d['state']})" for d in turn.created)
		final = "Stopped by the user." + (f" Documents already created: {made}." if made else " Nothing was created.")
		# Drop this turn's half-finished tool exchange so the next message starts from a valid history.
		history[before:] = [{"role": "user", "content": message}, {"role": "assistant", "content": final}]
		turn.cancelled = True
		turn.publish("cancelled", text=final)

	frappe.cache.set_value(key, {"provider": (s.provider, s.model), "messages": history}, expires_in_sec=HISTORY_TTL)
	return final, turn


# ------------------------------------------------------------------ Anthropic (Claude)
def run_anthropic(s, system, history, turn):
	import anthropic

	if not s.api_key:
		raise AgentStop("Add an Anthropic API key in AI Assistant Settings, or switch the provider to Free - Local AI.")
	client = anthropic.Anthropic(api_key=s.api_key, timeout=300, max_retries=2)
	while True:
		turn.check()
		try:
			response = client.beta.messages.create(
				model=s.model,
				max_tokens=16000,
				system=system,
				tools=TOOLS,
				messages=history,
				output_config={"effort": s.effort},
				betas=["server-side-fallback-2026-07-01"],
				fallbacks="default",
			)
		except anthropic.AuthenticationError:
			raise AgentStop("The Anthropic API key in AI Assistant Settings is not valid.")
		except anthropic.PermissionDeniedError:
			raise AgentStop("The Anthropic API key does not have access to this model.")
		except anthropic.NotFoundError:
			raise AgentStop(f"Model {s.model} was not found. Check AI Assistant Settings.")
		except anthropic.RateLimitError:
			raise AgentStop("The AI service is busy (rate limited). Please try again in a minute.")
		except anthropic.APIStatusError as e:
			frappe.log_error(title="ERP AI Assistant API error", message=str(e))
			raise AgentStop(f"The AI service returned an error ({e.status_code}). Please try again.")
		except anthropic.APIConnectionError:
			raise AgentStop("Could not reach the AI service. Check the server's internet connection.")

		history.append({"role": "assistant", "content": [b.model_dump(by_alias=True, exclude_none=True) for b in response.content]})
		text = "\n".join(b.text for b in response.content if b.type == "text").strip()

		if response.stop_reason == "refusal":
			return "I can't help with that request."
		if response.stop_reason == "pause_turn":
			continue
		if response.stop_reason != "tool_use":
			return (text or "Done.") + ("\n\n_(Reply was cut short.)_" if response.stop_reason == "max_tokens" else "")

		if text:
			turn.publish("note", text=text)
		results = []
		for block in response.content:
			if block.type == "tool_use":
				out, is_error = turn.tool(block.name, block.input)
				results.append({"type": "tool_result", "tool_use_id": block.id, "content": out, "is_error": is_error})
		history.append({"role": "user", "content": results})


# ------------------------------------------------------------------ OpenAI-compatible (Ollama, Gemini, Groq, OpenRouter, OpenAI)
THINK_RE = re.compile(r"<think>.*?</think>", re.S)
PROMISE_RE = re.compile(r"\b(let me|i will|i'll|i need to|next,? i|now,? i)\b[^.?!]*[.:]?\s*$", re.I)


GEMINI = "Google Gemini (free API key)"
# Free-tier models get overloaded at times; on 429/5xx/timeout the next one is tried, so a busy model never blocks you.
FALLBACK_MODELS = {GEMINI: ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-flash-latest"]}
CLOUD_TIMEOUT = 25


def strip_signatures(history):
	"""Thought signatures are tied to the model that made them; drop them before switching models."""
	for m in history:
		for tc in m.get("tool_calls") or []:
			tc.pop("extra_content", None)
		m.pop("extra_content", None)


def local_ai_available():
	import socket

	try:
		socket.create_connection(("erp-ollama", 11434), timeout=1).close()
		return True
	except OSError:
		return False


class ModelRouter:
	"""Calls the configured model, falling back to the next free model when one is busy or down."""

	def __init__(self, s, turn):
		import openai

		self.openai, self.turn, self.provider = openai, turn, s.provider
		self.candidates = []  # (label, client, model, extra kwargs)
		if s.provider != LOCAL:
			if not s.base_url or not s.model:
				raise AgentStop("Fill Server URL and Model in AI Assistant Settings for the custom provider.")
			client = openai.OpenAI(base_url=s.base_url, api_key=s.api_key or "none", timeout=s.timeout or CLOUD_TIMEOUT, max_retries=0)
			effort = (s.reasoning or "").lower()
			extra = {"reasoning_effort": effort} if effort in ("low", "medium", "high") and s.provider != "Groq (free API key)" else {}
			fallbacks = s.fallback_models or FALLBACK_MODELS.get(s.provider, [])
			for model in [s.model, *[m for m in fallbacks if m != s.model]]:
				self.candidates.append((s.provider, client, model, dict(extra)))
		if s.provider == LOCAL or (s.local_fallback and local_ai_available()):
			local_url, local_model = PROVIDERS[LOCAL]
			model = s.model if s.provider == LOCAL else local_model
			client = openai.OpenAI(base_url=s.base_url if s.provider == LOCAL else local_url, api_key="local", timeout=600, max_retries=0)
			self.candidates.append((LOCAL, client, model, {}))
		self.current = 0
		self.signatures_ok = True

	@property
	def label(self):
		return self.candidates[self.current][2]

	def create(self, system, history, tools):
		openai = self.openai
		last_error = None
		while self.current < len(self.candidates):
			provider, client, model, extra = self.candidates[self.current]
			sys_text = system + ("\n/no_think" if provider == LOCAL and model.startswith("qwen3") else "")
			try:
				return client.chat.completions.create(
					model=model,
					messages=[{"role": "system", "content": sys_text}, *history],
					tools=tools,
					temperature=0.1,
					**extra,
				)
			except openai.AuthenticationError:
				raise AgentStop(f"The API key for {provider} is not valid. Update it in AI Assistant Settings.")
			except openai.BadRequestError as e:
				if "reasoning" in str(e).lower() and extra.get("reasoning_effort"):
					extra.pop("reasoning_effort")  # this model does not support reasoning effort; retry without it
					continue
				if "thought" in str(e).lower() and self.signatures_ok:
					strip_signatures(history)
					self.signatures_ok = False
					continue
				frappe.log_error(title="ERP AI Assistant API error", message=str(e))
				raise AgentStop(f"{provider} rejected the request ({e.status_code}).")
			except (openai.RateLimitError, openai.NotFoundError, openai.InternalServerError, openai.APIConnectionError, openai.APIStatusError) as e:
				last_error = e
			# move on to the next model
			self.current += 1
			strip_signatures(history)
			if self.current < len(self.candidates):
				nxt = self.candidates[self.current]
				self.turn.publish("step", text=f"{model} is busy; switching to {nxt[2]}")
		if isinstance(last_error, openai.RateLimitError):
			raise AgentStop(f"{self.provider} daily/minute limit reached. Try again later.")
		raise AgentStop(f"Could not reach any AI model ({last_error.__class__.__name__ if last_error else 'no model'}). Check the internet connection.")


# The agent sees a short tool list: fewer choices = faster, more reliable decisions.
FAST_TOOL_NAMES = {
	"purchase_flow", "sales_flow", "stock_transfer", "get_stock_balance", "search_records", "get_document",
	"create_document", "make_mapped_document", "submit_document",
}


def run_openai_compatible(s, system, history, turn):
	if s.provider not in (LOCAL, CUSTOM) and not s.api_key:
		raise AgentStop(f"Add the API key for {s.provider} in AI Assistant Settings, or switch the provider to Free - Local AI.")
	router = ModelRouter(s, turn)
	tools = openai_tools(None if s.all_tools else FAST_TOOL_NAMES)
	nudged = False

	while True:
		turn.check()
		response = router.create(system, history, tools)

		msg = response.choices[0].message
		text = THINK_RE.sub("", msg.content or "").strip()
		# Keep the message as returned: Gemini attaches thought signatures (extra fields on tool calls)
		# that must be sent back unchanged with the next request.
		entry = msg.model_dump(exclude_none=True)
		entry["role"], entry["content"] = "assistant", text
		for tc in entry.get("tool_calls") or []:
			tc["function"]["arguments"] = tc["function"].get("arguments") or "{}"
		history.append(entry)

		if not msg.tool_calls:
			# Small models sometimes announce the next step instead of taking it; nudge once.
			if not nudged and PROMISE_RE.search(text[-300:]):
				nudged = True
				history.append({"role": "user", "content": "Continue: make the tool call now instead of describing it."})
				continue
			return text or "Done."
		if text:
			turn.publish("note", text=text)
		flow_results = []
		for tc in msg.tool_calls:
			try:
				args = json.loads(tc.function.arguments or "{}")
				out, is_error = turn.tool(tc.function.name, args)
			except ValueError:
				out, is_error = json.dumps({"error": "Arguments were not valid JSON. Send the tool call again with valid JSON."}), True
			history.append({"role": "tool", "tool_call_id": tc.id, "content": out})
			flow_results.append((tc.function.name, out, is_error))

		# A one-call flow that fully succeeded needs no second model call: we already know what was made.
		# This saves a whole round trip (several seconds on free tiers).
		summary = flow_summary(flow_results)
		if summary:
			history.append({"role": "assistant", "content": summary})
			return summary


ONE_CALL_FLOWS = {"purchase_flow", "sales_flow", "stock_transfer"}


def flow_summary(results):
	if not results or any(name not in ONE_CALL_FLOWS or err for name, _, err in results):
		return None
	lines = []
	for _, out, _ in results:
		data = json.loads(out)
		if data.get("error") or not data.get("documents"):
			return None  # let the model read the error and fix or explain it
		for d in data["documents"]:
			total = f" · ₹{d['grand_total']:,.2f}" if d.get("grand_total") else ""
			lines.append(f"- [{d['doctype']} {d['name']}]({d['url']}): **{d['state']}**{total}")
	return "Done ✅\n\n" + "\n".join(lines)
