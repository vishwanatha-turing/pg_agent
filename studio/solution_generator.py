# solution_generator.py
import os
from typing import List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

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


def generate_cpp_solution(problem_statement: str) -> str:
    """
    Generate C++ solution using Claude Opus.
    Args:
        problem_statement (str): The problem to solve
    Returns:
        str: Generated C++ solution with comments
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")

    llm = ChatAnthropic(
        model="claude-opus-4-20250514",
        anthropic_api_key=api_key,
        temperature=0.1,  # Low temperature for more focused code generation
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert competitive programming solution generator."),
            (
                "human",
                """Generate a highly optimized C++ solution for this problem.
Requirements:
- Solution must be in C++17
- Include detailed comments explaining the approach
- Handle all edge cases
- Provide optimal time and space complexity
- Include complexity analysis in comments
- Follow competitive programming best practices

Problem Statement:
{problem_statement}

Output ONLY the C++ code solution with comments.""",
            ),
        ]
    )
    chain: Runnable = prompt | llm | StrOutputParser()
    solution = chain.invoke({"problem_statement": problem_statement})
    return solution.strip()


def solution_generator_node(state):
    """
    Node that generates C++ solution for the problem.
    Requires: problem_statement in state
    Updates: cpp_solution in state
    """
    problem_statement = state.get("problem_statement")
    if not problem_statement:
        raise ValueError("No problem statement found in state for solution generation")

    # Generate solution
    cpp_solution = generate_cpp_solution(problem_statement)

    # Return the solution to be added to state
    return {"cpp_solution": cpp_solution}


if __name__ == "__main__":
    # Example usage
    example_problem = """
    Given an array of integers, find the longest increasing subsequence.
    Input: List of integers
    Output: Length of the longest increasing subsequence
    """
    print("Testing with example problem...")
    print("\nGenerating solution...")
    solution = generate_cpp_solution(example_problem)
    print(solution)
