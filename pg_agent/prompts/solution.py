# Prompt for generating C++ solutions

SOLUTION_PROMPT = """You are an expert competitive programming solution generator.
Given a problem statement, generate a highly optimized C++ solution.

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

__all__ = ["SOLUTION_PROMPT"]
