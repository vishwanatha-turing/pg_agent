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
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import uuid
from typing import Literal
from typing_extensions import TypedDict, Annotated
from operator import add

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
    return {"constraints": result.content}


def edge_case_generator(state: dict) -> dict:
    """LLM call -> returns edge_cases, takes into account reviewer feedback."""

    constraints = state.get("constraints")
    if constraints is None:
        raise ValueError("Edge Case Suggester: 'constraints' missing from state")

    # Merge constraints with optional reviewer feedback
    feedback = state.get("feedback")
    if feedback:
        input_text = f"{constraints}\n\nAdditional reviewer guidance:\n{feedback}"
    else:
        input_text = constraints

    result = edge_case_chain.invoke({"input": input_text})

    # Parse the LLM output, tolerating minor format issues.
    try:
        parsed = json.loads(result.content)
    except json.JSONDecodeError:
        # Fall back to returning the raw string as a single element list.
        parsed = [result.content]

    # Dedupe + cap at 25 items (requirement of the original prompt).
    if isinstance(parsed, list):
        parsed = list({json.dumps(x, sort_keys=True): x for x in parsed}.values())[:25]

    return {"edge_cases": parsed}


# ---------------------------------------------------------------------------
# Human feedback node
# ---------------------------------------------------------------------------


def human_feedback_node(state: dict) -> dict:
    """Pause execution and request reviewer input using LangGraph interrupt."""

    # If previous loop was accepted, exit immediately
    if state.get("accepted") is True:
        return {"accepted": True}

    edge_cases = state.get("edge_cases")

    # Prepare payload shown to human operator.
    payload = {
        "message": (
            "Review the generated edge cases below. "
            "Return an empty string to accept, or provide additional guidance "
            "to regenerate."
        ),
        "edge_cases": edge_cases,
    }

    # Pause execution. The returned dict comes from Command.resume when the run is resumed.
    response = interrupt(payload)  # type: ignore[arg-type]

    if isinstance(response, str):
        feedback = response.strip()
    elif isinstance(response, dict):
        feedback = str(response.get("data", "")).strip()
    else:
        feedback = str(response).strip()

    return {"feedback": feedback, "accepted": feedback == ""}


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
        return {"problem_spec": state["problem_statement"]}

    # Otherwise delegate to the existing problem generator node (requires topics).
    generated = problem_generator_node(state)
    problem_statement = generated["problem_statement"]
    return {**generated, "problem_spec": problem_statement}


# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------


class ECState(TypedDict, total=False):
    topics: list[str]
    problem_spec: str
    problem_statement: str
    constraints: str
    edge_cases: list
    feedback: str
    accepted: bool


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

builder = StateGraph(ECState)

# Nodes
builder.add_node("TopicSelector", topic_selector_node)
builder.add_node("ProblemGenerator", _ensure_problem_spec)
builder.add_node("ParseConstraints", parse_constraints)
builder.add_node("EdgeCaseGenerator", edge_case_generator)
builder.add_node("HumanFeedback", human_feedback_node)

# Wiring
builder.set_entry_point("TopicSelector")
builder.add_edge("TopicSelector", "ProblemGenerator")
builder.add_edge("ProblemGenerator", "ParseConstraints")
builder.add_edge("ParseConstraints", "EdgeCaseGenerator")

# After initial generation, request human feedback
builder.add_edge("EdgeCaseGenerator", "HumanFeedback")

# Conditional loop: if accepted → END, else back to EdgeCaseGenerator


def _route_after_feedback(
    state: dict,
) -> Literal["ParseConstraints", "__end__"]:
    # Terminate if reviewer accepted
    if state.get("accepted", False):
        return END
    # Re-run constraint parsing before generating new edge cases
    return "ParseConstraints"


# Update conditional edges to reflect new routing destinations
builder.add_conditional_edges(
    "HumanFeedback",
    _route_after_feedback,
    path_map=["ParseConstraints", END],
)

# Expose the *StateGraph* so Studio can compile it, but also provide a helper
# that compiles with a MemorySaver to enable human-in-the-loop persistence.

graph_builder = builder  # alias for clarity
graph = graph_builder  # exported for importers / Studio discovery

# ---------------------------------------------------------------------------
# Helper: compile the graph with an in-memory checkpointer so that interrupt /
# resume works when running programmatically or via the CLI.
# ---------------------------------------------------------------------------


def compile_with_memory(thread_id: str | None = None):
    """Return a compiled graph wrapped with MemorySaver.

    If *thread_id* is provided, it will be embedded in the default config so
    callers can omit it when invoking/resuming.
    """

    compiled = graph_builder.compile(checkpointer=MemorySaver())
    if thread_id is not None:
        compiled = compiled.with_config({"configurable": {"thread_id": thread_id}})
    return compiled


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

    compiled = compile_with_memory()
    # Run with auto-accept feedback to avoid interactive pause in CLI mode.
    final_state = compiled.invoke({"problem_spec": problem_text, "feedback": ""})
    print(json.dumps(final_state["edge_cases"], indent=2))

# ---------------------------------------------------------------------------
# Convenience helpers for external callers
# ---------------------------------------------------------------------------


def start_new_run(problem_markdown: str, *, feedback: str = ""):
    """Start a fresh thread and run until completion or interrupt.

    Returns a tuple (thread_id, final_state).
    If the run pauses for feedback and *feedback* is empty, an InterruptException
    will be propagated. Provide *feedback* to pre-accept or auto-respond.
    """

    thread_id = str(uuid.uuid4())
    compiled = compile_with_memory(thread_id)
    config = {"configurable": {"thread_id": thread_id}}

    state = compiled.invoke(
        {"problem_spec": problem_markdown, "feedback": feedback}, config
    )
    return thread_id, state


def resume_run(thread_id: str, *, feedback: str = ""):
    """Resume a paused run by supplying *feedback* via Command(resume=...)."""

    compiled = compile_with_memory(thread_id)
    config = {"configurable": {"thread_id": thread_id}}
    return compiled.resume(Command(resume=feedback), config)
