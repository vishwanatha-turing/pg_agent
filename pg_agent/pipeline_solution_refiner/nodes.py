"""Graph nodes for the solution refiner pipeline."""

import textwrap
import json
from typing import Literal
import logging

from langgraph.types import Command, interrupt

from .types import RefineState
from .utils import (
    get_llm,
    get_o3_llm,
    strip_code_fences,
    extract_content_from_o3_response,
    solution_prompt,
    fix_prompt,
    compile_and_run,
)


def llm_solution(state: RefineState):
    """LLM node that generates or fixes C++ solutions."""
    llm = get_o3_llm()
    # Use fix prompt if we have a previous solution AND either failing tests OR compilation error
    if "cpp_solution" in state and (
        state.get("failing_tests") or state.get("compile_error")
    ):
        prompt = fix_prompt
        # Prepare failing tests info - include compilation error if present
        failing_info = state.get("failing_tests", [])
        if state.get("compile_error"):
            failing_info = [{"compile_error": state["compile_error"]}] + failing_info

        variables = {
            "problem_statement": state["problem_statement"],
            "previous_solution": state["cpp_solution"],
            "failing_tests": textwrap.indent(json.dumps(failing_info, indent=2), " "),
        }
    else:
        prompt = solution_prompt
        variables = {"problem_statement": state["problem_statement"]}
    msg = (prompt | llm).invoke(variables)  # AIMessage
    print(f"LLM response: {msg.content}")

    # Extract content from O3's structured response format
    content = extract_content_from_o3_response(msg)
    cpp_code = strip_code_fences(content)
    return {"cpp_solution": cpp_code}


def format_test_cases_node(state: RefineState):
    """LLM node that formats test cases to match the C++ solution's expected input format."""
    llm = get_llm()

    # Get the C++ solution and original test cases (as string)
    cpp_solution = state["cpp_solution"]
    original_test_cases = state.get("test_cases", state.get("basic_tests", ""))

    # Create the formatting prompt
    format_prompt = f"""
You are a test case formatter. Given a C++ solution and original test cases in any format, convert the test cases to the exact format the C++ solution expects as input.

C++ Solution:
```cpp
{cpp_solution}
```

Original Test Cases (as provided by user - can be in any format):
{original_test_cases}

Your task:
1. Parse the original test cases (they can be in any format - JSON, text, CSV, etc.)
2. Analyze the C++ code to understand what input format it expects
3. Convert each test case to match this expected format
4. Return ONLY a JSON array of [input, expected_output] pairs

Important:
- The input format must match EXACTLY what the C++ program expects
- Pay attention to how the program reads input (cin >> statements)
- Handle edge cases like invalid input appropriately
- Return valid JSON that can be parsed directly
- If the original format is unclear, make reasonable assumptions

Example output format:
[
  ["5", "10"],
  ["3", "6"],
  ["abc", "ERROR"]
]

Return only the JSON array, no additional text or explanation.
"""

    # Get formatted test cases from LLM
    response = llm.invoke(format_prompt)

    try:
        # Try to parse the response as JSON
        formatted_test_cases = json.loads(strip_code_fences(response.content))

        # Validate that it's a list of tuples
        if not isinstance(formatted_test_cases, list):
            raise ValueError("Response is not a list")

        # Convert to list of tuples if needed
        formatted_tuples = []
        for item in formatted_test_cases:
            if isinstance(item, list) and len(item) == 2:
                formatted_tuples.append((str(item[0]), str(item[1])))
            else:
                raise ValueError(f"Invalid test case format: {item}")

        logger = logging.getLogger("format_test_cases")
        logger.info(f"Formatted {len(formatted_tuples)} test cases")
        logger.info(f"Original: {original_test_cases}")
        logger.info(f"Formatted: {formatted_tuples}")

        return {"formatted_test_cases": formatted_tuples}

    except (json.JSONDecodeError, ValueError) as e:
        logger = logging.getLogger("format_test_cases")
        logger.error(f"Failed to parse formatted test cases: {e}")
        logger.error(f"LLM response: {response.content}")

        # Fall back to empty list if formatting fails
        return {"formatted_test_cases": []}


def judge_node(state: RefineState):
    """Judge node that determines if all tests passed and increments attempt counter."""
    failed = state.get("failing_tests", [])
    passed = state.get("passing_tests", [])
    compile_err = state.get("compile_error")
    all_passed = not failed and not compile_err
    attempt = state.get("attempt", 0) + 1

    logger = logging.getLogger("judge_node")
    logger.info(
        "Attempt %d: %d passed, %d failed, all_passed=%s",
        attempt,
        len(passed),
        len(failed),
        all_passed,
    )

    return {"all_passed": all_passed, "attempt": attempt}


def compile_and_run_node(state):
    """Main compilation and execution node (single canonical method)."""
    src = state["cpp_solution"]
    if not isinstance(src, str):
        src = getattr(src, "content", str(src))

    # Use formatted test cases if available, otherwise fall back to original
    tests = state.get("formatted_test_cases", [])

    # If no formatted test cases, try to get original test cases
    if not tests:
        original_tests = state.get("test_cases", state.get("basic_tests", []))
        if isinstance(original_tests, list):
            tests = original_tests
        else:
            # If original is a string, we have no valid test cases
            tests = []

    logger = logging.getLogger("compile_run_node")
    logger.info("Test cases found: %d", len(tests))

    if not tests:
        logger.warning("No test cases available for execution")
        return {
            "compile_error": "No test cases available",
            "failing_tests": [],
            "passing_tests": [],
        }

    for i, (inp, exp) in enumerate(tests):
        logger.info("Test %d: input='%s', expected='%s'", i, inp, exp)

    report = compile_and_run(src, tests)
    return report  # keys compile_error, failing_tests, passing_tests


def route_after_judge(state: RefineState) -> Literal["LLM_Solution", "__end__"]:
    """Router that decides whether to continue refining or end."""
    if state.get("all_passed"):
        return "__end__"
    if state.get("attempt", 0) >= 20:
        return "__end__"
    return "LLM_Solution"
