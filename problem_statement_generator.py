import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable


SYSTEM_PROMPT = (
    "You are an expert problem setter for international informatics olympiads. "
    "Given the following topics, generate a completely original, high-difficulty programming problem. "
    "The problem should be suitable for a national or international olympiad, and must be clearly worded, unambiguous, and solvable in C++. "
    "Output ONLY the problem statement in Markdown format. Do not include the solution or any hints.\n\n"
    "Topics: {topics}\n"
)


def generate_problem_statement(topics: List[str]) -> str:
    """
    Uses LangChain LLMChain with OpenAI GPT-4 to generate a Markdown-formatted problem statement for the given topics.
    Args:
        topics (List[str]): List of algorithmic topics.
    Returns:
        str: Markdown-formatted problem statement.
    """
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


if __name__ == "__main__":
    # Example usage
    example_topics = ["Graphs", "Dynamic Programming"]
    print("Generating problem for topics:", example_topics)
    print(generate_problem_statement(example_topics))


def problem_generator_node(state):
    """
    Node that generates a problem statement based on selected topics.
    Requires: topics in state
    Updates: problem_statement in state
    """
    # Get topics from state
    topics = state.get("topics", [])
    if not topics:
        raise ValueError("No topics found in state for problem generation")

    # Generate problem statement
    problem_statement = generate_problem_statement(topics)

    # Return only the fields we're updating
    return {"problem_statement": problem_statement}
