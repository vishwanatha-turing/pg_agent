# LangGraph Studio – Competitive Programming Problem Generator

This repository contains a LangGraph pipeline that automatically **creates, solves, and validates competitive-programming problems**.  The pipeline lives inside the `studio/` folder and can be explored interactively with **LangGraph Studio**.

---
## 1 . Prerequisites

• Python 3.10 + (the code is tested with 3.12)  
• A terminal with `pip` available  
• API keys for the LLM providers you wish to use (e.g. OpenAI, Anthropic).

> **Tip:** You do **not** need to install LangChain or LangGraph globally. They are listed in `studio/requirements.txt` and will be installed in the next step.

---
## 2 . Setup

```bash
# 1. Clone the repo (skip if you already have it)
# git clone https://github.com/<your-org>/pg_agent.git
cd pg_agent

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install the pipeline dependencies
pip install -r studio/requirements.txt

# 4. Provide your API keys (OpenAI, Anthropic, etc.)
cp studio/.env.example .env        # optional helper file, if present
# then edit .env and fill in the keys, e.g.
# OPENAI_API_KEY="sk-..."
# ANTHROPIC_API_KEY="sk-anthropic-..."
```

---
## 3 . Launching LangGraph Studio

```bash

# Quick dev server (hot-reload):
cd studio
langgraph dev 
```

This will start a local web server on `http://localhost:8000/` (the exact port is shown in the terminal). Open the URL in your browser to:

* Visualise the full pipeline graph
* Inspect node inputs/outputs
* Execute the pipeline end-to-end or step-by-step
* Monitor the conversation state live

> **Note:** The first run may take a little longer because the LLMs have to spin up.

---
## 4 . Command-line Quick-start (without Studio)

If you just want to run the pipeline headless:

```bash
python studio/pipeline_graph.py  # invokes test_pipeline() at the bottom of the file
```

---
## 5 . Folder Structure (high-level)

```
pg_agent/
├─ studio/                # All LangGraph code lives here
│  ├─ pipeline_graph.py   # 🧠 Main pipeline definition
│  ├─ topic_selector.py   # 🔍 Picks a random algorithmic topic
│  ├─ problem_statement_generator.py
│  ├─ test_case_generator.py
│  ├─ solution_generator.py
│  └─ ...
├─ Data Requirements Document ...pdf  # reference paper – not needed for running
└─ README.md              # (this file)
```

---
## 6 . Troubleshooting

| Symptom | Fix |
|---------|------|
| `ModuleNotFoundError` for LangGraph / LangChain | Check that you installed dependencies from **studio/requirements.txt** inside the active virtualenv. |
| Browser shows blank Studio page | Verify the terminal shows `Uvicorn running on ...` and nothing crashed. Refresh. |
| "401 / 403" from provider | Double-check `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. |

---
## 7 . Contributing

PRs are welcome! Please open an issue first to discuss changes.

---
## 8 . License

MIT © 2024 