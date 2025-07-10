from langgraph.graph import StateGraph, END
from .schemas import TestCaseGeneratorState
from .nodes import (
    load_context_node,
    gen_small_tests_node,
    gen_stress_tests_node,
    gen_validator_node,
)

def build_test_case_generator_graph():
    """Builds the graph for the test case generation workflow."""
    workflow = StateGraph(TestCaseGeneratorState)

    # Add nodes
    workflow.add_node("load_context", load_context_node)
    workflow.add_node("gen_small_tests", gen_small_tests_node)
    workflow.add_node("gen_stress_tests", gen_stress_tests_node)
    workflow.add_node("gen_validator", gen_validator_node)

    # Define the flow
    workflow.set_entry_point("load_context")
    
    # After loading context, run all three generation tasks in parallel
    workflow.add_edge("load_context", "gen_small_tests")
    workflow.add_edge("load_context", "gen_stress_tests")
    workflow.add_edge("load_context", "gen_validator")

    # This is a simple, parallel graph. It ends after all branches complete.
    # We can add a "join" node later if we need to wait for all to finish.
    workflow.add_edge("gen_small_tests", END)
    workflow.add_edge("gen_stress_tests", END)
    workflow.add_edge("gen_validator", END)

    return workflow.compile()

test_case_generator_graph = build_test_case_generator_graph()
