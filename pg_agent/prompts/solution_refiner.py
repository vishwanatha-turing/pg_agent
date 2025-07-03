# Prompt templates for the Solution Refiner graph

GENERATE_SOLUTION_PROMPT = """You are an elite competitive programming coach.
Given the problem statement below, write an **optimal C++17** solution.

Requirements:
- Solution must be in C++17
- Do NOT use `#include <bits/stdc++.h>`; instead include only the standard headers actually required (e.g. `<iostream>`, `<vector>`, `<unordered_map>`, etc.)
- Include detailed comments explaining the approach
- Handle all edge cases
- Provide optimal time and space complexity
- Include complexity analysis in comments
- Follow competitive programming best practices

Problem Statement:
{problem_statement}

Output ONLY the raw C++17 source code with comments. Do NOT wrap it in markdown fences or add any extra text."""

FIX_SOLUTION_PROMPT = """You are an elite competitive programming coach.
The following C++17 solution fails some tests. Analyse the failing case(s)
and return a **corrected** version of the code.

Requirements:
- Solution must be in C++17
- Do NOT use `#include <bits/stdc++.h>`; instead include only the standard headers actually required (e.g. `<iostream>`, `<vector>`, `<unordered_map>`, etc.)
- Include detailed comments explaining the approach
- Handle all edge cases
- Provide optimal time and space complexity
- Include complexity analysis in comments
- Follow competitive programming best practices

Problem Statement:
{problem_statement}

Previous Solution:
```cpp
{previous_solution}
```

Failing Test Details:
{failing_tests}

Output ONLY the raw C++17 source code with comments. Do NOT wrap it in markdown fences or add any extra text."""

__all__ = [
    "GENERATE_SOLUTION_PROMPT",
    "FIX_SOLUTION_PROMPT",
]
