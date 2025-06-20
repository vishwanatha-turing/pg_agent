import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

SOLUTION_PROMPT = (
    "You are an expert competitive programmer. Given the following programming problem statement, "
    "write an efficient, correct C++ solution. Output ONLY the C++ code, with no explanation, comments, or extra text.\n\n"
    "Problem Statement (Markdown):\n{problem_statement}\n"
)


def generate_cpp_solution(problem_statement: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    llm = ChatOpenAI(
        model="gpt-4-turbo",
        api_key=api_key,
        temperature=0.7,
        max_tokens=1024,
    )
    prompt = ChatPromptTemplate.from_messages([("system", SOLUTION_PROMPT)])
    chain: Runnable = prompt | llm | StrOutputParser()
    result = chain.invoke({"problem_statement": problem_statement})
    return result.strip()
