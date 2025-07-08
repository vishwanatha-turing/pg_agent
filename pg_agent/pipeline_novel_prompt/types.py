"""Type definitions for the novel prompt pipeline."""

from typing import TypedDict, Optional


class NovelPromptState(TypedDict):
    """State for the novel prompt generation pipeline."""

    # Inputs
    topics: Optional[
        str
    ]  # Topic(s) for initial generation (optional if previous problem exists)
    previous_problem: Optional[str]  # Previous problem statement if exists
    user_prompt: Optional[str]  # User's prompt if provided

    # Generated content
    problem_statement: str  # Generated problem statement
    test_cases: list[tuple[str, str]]  # List of (input, expected_output) pairs

    # Output folder (copied from template)
    output_folder: str  # Folder where to save the generated files

    # Computed file paths (set by setup_output_node)
    problem_statement_file: Optional[str]  # Path to problem_statement.md
    test_cases_folder: Optional[str]  # Path to test_cases/ directory

    # UI Controls
    auto_load_previous: bool  # Checkbox to auto-load previous problem statement
