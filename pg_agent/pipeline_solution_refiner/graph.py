"""Graph construction and compilation for the solution refiner pipeline."""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .types import RefineState
from .nodes import (
    llm_solution,
    judge_node,
    route_after_judge,
    compile_and_run_node,
    format_test_cases_node,
)


def build_solution_graph():
    """Build the solution refinement graph."""
    builder = StateGraph(RefineState)
    builder.add_node("LLM_Solution", llm_solution)
    builder.add_node("FormatTestCases", format_test_cases_node)
    builder.add_node("CompileRun", compile_and_run_node)
    builder.add_node("Judge", judge_node)

    builder.set_entry_point("LLM_Solution")
    builder.add_edge("LLM_Solution", "FormatTestCases")
    builder.add_edge("FormatTestCases", "CompileRun")
    builder.add_edge("CompileRun", "Judge")

    builder.add_conditional_edges(
        "Judge", route_after_judge, path_map=["LLM_Solution", END]
    )

    return builder


# Build the graph
solution_graph = build_solution_graph()


def compile_with_memory(thread_id: str | None = None):
    """Compile the graph with memory checkpointing."""
    compiled = solution_graph.compile(checkpointer=MemorySaver())
    if thread_id:
        compiled = compiled.with_config({"configurable": {"thread_id": thread_id}})
    return compiled
