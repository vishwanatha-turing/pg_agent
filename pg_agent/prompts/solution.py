# Prompt for generating C++ solutions

SOLUTION_PROMPT = """You are an expert competitive programming solution generator.
Given a problem statement, generate a highly optimized C++ solution.

Requirements:
- Solution must be in C++17
- Include detailed comments explaining the approach
- Handle all edge cases
- Provide optimal time and space complexity
- Include complexity analysis in comments
- Follow competitive programming best practices

Problem Statement:
{problem_statement}

Output ONLY the C++ code solution with comments."""

__all__ = ["SOLUTION_PROMPT"]
