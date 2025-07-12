from langgraph.graph import StateGraph, END
from .schemas import BruteForceState
from .nodes import (
    load_problem_node,
    gen_bruteforce_node,
    interactive_review_node,
    test_bruteforce_on_examples_node,
    refine_bruteforce_node,
    save_and_version_node,
)

def should_refine(state: BruteForceState) -> str:
    """Decision node: determines if we should loop to refine or finish."""
    print("--- Decision: Should Refine Bruteforce? ---")
    if state["test_failures"]:
        if state["iteration_count"] >= state["max_iterations"]:
            print(f"  -> Verdict: FAILED. Max iterations ({state['max_iterations']}) reached.")
            return "end_failure"
        print(f"  -> Verdict: FAILED. Continuing to refinement loop.")
        return "refine"
    else:
        print("  -> Verdict: PASSED. Proceed to save.")
        return "save"

def build_bruteforce_creator_graph():
    """Builds the LangGraph agent for creating and validating a bruteforce solution."""
    workflow = StateGraph(BruteForceState)

    workflow.add_node("load_problem", load_problem_node)
    workflow.add_node("generate_bruteforce", gen_bruteforce_node)
    workflow.add_node("interactive_review", interactive_review_node) # <-- New node
    workflow.add_node("test_on_examples", test_bruteforce_on_examples_node)
    workflow.add_node("refine_bruteforce", refine_bruteforce_node)
    workflow.add_node("save_solution", save_and_version_node)

    workflow.set_entry_point("load_problem")
    workflow.add_edge("load_problem", "generate_bruteforce")
    
    # --- NEW: Add the review step after generation ---
    workflow.add_edge("generate_bruteforce", "interactive_review")
    workflow.add_edge("interactive_review", "test_on_examples")
    
    workflow.add_conditional_edges(
        "test_on_examples",
        should_refine,
        {
            "refine": "refine_bruteforce",
            "save": "save_solution",
            "end_failure": END,
        },
    )
    
    workflow.add_edge("refine_bruteforce", "test_on_examples")
    workflow.add_edge("save_solution", END)

    return workflow.compile()

bruteforce_creator_graph = build_bruteforce_creator_graph()