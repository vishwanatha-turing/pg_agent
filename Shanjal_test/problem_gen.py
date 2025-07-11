import importlib.util
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from pathlib import Path
from typing import TypedDict
from topics import select_topics
import subprocess
import os
import re
import asyncio

# Ensure qwen folder exists
Path("qwen").mkdir(exist_ok=True)

# === Load prompts from problem_spec.py ===
def load_prompts():
    spec = importlib.util.spec_from_file_location("problem_spec", "problem_spec.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GENERATE_PROBLEM_STATEMENT_PROMPT, module.GENERATE_TEST_CASES_PROMPT

# === State ===
class GraphState(TypedDict):
    instruction: str
    topics: list[str]
    generated_problem: str
    test_cases: list[str]
    cpp_codes: list[str]

# === Node 1: Generate Problem ===
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

def generate_problem_node(state: GraphState) -> GraphState:
    problem_prompt, _ = load_prompts()
    topics = select_topics()
    instruction = "Create a high-quality competitive programming problem."
    prompt = PromptTemplate.from_template(problem_prompt)

    formatted_prompt = prompt.format(
        topics=", ".join(topics),
        previous_problem="None",
        user_prompt=instruction
    )

    result = llm.invoke(formatted_prompt)
    Path("-problem.md").write_text(result.content, encoding="utf-8")
    return {
        "instruction": instruction,
        "generated_problem": result.content,
        "test_cases": [],
        "cpp_codes": [],
        "topics": topics
    }

# === Node 2: Generate Test Cases using Prompt ===
def generate_test_cases_node(state: GraphState) -> GraphState:
    _, test_prompt_template = load_prompts()
    prompt = PromptTemplate.from_template(test_prompt_template)

    test_prompt = prompt.format(problem_statement=state["generated_problem"])
    result = llm.invoke(test_prompt)

    # Extract test cases using format from output
    blocks = re.findall(
        r"Test Case \d+:\s*Input:\s*(.*?)\s*Expected Output:\s*(.*?)\s*Description:",
        result.content,
        re.DOTALL,
    )
    formatted = [f"{inp.strip()}\n{out.strip()}" for inp, out in blocks]
    return {**state, "test_cases": formatted}

# === Node 3: Generate and Validate C++ Code ===
async def generate_and_test_single_code(index: int, problem: str, test_cases: list[str]) -> tuple[str, bool]:
    llm_local = ChatOpenAI(model="gpt-4o", temperature=0.7)
    cpp_prompt = f"""
Generate C++14 or later code that solves the following problem:

{problem}

Ensure your solution handles all sample inputs correctly.
Output only code.
"""
    result = await llm_local.ainvoke(cpp_prompt)
    code = result.content.strip()

    path = Path(f"qwen/attempt_{index+1}.cpp")
    path.write_text(code)
    exe = f"qwen/attempt_{index+1}.exe"

    try:
        subprocess.run(["g++", "-std=c++14", str(path), "-o", exe], check=True, timeout=10)
        for sample in test_cases:
            sample_in, sample_out = sample.split("\n", 1)
            proc = subprocess.run(f"{exe}", input=sample_in.encode(), capture_output=True, timeout=2)
            output = proc.stdout.decode().strip()
            if sample_out.strip() not in output:
                return code, False
        return code, True
    except Exception:
        return code, False

async def loop_generate_cpp_node(state: GraphState) -> GraphState:
    print("Generating 16 C++ codes in parallel...")
    tasks = [generate_and_test_single_code(i, state["generated_problem"], state["test_cases"]) for i in range(16)]
    results = await asyncio.gather(*tasks)

    codes = [code for code, _ in results]
    any_passed = any(passed for _, passed in results)

    if any_passed:
        print(" At least one C++ code passed.")
        return {**state, "cpp_codes": codes}
    else:
        print(" All 16 attempts failed. Saving to qwen folder.")
        for j, code in enumerate(codes):
            Path(f"qwen/attempt_{j+1}.cpp").write_text(code)
        return {**state, "cpp_codes": codes, "end": True}

# === Build LangGraph ===
builder = StateGraph(GraphState)
builder.add_node("Load Prompt", generate_problem_node)
builder.add_node("Extract Testcases", generate_test_cases_node)
builder.add_node("Loop16", loop_generate_cpp_node)

builder.set_entry_point("Load Prompt")
builder.add_edge("Load Prompt", "Extract Testcases")
builder.add_edge("Extract Testcases", "Loop16")
builder.add_conditional_edges("Loop16", lambda x: "Load Prompt" if not x.get("end") else END)

app = builder.compile()

if __name__ == "__main__":
    initial_state: GraphState = {
        "instruction": "",
        "generated_problem": "",
        "test_cases": [],
        "cpp_codes": [],
        "topics": []
    }
    asyncio.run(app.ainvoke(initial_state))
