from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from generate_testcase_prompt import GENERATE_TESTCASE_PROMPT

from dotenv import load_dotenv
import os

# Load variables from .env file into environment
load_dotenv()

# Access the key (optional check)
assert os.getenv("OPENAI_API_KEY"), "❌ OPENAI_API_KEY not found in .env"

# Step 1: Load problem from file
def load_problem_node(state: dict) -> dict:
    print("[LoadProblem] Reading input.txt...")
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            problem = f.read().strip()
    except FileNotFoundError:
        raise ValueError("❌ input.txt not found")

    new_state = dict(state)
    new_state["problem_statement"] = problem
    new_state["round"] = 1  # start round counter
    return new_state


# Step 2: Generate test cases
def generate_testcases_node(state: dict) -> dict:
    round_num = state.get("round", 1)
    print(f"[GenerateTestCases] ROUND {round_num}")

    if "problem_statement" not in state:
        raise ValueError("Missing problem_statement in state")

    prompt_template = state.get("custom_prompt", GENERATE_TESTCASE_PROMPT)
    prompt = PromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI(model="gpt-4")  # or gpt-4o
    chain = LLMChain(llm=llm, prompt=prompt)

    result = chain.invoke({"problem_statement": state["problem_statement"]})

    new_state = dict(state)
    new_state["generated_testcases"] = result
    return new_state


# Step 3: Human feedback loop
def human_feedback_node(state: dict) -> dict:
    instruction = state.get("feedback_instruction", "").strip()
    new_state = dict(state)
    new_state["round"] = state.get("round", 1) + 1

    if instruction:
        custom_prompt = f"""You are a test case generator. Use the following user instruction to guide your generation:

User Instruction:
{instruction}

Now, generate 55-60 high-quality test cases for the following problem:

{{problem_statement}}
"""
        new_state["custom_prompt"] = custom_prompt
        new_state["has_feedback"] = True
    else:
        new_state["has_feedback"] = False

    return new_state



# Decide: loop or end
def decide_next_node(state: dict) -> str:
    return "GenerateTestCases" if state.get("has_feedback") else END


# Build graph
builder = StateGraph(dict)
builder.add_node("LoadProblem", load_problem_node)
builder.add_node("GenerateTestCases", generate_testcases_node)
builder.add_node("HumanFeedback", human_feedback_node)

builder.set_entry_point("LoadProblem")
builder.add_edge("LoadProblem", "GenerateTestCases")
builder.add_edge("GenerateTestCases", "HumanFeedback")
builder.add_conditional_edges("HumanFeedback", decide_next_node)

app = builder.compile()

# CLI runner
if __name__ == "__main__":
    final_state = app.invoke({})
    print("\n🎯 FINAL GENERATED TEST CASES\n")
    print(final_state.get("generated_testcases", "No test cases generated"))
