"""Prompt templates for the novel prompt generation pipeline."""

GENERATE_PROBLEM_STATEMENT_PROMPT = """You are an expert at creating programming problems and competitive programming questions.

Your task is to generate a clear, well-structured problem statement based on the given topics and context.

## Input Information:
- Topics: {topics}
- Previous Problem: {previous_problem}
- User Prompt: {user_prompt}

## Requirements:
1. Create a programming problem that is:
   - Clear and unambiguous
   - Appropriate difficulty level (medium-hard)
   - Engaging and interesting
   - Well-structured with clear input/output format

2. The problem statement should include:
   - Problem description
   - Input format specification
   - Output format specification
   - Constraints
   - Example test cases

3. If a previous problem is provided, ensure the new problem is:
   - Different from the previous one
   - Similar in difficulty level
   - Related to the same topic area if possible
   - Builds upon or extends the concepts from the previous problem

4. If user prompt is provided, incorporate those specific requirements.

5. If topics is "None" but previous problem exists:
   - Use the previous problem's topic area as a starting point
   - Create a variation or extension of the previous problem
   - Focus on the user prompt if provided

6. If topics is "None" and no previous problem:
   - Focus entirely on the user prompt
   - Create a problem that matches the user's specific requirements

## Output Format:
Generate a complete problem statement in markdown format. Include all necessary sections and be very specific about input/output formats.

Generate the problem statement now:"""

GENERATE_TEST_CASES_PROMPT = """You are an expert at creating test cases for programming problems.

Based on the given problem statement, generate 4-6 comprehensive test cases that cover:
- Edge cases
- Normal cases
- Boundary conditions
- Different input sizes

## Problem Statement:
{problem_statement}

## Requirements:
1. Generate exactly 4-6 test cases
2. Each test case must have:
   - Clear input format
   - Expected output
   - Brief description of what it tests

3. Test cases should cover:
   - Small inputs (n ≤ 10)
   - Medium inputs (10 < n ≤ 1000)
   - Large inputs (n > 1000) if applicable
   - Edge cases (empty input, maximum values, etc.)
   - Normal cases

4. **IMPORTANT: Use this exact format for each test case:**

```
Test Case 1:
Input: [actual input data]
Expected Output: [expected output]
Description: [brief description]

Test Case 2:
Input: [actual input data]
Expected Output: [expected output]
Description: [brief description]

... (continue for 4-6 test cases)
```

5. Make sure the input and output match the problem's input/output format exactly.

Generate the test cases now using the exact format specified above:"""
