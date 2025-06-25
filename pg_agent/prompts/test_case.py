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
Given this problem statement and the list of scenarios, output the concrete test cases **directly** instead of code.

Requirements:
1. Produce a JSON array. Each element is an object with exactly two string keys:
    • "input"            – The exact stdin string the judge will feed to the program (include new-lines as needed).
    • "expected_output"  – The exact stdout string expected from a correct solution (include trailing new-line if the format demands it).
2. Cover every scenario listed.
3. Keep inputs small but sufficient – up to ~10 KB total.
4. Ensure **no leading or trailing spaces** in either the `input` or `expected_output` strings.
5. Do NOT wrap the JSON in markdown fences or add any explanatory text.

Problem Statement:
{problem_statement}

Scenarios to cover:
{scenarios}

Output ONLY the JSON array, nothing else. """

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
