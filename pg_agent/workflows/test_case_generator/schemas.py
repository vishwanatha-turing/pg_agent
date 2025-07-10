from typing import TypedDict, Optional

class TestCaseGeneratorState(TypedDict):
    """
    Represents the state for the Test Case Generation workflow.
    """
    # --- Initial inputs ---
    problem_dir_path: str

    # --- Data loaded from files ---
    problem_statement: str
    bruteforce_code: str

    # --- Final outputs ---
    small_test_gen_path: Optional[str]
    stress_test_gen_path: Optional[str]
    validator_path: Optional[str]
    final_verdict: str
