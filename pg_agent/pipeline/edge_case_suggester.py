"""Edge Case Suggester – a standalone LangGraph mini-pipeline that
extracts input constraints from a problem statement and then proposes
up to 25 diverse edge-case inputs.

This module intentionally has **no** dependencies on the main build
pipeline.  It simply exposes a compiled `graph` variable so callers can
do:

    from pg_agent.pipeline.edge_case_suggester import graph
    result = graph.invoke({"problem_spec": md_text})

or run from the CLI:

    python -m pg_agent.pipeline.edge_case_suggester path/to/problem.md
"""

from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from pg_agent.prompts.edge_case_suggester import (
    PARSE_CONSTRAINTS_PROMPT,
    EDGE_CASE_GENERATOR_PROMPT,
)
from pg_agent.pipeline.problem_statement_generator import problem_generator_node
from pg_agent.pipeline.topic_selector import topic_selector_node

# Ensure env vars such as OPENAI_API_KEY are loaded if a .env file exists.
load_dotenv()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_llm(temperature: float = 0.0):
    """Return a `ChatOpenAI` instance with the given *temperature*."""
    return ChatOpenAI(model="gpt-4o", temperature=temperature)


# Build runnable chains once at import time so they can be reused.
parse_chain = (
    ChatPromptTemplate.from_messages(
        [
            ("system", PARSE_CONSTRAINTS_PROMPT),
            ("human", "{input}"),
        ]
    )
    | _get_llm()
)

edge_case_chain = (
    ChatPromptTemplate.from_messages(
        [
            ("system", EDGE_CASE_GENERATOR_PROMPT),
            ("human", "{input}"),
        ]
    )
    | _get_llm()
)

# ---------------------------------------------------------------------------
# Node definitions
# ---------------------------------------------------------------------------


def parse_constraints(state: dict) -> dict:
    """LLM call: turn *problem_spec* Markdown into JSON of constraints."""
    problem_spec = state.get("problem_spec")
    if problem_spec is None:
        raise ValueError(
            "Edge Case Suggester: 'problem_spec' key missing in state. Pass it when invoking the graph, e.g. graph.compile().invoke({'problem_spec': md_text})."
        )

    result = parse_chain.invoke({"input": problem_spec})
    return {**state, "constraints": result.content}


def edge_case_generator(state: dict) -> dict:
    """LLM call: turn JSON constraints into a list of edge-case inputs."""
    constraints = state.get("constraints")
    if constraints is None:
        raise ValueError("Edge Case Suggester: 'constraints' missing from state")

    result = edge_case_chain.invoke({"input": constraints})

    # Parse the LLM output, tolerating minor format issues.
    try:
        parsed = json.loads(result.content)
    except json.JSONDecodeError:
        # Fall back to returning the raw string as a single element list.
        parsed = [result.content]

    # Dedupe + cap at 25 items (requirement of the original prompt).
    if isinstance(parsed, list):
        parsed = list({json.dumps(x, sort_keys=True): x for x in parsed}.values())[:25]

    return {**state, "edge_cases": parsed}


# ---------------------------------------------------------------------------
# Bridge node – ensures we have `problem_spec` in state
# ---------------------------------------------------------------------------


def _ensure_problem_spec(state: dict) -> dict:
    """Ensure `problem_spec` exists.

    1. If already present, pass through unchanged.
    2. Else, attempt to use an existing `problem_statement` value.
    3. Else, fall back to `problem_generator_node` to create one from `topics`.
    """

    if state.get("problem_spec") is not None:
        return state

    # If problem_statement already generated, reuse it.
    if "problem_statement" in state:
        return {**state, "problem_spec": state["problem_statement"]}

    # Otherwise delegate to the existing problem generator node (requires topics).
    generated = problem_generator_node(state)
    problem_statement = generated["problem_statement"]
    return {**state, **generated, "problem_spec": problem_statement}


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

builder = StateGraph(dict)

# Nodes
builder.add_node("TopicSelector", topic_selector_node)
builder.add_node("ProblemGenerator", _ensure_problem_spec)
builder.add_node("ParseConstraints", parse_constraints)
builder.add_node("EdgeCaseGenerator", edge_case_generator)

# Wiring
builder.set_entry_point("TopicSelector")
builder.add_edge("TopicSelector", "ProblemGenerator")
builder.add_edge("ProblemGenerator", "ParseConstraints")
builder.add_edge("ParseConstraints", "EdgeCaseGenerator")
builder.add_edge("EdgeCaseGenerator", END)

# Expose the *StateGraph* (not compiled) so that LangGraph Studio / dev server
# can discover and compile it automatically when running `langgraph dev`.
graph = builder

# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python -m pg_agent.pipeline.edge_case_suggester <path_to_problem.md>"
        )
        raise SystemExit(1)

    input_md = Path(sys.argv[1])
    if not input_md.exists():
        print(f"Error: File not found – {input_md}")
        raise SystemExit(1)

    problem_text = input_md.read_text(encoding="utf-8")

    compiled = graph.compile()
    final_state = compiled.invoke({"problem_spec": problem_text})
    print(json.dumps(final_state["edge_cases"], indent=2))
