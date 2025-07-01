from langgraph.graph import StateGraph, END

from .schemas import ValidationState
# Import the renamed node functions
from .validation_nodes import sandbox_run_test, critique_node, verdict_node

def should_critique(state: ValidationState) -> str:
    """
    This conditional edge determines whether to generate a critique or not.
    """
    print("--- Checking Test Results for Routing ---")
    if state["test_results"]["failed"] > 0:
        # Route to the 'critique_node'
        print("  Condition: Tests failed. Routing to Critique Node.")
        return "critique_node"
    else:
        # Route to the 'verdict_node'
        print("  Condition: All tests passed. Routing to Verdict Node.")
        return "verdict_node"

def get_solution_validator_graph():
    """
    Builds and returns the compiled solution validator graph.
    """
    workflow = StateGraph(ValidationState)

    # Add the nodes with their new, non-conflicting names
    workflow.add_node("sandbox_run_test", sandbox_run_test)
    workflow.add_node("critique_node", critique_node)
    workflow.add_node("verdict_node", verdict_node)

    workflow.set_entry_point("sandbox_run_test")

    # Update the conditional edge mapping to use the new node names
    workflow.add_conditional_edges(
        "sandbox_run_test",
        should_critique,
        {
            "critique_node": "critique_node",
            "verdict_node": "verdict_node",
        },
    )

    # The edge from critique now goes to the verdict node
    workflow.add_edge("critique_node", "verdict_node")
    
    # The verdict node is the end of this graph
    workflow.add_edge("verdict_node", END)

    return workflow.compile()

solution_validator_graph = get_solution_validator_graph()