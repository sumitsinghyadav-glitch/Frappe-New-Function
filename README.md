# Simple AI for ERPNext

A chat assistant inside the ERPNext desk. After installing it, a chat button appears in the bottom-right corner of every page.

It has three modes:

| Mode | What it does | Needs an AI key? |
|---|---|---|
| 💡 **Help Guide** | Instant answers about ERPNext: step-by-step processes, what a field means, where to find a screen, common errors and their fixes, current stock. Works offline. | No |
| 🤖 **AI Agent** | Does the work for you. Type a command such as *"Create a purchase order for 10 Steel Pipes from Summit Traders, then receive it and make the invoice"*. It looks up your masters and creates (and, when asked, submits) the documents using ERPNext's standard mappings. | Yes |
| ⚡ **Both (Auto)** | Questions go to the Help Guide, commands go to the AI Agent. | For commands only |

Commands can be in English or Hindi.

## Requirements

- Frappe / ERPNext **v16**
- Optional: India Compliance and Frappe HR. The Help Guide covers them when they are installed.

## Install

From your bench folder:

```bash
bench get-app https://github.com/sumitsinghyadav-glitch/Frappe-New-Function.git
bench --site <your-site> install-app erp_ai_assistant
bench build --app erp_ai_assistant
bench restart
```

Then reload the browser (Ctrl+Shift+R). The **Simple AI** button appears in the bottom-right corner.
### Install on frappe_docker

Add the app to your custom image. For example, add these lines to your Dockerfile:

```dockerfile
FROM <your-erpnext-image>
RUN cd /home/frappe/frappe-bench \
 && git clone --depth 1 https://github.com/sumitsinghyadav-glitch/Frappe-New-Function.git apps/erp_ai_assistant \
 && env/bin/pip install --no-cache-dir -e apps/erp_ai_assistant \
 && ln -sfn /home/frappe/frappe-bench/apps/erp_ai_assistant/erp_ai_assistant/public sites/assets/erp_ai_assistant \
 && (grep -qx erp_ai_assistant sites/apps.txt || echo erp_ai_assistant >> sites/apps.txt)
```

Rebuild the image and recreate the containers. Then run once inside the backend container:

```bash
bench --site <your-site> install-app erp_ai_assistant
```

## Set up the AI Agent (optional)

The Help Guide works right after installing. The AI Agent needs an AI provider:

1. Open **AI Assistant Settings** (search for it in the awesome bar).
2. Choose an **AI Provider**:
   - Google Gemini (free API key)
   - Groq (free API key)
   - OpenRouter (free models)
   - OpenAI (ChatGPT)
   - Anthropic (Claude)
   - Free - Local AI (Ollama), which runs on your own server
   - Custom (any OpenAI-compatible API)
3. Paste the **API Key**, then fill **Model** and **Server URL** if your provider needs them.
4. Tick **Enabled** and save.

**Company Instructions** in the same settings lets you add your own rules, for example "always use warehouse Stores".

## Company SOPs in the Help Guide

Add your own guides as **ERP Help Article** records (type *Company SOP*). The Help Guide searches them together with its built-in knowledge.

## Notes

- The AI Agent works with the logged-in user's permissions. It can only create or submit what that user is allowed to.
- API keys are stored in a Password field, so they are saved encrypted and never sent to the browser.

## License

MIT
