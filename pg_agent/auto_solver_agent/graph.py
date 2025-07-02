from langgraph.graph import StateGraph, END
from .schemas import SolverState
from .nodes import (
    gen_bruteforce_node,
    gen_and_run_test_cases_node,
    gen_optimal_solution_node,
    refine_solution_node,
    run_tests_node,
    cleanup_node,
)

def should_refine(state: SolverState) -> str:
    """Decision node: determines if we should loop to refine or finish."""
    print("--- Decision: Should Refine? ---")
    if state["test_results"]["failed"] == 0:
        print("  -> Verdict: PASSED. Proceed to cleanup.")
        return "cleanup"
    
    if state["iteration_count"] >= state["max_iterations"]:
        print(f"  -> Verdict: FAILED. Max iterations ({state['max_iterations']}) reached.")
        return "cleanup" # Go to cleanup even on failure
    
    print(f"  -> Verdict: FAILED. Continuing to refinement loop (Attempt #{state['iteration_count'] + 1}).")
    return "refine_solution"

def build_auto_solver_graph():
    """Builds the LangGraph agent for solving programming problems."""
    workflow = StateGraph(SolverState)

    workflow.add_node("gen_bruteforce", gen_bruteforce_node)
    # This node now generates the code AND runs it to create the test case files
    workflow.add_node("gen_tests", gen_and_run_test_cases_node)
    workflow.add_node("gen_optimal", gen_optimal_solution_node)
    workflow.add_node("run_tests", run_tests_node)
    workflow.add_node("refine_solution", refine_solution_node)
    workflow.add_node("cleanup", cleanup_node)

    # The entry point forks to three parallel generation nodes
    workflow.set_entry_point("gen_bruteforce")
    workflow.add_edge("gen_bruteforce", "gen_tests")
    workflow.add_edge("gen_tests", "gen_optimal")
    
    # After the optimal solution is generated, we proceed to the first test run.
    workflow.add_edge("gen_optimal", "run_tests")

    # After running tests, we make a decision
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