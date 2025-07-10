from typing import TypedDict, Optional, List

class TestValidatorState(TypedDict):
    """
    Represents the state for the Test Case Validation and Execution workflow.
    """
    # --- Initial inputs ---
    problem_dir_path: str
    bruteforce_time_limit: float

    # --- Data loaded from files ---
    bruteforce_path: str
    small_test_gen_path: str
    stress_test_gen_path: str
    validator_path: str
    
    # --- Internal state ---
    # Path to a temporary directory holding all generated files
    run_dir_path: str 
    # Lists of paths to valid input files after validation
    valid_small_tests: Optional[List[str]]
    valid_large_tests: Optional[List[str]]
    invalid_tests: Optional[List[dict]] # <-- ADD THIS LINE to track invalid files

    # --- Final output ---
    final_verdict: str
