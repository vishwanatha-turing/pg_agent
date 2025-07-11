"""Type definitions for the solution refiner pipeline."""

from typing_extensions import TypedDict
from typing import Union


class RefineState(TypedDict, total=False):
    """State schema for the solution refinement pipeline."""

    problem_statement: str
    test_cases: Union[str, list]  # Can be string (any format) or list[tuple[str, str]]
    basic_tests: Union[
        str, list
    ]  # Can be string (any format) or list[tuple[str, str]] - for backward compatibility
    formatted_test_cases: (
        list  # list[tuple[str, str]] - test cases formatted for the solution
    )
    cpp_solution: str
    failing_tests: list  # list[dict]
    passing_tests: list  # list[dict] - test cases that passed
    attempt: int
    all_passed: bool
    compile_error: str | None
