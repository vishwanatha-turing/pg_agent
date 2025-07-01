from typing import TypedDict, Dict, Any, Optional

class ValidationState(TypedDict):
    """
    Represents the state for validating a C++ solution.
    This is the central data structure for the validator graph.
    """
    # --- Inputs for the validation ---
    problem_statement: str
    solution_code: str          # The C++ code for the user's solution
    test_generator_code: str    # The C++ code for testcaseGenerator.cpp
    bruteforce_solution_code: str # The C++ code for the correct/bruteforce solution

    # --- Fields populated by the graph ---
    test_results: Optional[Dict[str, Any]]
    critique: Optional[str]
    verdict: Optional[str]

# You can add other state TypedDicts here in the future