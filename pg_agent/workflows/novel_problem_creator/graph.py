from langgraph.graph import StateGraph, END
from .schemas import NovelProblemState
from .nodes import (
    setup_node,
    initial_generation_node,
    interactive_feedback_node,
    refinement_node,
    generate_examples_node,
    final_save_node,
)

def should_refine(state: NovelProblemState) -> str:
    """Decision node: checks if the user provided feedback."""
    print("--- Decision: Refine or Finalize? ---")
    if state.get("human_feedback"):
        print("  -> Feedback found. Looping back to refine.")
        return "refine"
    else:
        print("  -> No feedback. Proceeding to generate examples.")
        return "generate_examples"

def build_novel_problem_creator_graph():
    """Builds the graph for the interactive problem creation workflow."""
    workflow = StateGraph(NovelProblemState)

    # Add all nodes
    workflow.add_node("setup", setup_node)
    workflow.add_node("initial_generation", initial_generation_node)
    workflow.add_node("get_feedback", interactive_feedback_node)
    workflow.add_node("refine_problem", refinement_node)
    workflow.add_node("generate_examples", generate_examples_node)
    workflow.add_node("save_examples", final_save_node)

    # Define the graph's flow
    workflow.set_entry_point("setup")
    workflow.add_edge("setup", "initial_generation")
    workflow.add_edge("initial_generation", "get_feedback")

    # The main refinement loop
    workflow.add_conditional_edges(
        "get_feedback",
        should_refine,
        {
            "refine": "refine_problem",
            "generate_examples": "generate_examples",
        },
    )
    workflow.add_edge("refine_problem", "get_feedback") # Loop back for more feedback
    
    # Final steps
    workflow.add_edge("generate_examples", "save_examples")
    workflow.add_edge("save_examples", END)

    return workflow.compile()

novel_problem_creator_graph = build_novel_problem_creator_graph()
