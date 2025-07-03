from langgraph.graph import StateGraph, END
from .schemas import SolverState
from .nodes import (
    gen_bruteforce_node,
    gen_test_case_code_node,         # <-- New import
    run_test_case_generator_node,    # <-- New import
    gen_optimal_solution_node,
    refine_solution_node,
    run_tests_node,
    cleanup_node,
)

def should_refine(state: SolverState) -> str:
    """Decision node: determines if we should loop to refine or finish."""
    print("--- Decision: Should Refine? ---")
    # First, check if test generation failed. If so, end immediately.
    if state.get("test_results", {}).get("details", "").startswith("FATAL"):
        print("  -> Verdict: FATAL error during test generation. Ending.")
        return "cleanup"

    if state["test_results"]["failed"] == 0:
        print("  -> Verdict: PASSED. Proceed to cleanup.")
        return "cleanup"
    
    if state["iteration_count"] >= state["max_iterations"]:
        print(f"  -> Verdict: FAILED. Max iterations ({state['max_iterations']}) reached.")
        return "cleanup"
    
    print(f"  -> Verdict: FAILED. Continuing to refinement loop (Attempt #{state['iteration_count'] + 1}).")
    return "refine_solution"

def build_auto_solver_graph():
    """Builds the LangGraph agent for solving programming problems."""
    workflow = StateGraph(SolverState)

    # --- 1. Add all nodes to the graph ---
    workflow.add_node("gen_bruteforce", gen_bruteforce_node)
    workflow.add_node("gen_test_case_code", gen_test_case_code_node) # <-- New node
    workflow.add_node("run_test_case_generator", run_test_case_generator_node) # <-- New node
    workflow.add_node("gen_optimal", gen_optimal_solution_node)
    workflow.add_node("run_tests", run_tests_node)
    workflow.add_node("refine_solution", refine_solution_node)
    workflow.add_node("cleanup", cleanup_node)

    # --- 2. Define the new sequential flow for generation ---
    workflow.set_entry_point("gen_bruteforce")
    workflow.add_edge("gen_bruteforce", "gen_test_case_code")
    workflow.add_edge("gen_test_case_code", "run_test_case_generator")
    workflow.add_edge("run_test_case_generator", "gen_optimal")
    
    # After all code is generated, proceed to the first test run.
    workflow.add_edge("gen_optimal", "run_tests")

    # The rest of the refinement loop logic remains the same
    workflow.add_conditional_edges(
        "run_tests",
        should_refine,
        {
            "refine_solution": "refine_solution",
            "cleanup": "cleanup",
        },
    )
    workflow.add_edge("refine_solution", "run_tests")
    workflow.add_edge("cleanup", END)

    return workflow.compile()

auto_solver_graph = build_auto_solver_graph()