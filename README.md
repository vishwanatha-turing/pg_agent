# LangGraph Studio – Competitive Programming Problem Generator

This repository contains a LangGraph pipeline that automatically **creates, solves, and validates competitive-programming problems**.  The code now lives inside an installable Python package (`pg_agent/`).  You can still explore it visually with **LangGraph Studio**, but you no longer need the legacy `studio/` folder.

---
## 1 . Prerequisites

• Python 3.11 or higher (the code is tested with 3.12)
• A terminal with `pip` available  
• API keys for the LLM providers you wish to use (e.g. OpenAI, Anthropic).

> **Tip:** You do **not** need to install LangChain or LangGraph globally. Everything is declared in the root-level `requirements.txt` (or `pyproject.toml`) and will be installed in the next step.

---
## 2 . Setup

```bash
# 1. Clone the repo (skip if you already have it)
# git clone https://github.com/<your-org>/pg_agent.git
cd pg_agent

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install the pipeline dependencies (editable install recommended for dev)
pip install -r requirements.txt        # or:  pip install -e .[dev]

# 4. Provide your API keys (OpenAI, Anthropic, etc.)
# If an `.env.example` file exists, copy it over and fill in your keys:
# cp .env.example .env
# then edit .env and fill in the keys, e.g.
# OPENAI_API_KEY="sk-..."
# ANTHROPIC_API_KEY="sk-anthropic-..."
```

---
## 3 . Launching LangGraph Studio

```bash
# First time only — install your *local* package in editable mode so Studio can
# import it as a proper Python package (no need to repeat after each change):
pip install -e .

# Quick dev server (hot-reload):
langgraph dev 
```

This will start a local web server on `http://localhost:2024/` (the exact port is shown in the terminal). Open the URL in your browser to:

* Visualise the full pipeline graph
* Inspect node inputs/outputs
* Execute the pipeline end-to-end or step-by-step
* Monitor the conversation state live

> **Note:** The first run may take a little longer because the LLMs have to spin up.

---
## 4 . Command-line Quick-start (without Studio)

If you just want to run the pipeline headless:

```bash
python -m pg_agent.pipeline.pipeline_graph   # runs __main__ section
python - <<'PY'
from pg_agent.pipeline import test_pipeline
print(test_pipeline().invoke({}))
PY
```

---
## 5 . Folder Structure (high-level)

```
pg_agent/
├─ pg_agent/                 # Installable package
│  ├─ pipeline/              # LangGraph nodes & graph
│  ├─ prompts/
│  └─ utils/
├─ tests/
├─ langgraph.json
├─ requirements.txt / pyproject.toml
└─ README.md
```

---
## 6 . Troubleshooting

| Symptom | Fix |
|---------|------|
| `ModuleNotFoundError` for LangGraph / LangChain | Check that you installed dependencies from **requirements.txt** inside the active virtualenv. |
| Browser shows blank Studio page | Verify the terminal shows `Uvicorn running on ...` and nothing crashed. Refresh. |
| "401 / 403" from provider | Double-check `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. |

---
## 7 . Contributing

PRs are welcome! Please open an issue first to discuss changes.

---
## 8 . License

MIT © 2024 