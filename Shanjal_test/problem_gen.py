# problem_gen.py

import importlib.util
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from pathlib import Path
from typing import TypedDict
import subprocess
import os
import re

# Ensure qwen folder exists
Path("qwen").mkdir(exist_ok=True)

# === Load the dictionary from problem_spec.py ===
def load_problem_spec():
    spec = importlib.util.spec_from_file_location("problem_spec", "problem_spec.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.problem_spec

# === Convert dictionary to prompt ===
def dict_to_instruction(spec: dict) -> str:
    lines = [f"### Problem Title:\n{spec.get('title')}\n"]
    meta = spec.get("metadata", {})
    lines.append("### Metadata:")
    for k, v in meta.items():
        lines.append(f"- {k.replace('_', ' ').capitalize()}: {v}")

    lines.append("\n### Requirements:")
    for req_name, req in spec.get("requirements", {}).items():
        lines.append(f"**{req_name.replace('_', ' ').capitalize()}**:")
        if isinstance(req, dict):
            for key, value in req.items():
                lines.append(f"- {key.capitalize()}: {value}")
        else:
            lines.append(f"- {req}")

    lines.append("\n### Output Format:")
    for item in spec.get("output_format", {}).get("constraints", []):
        lines.append(f"- {item}")

    lines.append("\n### Evaluation Criteria:")
    for k, v in spec.get("evaluation_criteria", {}).items():
        lines.append(f"- {k.capitalize()}: {v}")

    lines.append("\n### Misc Notes:")
    for k, v in spec.get("misc_notes", {}).items():
        if isinstance(v, list):
            lines.append(f"- {k.capitalize()}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"- {k.capitalize()}: {v}")

    return "\n".join(lines)

# === State ===
class GraphState(TypedDict):
    instruction: str
    generated_problem: str
    test_cases: list[str]
    cpp_codes: list[str]

# === Node 1: Generate Problem ===
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

template = PromptTemplate.from_template(
    "You are an expert CP problem setter. Based on the following spec, write a markdown problem:\n\n{instruction}\n\n---"
)

def generate_problem_node(state: GraphState) -> GraphState:
    spec_dict = load_problem_spec()
    instruction = dict_to_instruction(spec_dict)
    result = llm.invoke(template.format(instruction=instruction))
    Path("-problem.md").write_text(result.content, encoding="utf-8")
    return {"instruction": instruction, "generated_problem": result.content, "test_cases": [], "cpp_codes": []}

# === Node 2: Extract Test Cases from Markdown ===
def extract_tests_node(state: GraphState) -> GraphState:
    text = state["generated_problem"]
    samples = re.findall(r"Sample Input.*?```(?:[a-zA-Z]*\n)?(.*?)```.*?Sample Output.*?```(?:[a-zA-Z]*\n)?(.*?)```", text, re.DOTALL)
    cases = [(inp.strip(), out.strip()) for inp, out in samples]
    formatted = [f"{i}\n{o}" for i, o in cases]
    return {**state, "test_cases": formatted}

# === Node 3: Loop 16 GPT calls for C++ ===
def loop_generate_cpp_node(state: GraphState) -> GraphState:
    codes = []
    success = False

    for i in range(16):
        cpp_prompt = f"""
Generate C++14 or later code that solves the following problem:

{state['generated_problem']}

Ensure your solution handles all sample inputs correctly.
Output only code.
"""
        result = llm.invoke(cpp_prompt)
        code = result.content.strip()
        codes.append(code)

        # Save and test
        path = Path(f"temp_solution.cpp")
        path.write_text(code)

        exe = "temp_solution.exe"
        try:
            subprocess.run(["g++", "-std=c++14", "temp_solution.cpp", "-o", exe], check=True, timeout=5)
            all_pass = True
            for idx, sample in enumerate(state["test_cases"]):
                sample_in, sample_out = sample.split("\n", 1)
                proc = subprocess.run(f"{exe}", input=sample_in.encode(), capture_output=True, timeout=2)
                output = proc.stdout.decode().strip()
                if sample_out.strip() not in output:
                    all_pass = False
                    break
            if all_pass:
                success = True
                break
        except Exception as e:
            continue

    if success:
        print("✅ At least one C++ code passed. Regenerating new problem.")
        return {"instruction": state["instruction"], "generated_problem": "", "test_cases": [], "cpp_codes": []}
    else:
        print("❌ All 16 attempts failed. Saving to qwen folder.")
        for j, code in enumerate(codes):
            Path(f"qwen/attempt_{j+1}.cpp").write_text(code)
        return {**state, "cpp_codes": codes}

# === Build LangGraph ===
builder = StateGraph(GraphState)
builder.add_node("GenerateProblem", generate_problem_node)
builder.add_node("ExtractTests", extract_tests_node)
builder.add_node("Loop16", loop_generate_cpp_node)

builder.set_entry_point("GenerateProblem")
builder.add_edge("GenerateProblem", "ExtractTests")
builder.add_edge("ExtractTests", "Loop16")
builder.add_edge("Loop16", "GenerateProblem")  # Loop again if success

builder.add_edge("Loop16", END)  # END if all 16 fail

app = builder.compile()

if __name__ == "__main__":
    app.invoke({})