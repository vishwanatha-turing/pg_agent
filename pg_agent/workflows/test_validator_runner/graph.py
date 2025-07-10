from langgraph.graph import StateGraph, END
from .schemas import TestValidatorState
from .nodes import (
    load_scripts_node,
    run_generators_node,
    validate_inputs_node,
    run_bruteforce_on_small_tests_node,
    save_results_node,
)

def build_test_validator_graph():
    """Builds the graph for the test case validation and execution workflow."""
    workflow = StateGraph(TestValidatorState)

    # Add nodes
    workflow.add_node("load_scripts", load_scripts_node)
    workflow.add_node("run_generators", run_generators_node)
    workflow.add_node("validate_inputs", validate_inputs_node)
    workflow.add_node("run_bruteforce", run_bruteforce_on_small_tests_node)
    workflow.add_node("save_results", save_results_node)

    # Define the sequential flow
    workflow.set_entry_point("load_scripts")
    workflow.add_edge("load_scripts", "run_generators")
    workflow.add_edge("run_generators", "validate_inputs")
    workflow.add_edge("validate_inputs", "run_bruteforce")
    workflow.add_edge("run_bruteforce", "save_results")
    workflow.add_edge("save_results", END)

    return workflow.compile()

test_validator_graph = build_test_validator_graph()
