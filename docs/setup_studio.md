# Local Setup – Edge Case Suggester & Pipeline Graphs

This guide shows your teammates how to spin up LangGraph **Studio** locally so they can run and iterate on the two graphs that live in this repository:

* `edge_case_suggester` – mini-graph for generating tricky test cases.
* `pipeline_graph`      – full end-to-end task-creation pipeline.

## 1. Prerequisites

* Python 3.11 (matching the `python_version` in `langgraph.json`).
* Git access to this repo.
* API keys for the LLM providers you want to use:
  * `OPENAI_API_KEY` – required (GPT-4o, GPT-4-turbo …)
  * `ANTHROPIC_API_KEY` – only if you plan to run the full pipeline (Claude Opus).
* (macOS) Xcode command-line tools installed – required by some Python deps.

## 2. Clone & create a virtual environment

```bash
# Clone
$ git clone <repo-url> pg_agent
$ cd pg_agent

# Create and activate venv (choose tool you prefer)
$ python3.11 -m venv .venv
$ source .venv/bin/activate  # on Windows use .venv\Scripts\activate
```

## 3. Install dependencies

```bash
# Core libs + extras required by LangGraph Studio
(venv) $ pip install -e .
(venv) $ pip install "langgraph[server]"    # brings in langgraph-cli & Studio UI
```

## 4. Add your environment variables

Create a file named `.env` at the repo root (it’s already referenced in
`langgraph.json`).  Example:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...   # optional, only for full pipeline
```

> ℹ️  Studio automatically loads this `.env` when it starts.

## 5. Launch LangGraph Studio

```bash
(venv) $ langgraph dev
```

• The CLI discovers the graphs specified in `langgraph.json` and serves Studio
  on <http://localhost:8000> (printed in the console).
• In the **left sidebar** you’ll see both `edge_case_suggester` and
  `pipeline_graph`.  Pick one to open its visual diagram.

## 6. Running the graphs

1. Click **“Run”** (▶) to start a new thread.  For `edge_case_suggester`, paste
   a Markdown problem statement under the `problem_spec` key when prompted, or
   leave the state blank to let the graph pick random topics and generate a
   problem itself.
2. When execution pauses at **HumanFeedback** you’ll see a *Resume* box.
   • Leave it blank and hit **Resume** to accept the list.
   • Or type guidance (e.g. `include ±2 cases`) and resume to loop.
3. The **State** pane shows every checkpoint so you can time-travel or fork.

## 7. Updating dependencies

If the repo requirements change, run:

```bash
(venv) $ pip install -e . -U
```

## 8. Common troubleshooting

| Symptom                                   | Fix                                          |
|-------------------------------------------|-----------------------------------------------|
| No *Resume* box in Studio                 | Ensure Studio started via `langgraph dev` so it compiles with the checkpointer declared in code (`MemorySaver`). |
| `OPENAI_API_KEY` errors                   | Check your `.env` file is at repo root and keys are valid. |
| Ports already in use                      | `langgraph dev --port 9000` to choose another. |

Happy testing!  Reach out in `#pg-agent` Slack channel if you hit issues.
