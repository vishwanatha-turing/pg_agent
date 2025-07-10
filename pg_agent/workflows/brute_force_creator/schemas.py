from typing import TypedDict, Dict, List, Any, Optional

class BruteForceState(TypedDict):
    """
    Represents the state for the Bruteforce Creation workflow.
    """
    # --- Initial inputs ---
    problem_dir_path: str
    max_iterations: int

    # --- Data loaded from files ---
    problem_statement: str
    # A list of dicts, e.g., [{"input": "content", "output": "content"}]
    example_test_cases: List[Dict[str, str]]

    # --- State for the generation loop ---
    bruteforce_code: Optional[str]
    # A list of failures from the last test run
    test_failures: Optional[List[Dict[str, Any]]]
    iteration_count: int

    # --- Final output ---
    final_verdict: str
    final_bruteforce_path: Optional[str]
