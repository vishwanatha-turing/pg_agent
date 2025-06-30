from pathlib import Path
import json
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
# Load prompt from .txt
def load_prompt(path: str) -> ChatPromptTemplate:
    text = Path(path).read_text(encoding="utf-8")
    return ChatPromptTemplate.from_messages([("system", text), ("human", "{input}")])

# Set up LLM and prompt chains
llm = ChatOpenAI(model="gpt-4o", temperature=0)
parse_chain = load_prompt("prompts/parse_constraints.txt") | llm
edge_case_chain = load_prompt("prompts/edge_case_generator.txt") | llm

# Node 1: ParseConstraints
def parse_constraints(state: dict) -> dict:
    result = parse_chain.invoke({"input": state["problem_spec"]})
    return {**state, "constraints": result.content}

# Node 2: EdgeCaseGenerator
def edge_case_gen(state: dict) -> dict:
    result = edge_case_chain.invoke({"input": state["constraints"]})
    try:
        parsed = json.loads(result.content)
    except json.JSONDecodeError:
        parsed = [result.content]
    return {**state, "edge_cases": parsed}

# Define graph
builder = StateGraph(dict)
builder.add_node("ParseConstraints", parse_constraints)
builder.add_node("EdgeCaseGenerator", edge_case_gen)

builder.set_entry_point("ParseConstraints")
builder.add_edge("ParseConstraints", "EdgeCaseGenerator")
builder.add_edge("EdgeCaseGenerator", END)

graph = builder.compile()

# CLI usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m graphs.edge_case_suggester <path_to_problem.md>")
        exit(1)

    input_file = Path(sys.argv[1])
    problem_text = input_file.read_text(encoding="utf-8")
    final_state = graph.invoke({"problem_spec": problem_text})

    edge_cases = final_state["edge_cases"]
    if isinstance(edge_cases, list):
        edge_cases = list({json.dumps(x): x for x in edge_cases}.values())  # dedupe
        edge_cases = edge_cases[:25]  # limit to 25

    print(json.dumps(edge_cases, indent=2))
