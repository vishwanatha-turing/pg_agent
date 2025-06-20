from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from operator import add
from topic_selector import topic_selector_node
from problem_statement_generator import (
    problem_generator_node,
)
from test_case_generator import test_case_generator_node
from solution_generator import solution_generator_node


class PipelineState(TypedDict, total=False):
    # Message-based state
    messages: Annotated[list, add_messages]

    # List-based states with add reducer
    topics: Annotated[list[str], add]
    scenarios: Annotated[list[str], add]
    test_cases: Annotated[list[str], add]
    sample_test_cases: Annotated[list[str], add]
    test_results: Annotated[list[str], add]
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


def placeholder_node(state):
    """Placeholder node that just passes through the state"""
    return state


def build_pipeline_graph():
    # Configure the graph
    graph = StateGraph(PipelineState)

    # Add nodes (update test_case_generator to use real node)
    graph.add_node("topic_selector", topic_selector_node)
    graph.add_node("problem_generator", problem_generator_node)
    graph.add_node("test_case_generator", test_case_generator_node)  # Real node
    graph.add_node("solution_generator", placeholder_node)
    graph.add_node("metadata_setup", placeholder_node)
    graph.add_node("join_for_validation", placeholder_node)
    graph.add_node("agentic_validator", placeholder_node)
    graph.add_node("fix_or_regenerate_test_cases", placeholder_node)
    graph.add_node("qwen_evaluation", placeholder_node)
    graph.add_node("archive_problem", placeholder_node)
    graph.add_node("retry_problem", placeholder_node)

    # Entry point from START
    graph.add_edge(START, "topic_selector")

    # Main sequential flow
    graph.add_edge("topic_selector", "problem_generator")
    graph.add_edge("problem_generator", "solution_generator")

    # Parallel execution after problem generation
    graph.add_edge("problem_generator", "test_case_generator")
    graph.add_edge("problem_generator", "metadata_setup")

    # Join node to synchronize parallel outputs
    graph.add_edge("solution_generator", "join_for_validation")
    graph.add_edge("test_case_generator", "join_for_validation")
    graph.add_edge("metadata_setup", "join_for_validation")

    # Continue with validation
    graph.add_edge("join_for_validation", "agentic_validator")

    # Conditional flows from validator
    def validator_condition(state):
        return state.get("validation_result", "pass")  # Default to pass for now

    graph.add_conditional_edges(
        "agentic_validator",
        validator_condition,
        {"pass": "qwen_evaluation", "fail": "fix_or_regenerate_test_cases"},
    )

    # Loop back from fix/regenerate to validator
    graph.add_edge("fix_or_regenerate_test_cases", "agentic_validator")

    # Conditional flows from Qwen evaluation
    def qwen_condition(state):
        return state.get("qwen_result", "solved")  # Default to solved for now

    graph.add_conditional_edges(
        "qwen_evaluation",
        qwen_condition,
        {"fail_all": "archive_problem", "solved": "retry_problem"},
    )

    # End conditions
    graph.add_edge("archive_problem", END)
    graph.add_edge("retry_problem", "problem_generator")

    return graph


def run_graph(initial_state=None):
    # Create a new state dictionary with all required fields properly initialized
    state = {}

    # Update with any provided initial state values
    if initial_state:
        state.update(initial_state)

    # Build and compile the graph
    graph = build_pipeline_graph()
    compiled = graph.compile()

    png_bytes = compiled.get_graph().draw_mermaid_png()

    with open("pipeline_graph.png", "wb") as f:
        f.write(png_bytes)

    return compiled.invoke(state)


def build_test_graph():
    """
    Test graph that we'll build incrementally.
    Currently implements topic selector, problem generator, test case generator,
    and solution generator.
    """
    # Configure the graph
    graph = StateGraph(PipelineState)

    # Add implemented nodes
    graph.add_node("topic_selector", topic_selector_node)
    graph.add_node("problem_generator", problem_generator_node)
    graph.add_node("test_case_generator", test_case_generator_node)
    graph.add_node("solution_generator", solution_generator_node)

    # Flow: START -> topic_selector -> problem_generator -> [test_case_generator, solution_generator] -> END
    graph.add_edge(START, "topic_selector")
    graph.add_edge("topic_selector", "problem_generator")

    # Parallel execution after problem generation
    graph.add_edge("problem_generator", "test_case_generator")
    graph.add_edge("problem_generator", "solution_generator")

    # Both test cases and solution need to complete before ending
    graph.add_edge("test_case_generator", END)
    graph.add_edge("solution_generator", END)

    return graph.compile()


def test_pipeline():
    """
    Function to test our incrementally built graph
    """
    # Create empty initial state
    initial_state = {}

    # Build and run test graph
    test_graph = build_test_graph()
    # result = test_graph.invoke(initial_state)

    # print("Test result:", result)
    return test_graph


graph = test_pipeline()


# if __name__ == "__main__":
#     # Run the test graph instead of the main graph
#     test_result = test_pipeline()
