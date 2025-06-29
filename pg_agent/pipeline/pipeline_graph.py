from typing import Annotated, TypedDict
from operator import add

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages

from .topic_selector import topic_selector_node
from .problem_statement_generator import problem_generator_node
from .test_case_generator import case_generator_node
from .solution_generator import solution_generator_node
from .evaluation_code_generator import evaluation_code_generator_node
from .evaluation_runner import evaluation_runner_node

# from .evaluation_runner import evaluation_runner_node  # unused for now

__all__ = [
    "PipelineState",
    "build_pipeline_graph",
    "run_graph",
    "build_test_graph",
    "test_pipeline",
]


class PipelineState(TypedDict, total=False):
    # Message-based state
    messages: Annotated[list, add_messages]

    # List-based states with add reducer
    topics: Annotated[list[str], add]
    scenarios: Annotated[list[str], add]
    test_cases: Annotated[list, add]
    sample_test_cases: Annotated[list[str], add]
    test_results: Annotated[list[dict], add]
    failed_tests: Annotated[list[str], add]
    retry_history: Annotated[list[str], add]

    # Counter with operator reducer
    retry_count: Annotated[int, add]

    # Single value states (no reducer needed)
    problem_statement: str
    cpp_solution: str
    validation_result: str
    qwen_result: str
    archive_path: str
    archived: bool
    status: str
    difficulty: str
    constraints: list
    solution_metadata: dict
    qwen_feedback: dict
    archive_metadata: dict
    test_case_metadata: dict
    metadata: dict
    evaluation_code: str


# ---------------------------------------------------------------------------
# Placeholder node (unimplemented steps)
# ---------------------------------------------------------------------------


def _passthrough_node(state):
    """A temporary placeholder node that returns *state* unchanged."""
    return state


# ---------------------------------------------------------------------------
# Graph builders
# ---------------------------------------------------------------------------


def build_pipeline_graph() -> StateGraph:
    """Return the fully wired LangGraph pipeline graph (placeholders for TODO nodes)."""

    graph = StateGraph(PipelineState)

    # Implemented nodes
    graph.add_node("topic_selector", topic_selector_node)
    graph.add_node("problem_generator", problem_generator_node)
    graph.add_node("test_case_generator", case_generator_node)
    graph.add_node("solution_generator", solution_generator_node)
    graph.add_node("evaluation_code_generator", evaluation_code_generator_node)
    graph.add_node("evaluation_runner", evaluation_runner_node)

    # Commented-out nodes for future expansion
    # graph.add_node("metadata_setup", _passthrough_node)
    # graph.add_node("join_for_validation", _passthrough_node)
    # graph.add_node("agentic_validator", _passthrough_node)
    # graph.add_node("fix_or_regenerate_test_cases", _passthrough_node)
    # graph.add_node("qwen_evaluation", _passthrough_node)
    # graph.add_node("archive_problem", _passthrough_node)
    # graph.add_node("retry_problem", _passthrough_node)

    # Edges
    graph.add_edge(START, "topic_selector")
    graph.add_edge("topic_selector", "problem_generator")

    # Fan-out to generation branches
    graph.add_edge("problem_generator", "solution_generator")
    graph.add_edge("problem_generator", "evaluation_code_generator")
    graph.add_edge("problem_generator", "test_case_generator")

    # Evaluation runner depends on three generators
    graph.add_edge("solution_generator", "evaluation_runner")
    graph.add_edge("evaluation_code_generator", "evaluation_runner")
    graph.add_edge("test_case_generator", "evaluation_runner")
    graph.add_edge("evaluation_runner", END)

    return graph


def run_graph(initial_state: dict | None = None):
    """Helper to compile + invoke the graph once (mainly for CLI use)."""

    state: dict = initial_state.copy() if initial_state else {}
    compiled = build_pipeline_graph().compile()
    return compiled.invoke(state)


# ---------------------------------------------------------------------------
# Testing helpers – smaller graph with only implemented nodes
# ---------------------------------------------------------------------------


def build_test_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("topic_selector", topic_selector_node)
    graph.add_node("problem_generator", problem_generator_node)
    graph.add_node("test_case_generator", case_generator_node)
    graph.add_node("solution_generator", solution_generator_node)
    graph.add_node("evaluation_code_generator", evaluation_code_generator_node)
    graph.add_node("evaluation_runner", evaluation_runner_node)

    graph.add_edge(START, "topic_selector")
    graph.add_edge("topic_selector", "problem_generator")
    graph.add_edge("problem_generator", "test_case_generator")
    graph.add_edge("problem_generator", "solution_generator")
    graph.add_edge("problem_generator", "evaluation_code_generator")

    # Evaluation runner depends on three generators
    graph.add_edge("solution_generator", "evaluation_runner")
    graph.add_edge("evaluation_code_generator", "evaluation_runner")
    graph.add_edge("test_case_generator", "evaluation_runner")
    graph.add_edge("evaluation_runner", END)

    return graph.compile()


def test_pipeline():
    """Return the compiled *test* graph so that external callers can invoke it."""
    return build_test_graph()


if __name__ == "__main__":
    print("Invoking minimal graph for smoke-test …")
    result = test_pipeline().invoke({})
    print("State after run:\n", result)

# ---------------------------------------------------------------------------
# Expose a graph variable for LangGraph Studio auto-discovery
# ---------------------------------------------------------------------------

# NOTE: Studio looks for a variable that holds a *StateGraph*. We create it
# lazily at import time so that `studio/langgraph.json` (now at repo root)
# can reference `pg_agent/pipeline/pipeline_graph.py:graph`.

graph = build_pipeline_graph()
