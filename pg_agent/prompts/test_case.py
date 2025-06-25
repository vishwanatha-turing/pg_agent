# Prompt templates used by test_case_generator.

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

__all__ = [
    "SCENARIO_PROMPT",
    "TEST_CASE_PROMPT",
    "SAMPLE_TEST_CASE_PROMPT",
]
