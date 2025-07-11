from typing import TypedDict, Optional, List, Tuple

class NovelProblemState(TypedDict):
    """
    Represents the state for the Novel Problem Creation workflow.
    """
    # --- Inputs from CLI ---
    output_dir: str
    topics: Optional[str]
    context_dir: Optional[str]
    user_prompt: Optional[str]

    # --- Internal State ---
    previous_problem: Optional[str] # Loaded from context_dir
    problem_statement: str
    human_feedback: Optional[str]
    # List of (input_str, output_str) tuples
    test_cases: List[Tuple[str, str]] 
