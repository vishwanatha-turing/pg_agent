# solution_generator.py
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from pg_agent.prompts.solution import SOLUTION_PROMPT
from typing import List

__all__ = [
    "generate_cpp_solution",
    "solution_generator_node",
]


def _get_claude_llm():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")

    return ChatAnthropic(
        model="claude-opus-4-20250514",
        anthropic_api_key=api_key,
        temperature=0.1,
        max_tokens=3200,
    )


def _strip_code_fences(text: str) -> str:
    """Remove surrounding triple-backtick fences (optionally with language tag)."""
    if text.startswith("```"):
        lines: List[str] = text.splitlines()
        # Drop first line (``` or ```cpp)
        lines = lines[1:]
        # Drop last line if it's a closing fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text.strip()


def generate_cpp_solution(problem_statement: str) -> str:
    """Generate a C++17 solution for *problem_statement* using Claude Opus."""
    llm = _get_claude_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert competitive programming solution generator."),
            ("human", SOLUTION_PROMPT),
        ]
    )
    chain: Runnable = prompt | llm | StrOutputParser()
    solution = chain.invoke({"problem_statement": problem_statement})
    return _strip_code_fences(solution)


# ---------------------------------------------------------------------------
# LangGraph node wrapper
# ---------------------------------------------------------------------------


def solution_generator_node(state):
    """LangGraph node: generates `cpp_solution` from state["problem_statement"]."""
    problem_statement = state.get("problem_statement")
    if not problem_statement:
        raise ValueError("No problem statement found in state for solution generation")

    cpp_solution = generate_cpp_solution(problem_statement)
    return {"cpp_solution": cpp_solution}


if __name__ == "__main__":
    example_problem = """
    Given an array of integers, find the longest increasing subsequence.
    Input: List of integers
    Output: Length of the longest increasing subsequence
    """
    print("Testing with example problem...")
    print("\nGenerating solution...")
    print(generate_cpp_solution(example_problem))
