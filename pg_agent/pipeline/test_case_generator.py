# test_case_generator.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from pg_agent.prompts.test_case import (
    SCENARIO_PROMPT,
    TEST_CASE_PROMPT,
    SAMPLE_TEST_CASE_PROMPT,
)
import json
import ast

__all__ = [
    "generate_test_scenarios",
    "generate_python_test_cases",
    "generate_sample_test_cases",
    "case_generator_node",
]

# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------


def _get_openai_llm(temperature: float = 0.7):
    """Return a ChatOpenAI instance with the env var already validated."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
    return ChatOpenAI(model="gpt-4-turbo", api_key=api_key, temperature=temperature)


def generate_test_scenarios(problem_statement: str) -> str:
    """Generate a newline-separated list of scenarios for *problem_statement*."""
    llm = _get_openai_llm()
    prompt = ChatPromptTemplate.from_messages([("system", SCENARIO_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    scenarios = chain.invoke({"problem_statement": problem_statement})
    return scenarios.strip()


def generate_python_test_cases(problem_statement: str, scenarios: str):
    """Generate a list of (input, expected_output) tuples for *problem_statement*.

    The underlying prompt requests the LLM to output a JSON array. This helper
    parses that JSON and returns it as `list[tuple[str, str]]`.
    """
    llm = _get_openai_llm()
    prompt = ChatPromptTemplate.from_messages([("system", TEST_CASE_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    raw = chain.invoke({"problem_statement": problem_statement, "scenarios": scenarios})
    raw = raw.strip()

    # Attempt to parse as JSON first; fall back to Python literal list.
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(raw)
        except Exception as err:
            raise ValueError(
                f"Unable to parse test cases JSON/py literal: {err}\nRaw output:\n{raw}"
            )

    if not isinstance(data, list):
        raise ValueError("Parsed test cases must be a list")

    # Normalize into list[tuple[str,str]]
    test_case_list = []
    for item in data:
        if isinstance(item, dict):
            inp = item.get("input")
            out = item.get("expected_output") or item.get("output")
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            inp, out = item
        else:
            raise ValueError(f"Unexpected test case format: {item}")
        if not isinstance(inp, str) or not isinstance(out, str):
            raise ValueError("Test case input/output must be strings")
        # Trim leading/trailing whitespace to avoid accidental grading issues
        test_case_list.append((inp.strip(), out.strip()))

    return test_case_list


def generate_sample_test_cases(problem_statement: str) -> str:
    """Generate sample test cases with explanations for docs / quick validation."""
    llm = _get_openai_llm(temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([("system", SAMPLE_TEST_CASE_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    sample_test_cases = chain.invoke({"problem_statement": problem_statement})
    return sample_test_cases.strip()


# ---------------------------------------------------------------------------
# LangGraph node wrapper
# ---------------------------------------------------------------------------


def case_generator_node(state):
    """LangGraph node that generates scenarios, concrete test cases, and samples."""
    problem_statement = state.get("problem_statement")
    if not problem_statement:
        raise ValueError("No problem statement found in state for test case generation")

    # Skip scenario and sample generation for now – generate test cases directly.
    test_cases = generate_python_test_cases(problem_statement, "")

    return {"test_cases": test_cases}  # list[tuple[str,str]]


if __name__ == "__main__":
    example_problem = """
    Given an array of integers, find the longest increasing subsequence.
    Input: List of integers
    Output: Length of the longest increasing subsequence
    """
    print("Testing with example problem...")

    print("\nGenerating scenarios...")
    scenarios = generate_test_scenarios(example_problem)
    print(scenarios)

    print("\nGenerating test cases...")
    test_cases = generate_python_test_cases(example_problem, scenarios)
    print(test_cases)

    print("\nGenerating sample test cases with explanations...")
    sample_test_cases = generate_sample_test_cases(example_problem)
    print(sample_test_cases)
