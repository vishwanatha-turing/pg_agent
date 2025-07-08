"""Graph construction for the novel prompt pipeline."""

from langgraph.graph import StateGraph, END
from pg_agent.pipeline_novel_prompt.types import NovelPromptState
from pg_agent.pipeline_novel_prompt.nodes import (
    setup_output_node,
    generate_problem_statement_node,
    generate_test_cases_node,
    save_outputs_node,
)


def create_novel_prompt_graph():
    """Create the novel prompt generation graph."""

    workflow = StateGraph(NovelPromptState)

    # Add nodes
    workflow.add_node("setup_output", setup_output_node)
    workflow.add_node("generate_problem", generate_problem_statement_node)
    workflow.add_node("generate_tests", generate_test_cases_node)
    workflow.add_node("save_outputs", save_outputs_node)

    # Set entry point
    workflow.set_entry_point("setup_output")

    # Define the flow
    workflow.add_edge("setup_output", "generate_problem")
    workflow.add_edge("generate_problem", "generate_tests")
    workflow.add_edge("generate_tests", "save_outputs")
    workflow.add_edge("save_outputs", END)

    return workflow.compile()


def create_novel_prompt_graph_with_validation():
    """Create the novel prompt generation graph with validation."""

    workflow = StateGraph(NovelPromptState)

    # Add nodes
    workflow.add_node("setup_output", setup_output_node)
    workflow.add_node("generate_problem", generate_problem_statement_node)
    workflow.add_node("generate_tests", generate_test_cases_node)
    workflow.add_node("save_outputs", save_outputs_node)

    # Set entry point
    workflow.set_entry_point("setup_output")

    # Define the flow
    workflow.add_edge("setup_output", "generate_problem")
    workflow.add_edge("generate_problem", "generate_tests")
    workflow.add_edge("generate_tests", "save_outputs")
    workflow.add_edge("save_outputs", END)

    return workflow.compile()
