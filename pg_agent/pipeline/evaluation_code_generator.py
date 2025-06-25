# evaluation_code_generator.py
"""Node for generating Python evaluation scripts that judge C++ solutions.

This node takes the `problem_statement` produced by the problem generator and
returns Python code that will:
    * accept a C++ solution source string and a list of test cases,
    * compile the solution,
    * run it against each test, and
    * report pass/fail statistics.
"""

from __future__ import annotations

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from pg_agent.prompts.evaluation_code import EVALUATION_PROMPT

__all__ = [
    "generate_evaluation_code",
    "evaluation_code_generator_node",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_openai_llm(temperature: float = 0.3):
    """Return a `ChatOpenAI` instance after validating the API key env var."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    return ChatOpenAI(
        model="gpt-4-turbo",
        api_key=api_key,
        temperature=temperature,
        max_tokens=2048,
    )


# ---------------------------------------------------------------------------
# Public generation function
# ---------------------------------------------------------------------------


def generate_evaluation_code(problem_statement: str) -> str:
    """Generate a Python judge script for *problem_statement* using GPT-4."""
    llm = _get_openai_llm(temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([("system", EVALUATION_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    code = chain.invoke({"problem_statement": problem_statement})
    return _strip_code_fences(code)


# ---------------------------------------------------------------------------
# LangGraph node wrapper
# ---------------------------------------------------------------------------


def evaluation_code_generator_node(state):
    """LangGraph node: creates `evaluation_code` from state["problem_statement"]."""
    problem_statement = state.get("problem_statement")
    if not problem_statement:
        raise ValueError(
            "No problem statement found in state for evaluation code generation"
        )

    evaluation_code = generate_evaluation_code(problem_statement)
    return {"evaluation_code": evaluation_code}


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _strip_code_fences(text: str) -> str:
    """Remove surrounding triple-backtick fences (``` or ```python).

    Many LLMs wrap code in markdown fences despite explicit instructions. This helper
    ensures we return clean, directly executable Python source.
    """
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop first fence line
        lines = lines[1:]
        # Drop last line if fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text.strip()


if __name__ == "__main__":
    # Simple manual test when running this file directly.
    example_problem = """
    Given an array of integers, find the length of the longest increasing subsequence.
    Input: List of integers
    Output: Integer – length of LIS
    """
    print("Generating evaluation script for example problem…\n")
    print(generate_evaluation_code(example_problem))
