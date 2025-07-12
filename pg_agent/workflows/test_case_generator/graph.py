from langgraph.graph import StateGraph, END
from .schemas import TestCaseGeneratorState
from .nodes import (
    load_context_node,
    gen_small_tests_node,
    gen_stress_tests_node,
    gen_validator_node,
)

def build_test_case_generator_graph():
    """Builds the graph for the test case generation workflow with a sequential flow."""
    workflow = StateGraph(TestCaseGeneratorState)

    # Add nodes
    workflow.add_node("load_context", load_context_node)
    workflow.add_node("gen_small_tests", gen_small_tests_node)
    workflow.add_node("gen_stress_tests", gen_stress_tests_node)
    workflow.add_node("gen_validator", gen_validator_node)

    # --- THIS IS THE CRUCIAL FIX ---
    # Define a clear, sequential flow. Each node runs only after the previous one completes.
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "gen_small_tests")
    workflow.add_edge("gen_small_tests", "gen_stress_tests")
    workflow.add_edge("gen_stress_tests", "gen_validator")
    workflow.add_edge("gen_validator", END)
    # --- END OF FIX ---

    return workflow.compile()

test_case_generator_graph = build_test_case_generator_graph()
