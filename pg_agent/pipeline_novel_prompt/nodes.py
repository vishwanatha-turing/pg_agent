"""Graph nodes for the novel prompt pipeline."""

import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from pg_agent.pipeline_novel_prompt.types import NovelPromptState
from pg_agent.pipeline_novel_prompt.utils import (
    get_llm,
    setup_output_structure,
    save_problem_statement,
    save_test_cases,
    parse_test_cases_from_llm_response,
    problem_statement_prompt,
    test_cases_prompt,
)

logger = logging.getLogger(__name__)


def setup_output_node(state: NovelPromptState) -> NovelPromptState:
    """Setup the output folder structure by copying from template."""
    output_folder = state["output_folder"]
    auto_load = state.get("auto_load_previous", True)  # Default to True for better UX

    try:
        problem_statement_file, test_cases_folder = setup_output_structure(
            output_folder
        )

        # Store the file paths in state for later use (these are computed, not user inputs)
        state["problem_statement_file"] = problem_statement_file
        state["test_cases_folder"] = test_cases_folder

        # Auto-load previous problem statement if checkbox is selected
        if auto_load:
            from pg_agent.pipeline_novel_prompt.utils import detect_previous_problem

            previous_problem = detect_previous_problem(output_folder)
            if previous_problem:
                state["previous_problem"] = previous_problem
                logger.info(
                    f"Auto-loaded previous problem statement ({len(previous_problem)} characters)"
                )
            else:
                logger.info("No previous problem statement found to auto-load")
        else:
            logger.info("Auto-load disabled by user")

        logger.info(f"Output structure setup: {output_folder}")
        return state

    except Exception as e:
        logger.error(f"Failed to setup output structure: {str(e)}")
        raise


def generate_problem_statement_node(state: NovelPromptState) -> NovelPromptState:
    """Generate a problem statement based on topics and context."""
    llm = get_llm(temp=0.7)

    # Prepare context
    topics = state.get("topics", "None")
    previous_problem = state.get("previous_problem", "None")
    user_prompt = state.get("user_prompt", "None")

    # Validate that we have enough context to generate a problem
    if topics == "None" and previous_problem == "None" and user_prompt == "None":
        raise ValueError(
            "At least one of topics, previous_problem, or user_prompt must be provided"
        )

    # Format the prompt
    formatted_prompt = problem_statement_prompt.format(
        topics=topics, previous_problem=previous_problem, user_prompt=user_prompt
    )

    # Generate problem statement
    response = llm.invoke([HumanMessage(content=formatted_prompt)])
    problem_statement = response.content

    state["problem_statement"] = problem_statement
    logger.info("Problem statement generated successfully")

    return state


def generate_test_cases_node(state: NovelPromptState) -> NovelPromptState:
    """Generate test cases based on the problem statement."""
    llm = get_llm(temp=0.5)

    # Format the prompt
    formatted_prompt = test_cases_prompt.format(
        problem_statement=state["problem_statement"]
    )

    # Generate test cases
    response = llm.invoke([HumanMessage(content=formatted_prompt)])
    test_cases_response = response.content

    # Debug: Log the raw response
    logger.info(
        f"Raw LLM response for test cases ({len(test_cases_response)} characters):"
    )
    logger.info("=" * 50)
    logger.info(
        test_cases_response[:500] + "..."
        if len(test_cases_response) > 500
        else test_cases_response
    )
    logger.info("=" * 50)

    # Parse test cases from response
    test_cases = parse_test_cases_from_llm_response(test_cases_response)

    # If no test cases found or response is empty, try again with a simpler prompt
    if not test_cases or len(test_cases_response.strip()) < 50:
        logger.warning(
            "No test cases found or response too short, trying with simpler prompt"
        )

        # Try with a simpler prompt
        simple_prompt = f"""Generate 4 simple test cases for this problem:

{state['problem_statement']}

Format each test case as:
Input: [input data]
Expected Output: [output data]

Generate 4 test cases now:"""

        simple_response = llm.invoke([HumanMessage(content=simple_prompt)])
        simple_test_cases_response = simple_response.content

        logger.info(
            f"Simple prompt response ({len(simple_test_cases_response)} characters):"
        )
        logger.info(
            simple_test_cases_response[:300] + "..."
            if len(simple_test_cases_response) > 300
            else simple_test_cases_response
        )

        test_cases = parse_test_cases_from_llm_response(simple_test_cases_response)

    # If still no test cases, create some basic ones
    if not test_cases:
        logger.warning("Still no test cases found, creating basic fallback test cases")
        test_cases = create_fallback_test_cases(state["problem_statement"])

    # Ensure we have at least 4 test cases
    if len(test_cases) < 4:
        logger.warning(f"Only {len(test_cases)} test cases generated, expected 4-6")
        logger.warning("This might indicate a parsing issue with the LLM response")

    state["test_cases"] = test_cases
    logger.info(f"Generated {len(test_cases)} test cases")

    # Debug: Log the parsed test cases
    for i, (input_data, output_data) in enumerate(test_cases, 1):
        logger.info(f"Test case {i}:")
        logger.info(f"  Input: {input_data[:100]}...")
        logger.info(f"  Output: {output_data[:100]}...")

    return state


def create_fallback_test_cases(problem_statement: str) -> list[tuple[str, str]]:
    """Create basic fallback test cases when LLM fails."""
    logger.info("Creating fallback test cases")

    # Create some basic test cases based on common problem patterns
    fallback_cases = [
        ("1\n1", "1"),  # Simple single value
        ("2\n1 2", "3"),  # Two values
        ("3\n1 2 3", "6"),  # Three values
        ("4\n-1 0 1 2", "2"),  # Mixed positive/negative
    ]

    logger.info(f"Created {len(fallback_cases)} fallback test cases")
    return fallback_cases


def save_outputs_node(state: NovelPromptState) -> NovelPromptState:
    """Save the generated problem statement and test cases to files."""
    # Get file paths from state (set by setup_output_node)
    problem_statement_file = state.get("problem_statement_file")
    test_cases_folder = state.get("test_cases_folder")

    if not problem_statement_file or not test_cases_folder:
        raise ValueError("File paths not set. Make sure setup_output_node runs first.")

    # Save problem statement
    save_problem_statement(state["problem_statement"], problem_statement_file)

    # Save test cases
    save_test_cases(state["test_cases"], test_cases_folder)

    logger.info("All outputs saved successfully")
    return state
