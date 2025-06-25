import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from pg_agent.prompts.problem_statement import SYSTEM_PROMPT

__all__ = [
    "generate_problem_statement",
    "problem_generator_node",
]


def generate_problem_statement(topics: List[str]) -> str:
    """Generate a problem statement for the given *topics* using GPT-4."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    llm = ChatOpenAI(
        model="gpt-4-turbo",
        api_key=api_key,
        temperature=0.9,
        max_tokens=1024,
    )
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    result = chain.invoke({"topics": ", ".join(topics)})
    return result.strip()


# ---------------------------------------------------------------------------
# LangGraph node wrapper
# ---------------------------------------------------------------------------


def problem_generator_node(state):
    """LangGraph node: creates a problem statement from state["topics"]."""
    topics = state.get("topics", [])
    if not topics:
        raise ValueError("No topics found in state for problem generation")

    problem_statement = generate_problem_statement(topics)
    return {"problem_statement": problem_statement}


if __name__ == "__main__":
    example_topics = ["Graphs", "Dynamic Programming"]
    print("Generating problem for topics:", example_topics)
    print(generate_problem_statement(example_topics))
