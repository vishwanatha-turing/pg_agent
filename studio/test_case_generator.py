# test_case_generator.py
import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

# Prompts as module-level constants
SCENARIO_PROMPT = """You are an expert competitive programming test case designer.
Given this problem statement, identify all possible edge cases and scenarios that should be tested.
Consider:
- Boundary conditions
- Special cases
- Performance edge cases
- Invalid inputs
- Maximum/minimum values
- Empty/null cases

Problem Statement:
{problem_statement}

Output ONLY a list of scenarios, one per line, without any additional text."""

TEST_CASE_PROMPT = """You are an expert competitive programming test case generator.
Given this problem statement and list of scenarios, generate Python code that creates test cases.
Each test case should be a tuple of (input, expected_output).

Problem Statement:
{problem_statement}

Scenarios to cover:
{scenarios}

Output ONLY the Python code that generates the test cases, ensuring:
- Each test case tests one or more scenarios
- Test cases are comprehensive
- Test cases follow the input/output format specified in the problem
- Include comments explaining which scenario each test case covers"""

SAMPLE_TEST_CASE_PROMPT = """You are an expert competitive programming instructor.
Given this problem statement, generate sample test cases for initial validation and understanding.

Problem Statement:
{problem_statement}

Generate your response in exactly this format:

## Section 1: Sample Test Cases with Explanations

### Test Case 1:
**Input:** [input here]
**Step-by-step solution:**
1. [step 1]
2. [step 2]
3. [step 3]
**Output:** [output here]

### Test Case 2:
[repeat format for 4-5 test cases total]

## Section 2: Test Cases for Validation

```
Input: [input]
Output: [output]

Input: [input]
Output: [output]

[repeat for all test cases]
```

Make sure the test cases:
- Cover basic functionality
- Include at least one edge case
- Are easy to trace through manually
- Have clear, step-by-step explanations"""


def generate_test_scenarios(problem_statement: str) -> str:
    """
    Generate test scenarios using LLM.
    Args:
        problem_statement (str): The problem statement to generate scenarios for
    Returns:
        str: Generated scenarios, one per line
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    llm = ChatOpenAI(model="gpt-4-turbo", api_key=api_key, temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([("system", SCENARIO_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    scenarios = chain.invoke({"problem_statement": problem_statement})
    return scenarios.strip()


def generate_python_test_cases(problem_statement: str, scenarios: str) -> str:
    """
    Generate Python test cases based on scenarios.
    Args:
        problem_statement (str): The original problem statement
        scenarios (str): The generated test scenarios
    Returns:
        str: Python code for test cases
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    llm = ChatOpenAI(model="gpt-4-turbo", api_key=api_key, temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([("system", TEST_CASE_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    test_cases = chain.invoke(
        {"problem_statement": problem_statement, "scenarios": scenarios}
    )
    return test_cases.strip()


def generate_sample_test_cases(problem_statement: str) -> str:
    """
    Generate sample test cases with explanations for initial validation.
    Args:
        problem_statement (str): The problem statement to generate sample test cases for
    Returns:
        str: Sample test cases with step-by-step explanations and validation format
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    llm = ChatOpenAI(model="gpt-4-turbo", api_key=api_key, temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([("system", SAMPLE_TEST_CASE_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    sample_test_cases = chain.invoke({"problem_statement": problem_statement})
    return sample_test_cases.strip()


def test_case_generator_node(state):
    """
    Node that generates test cases in three steps:
    1. Generate test scenarios
    2. Convert scenarios to actual test cases
    3. Generate sample test cases with explanations for initial validation

    Requires: problem_statement in state
    Updates: scenarios, test_cases, and sample_test_cases in state
    """
    problem_statement = state.get("problem_statement")
    if not problem_statement:
        raise ValueError("No problem statement found in state for test case generation")

    # Step 1: Generate scenarios
    scenarios = generate_test_scenarios(problem_statement)

    # Step 2: Generate actual test cases
    test_cases = generate_python_test_cases(problem_statement, scenarios)

    # Step 3: Generate sample test cases with explanations
    sample_test_cases = generate_sample_test_cases(problem_statement)

    # Return scenarios, test cases, and sample test cases to be added to state
    return {
        "scenarios": [scenarios],  # Wrapped in list for add reducer
        "test_cases": [test_cases],  # Wrapped in list for add reducer
        "sample_test_cases": [sample_test_cases],  # Wrapped in list for add reducer
    }


if __name__ == "__main__":
    # Example usage
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
