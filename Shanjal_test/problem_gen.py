import importlib.util
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from pathlib import Path
from typing import TypedDict
from topics import select_topics
import subprocess
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

# === Graph State ===
class GraphState(TypedDict):
    instruction: str
    topics: list[str]
    generated_problem: str
    test_cases: list[str]
    cpp_codes: list[str]
    accepted: bool

# === LLM ===
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# === Step 1: Generate Problem ===
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
        "topics": topics,
        "accepted": False
    }
def interrupt(payload: dict) -> dict:
    print("\n === HUMAN FEEDBACK REQUIRED ===")
    print(payload["message"])

    # Show relevant content
    if "edge_cases" in payload:
        print("\nEdge Cases:")
        for i, case in enumerate(payload["edge_cases"], 1):
            print(f"\nCase {i}:\n{case}")
    elif "problem" in payload:
        print("\nGenerated Problem:\n")
        print(payload["problem"])

    # Ask for user feedback
    feedback = input("\n Enter feedback (or leave blank to accept): ").strip()
    return {"data": feedback}

# === Step 2: Generate Test Cases ===
def generate_test_cases_node(state: GraphState) -> GraphState:
    _, test_prompt_template = load_prompts()
    prompt = PromptTemplate.from_template(test_prompt_template)

    test_prompt = prompt.format(problem_statement=state["generated_problem"])
    result = llm.invoke(test_prompt)

    blocks = re.findall(
        r"Test Case \d+:\s*Input:\s*(.*?)\s*Expected Output:\s*(.*?)\s*Description:",
        result.content,
        re.DOTALL,
    )
    formatted = [f"{inp.strip()}\n{out.strip()}" for inp, out in blocks]
    return {**state, "test_cases": formatted}

# === Step 3: Generate and Validate C++ Code ===
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
        print("At least one C++ code passed.")
        return {**state, "cpp_codes": codes}
    else:
        print(" All 16 attempts failed.")
        for j, code in enumerate(codes):
            Path(f"qwen/run_{j+1}.cpp").write_text(code)
        return {**state, "cpp_codes": codes}


# === Step 4: Human Feedback (final review) ===
def human_feedback_node(state: dict) -> dict:
    payload = {
        "message": "Review everything generated (problem, test cases, and C++ codes). Leave empty to accept, or type feedback.",
        "problem": state.get("generated_problem", ""),
        "test_cases": state.get("test_cases", []),
        "cpp_code_sample": state.get("cpp_codes", ["<none>"])[0],
    }

    response = interrupt(payload)

    if isinstance(response, dict):
        feedback = str(response.get("data", "")).strip()
    else:
        feedback = str(response).strip()

    state["accepted"] = feedback == ""
    return state

# === Build LangGraph ===
builder = StateGraph(GraphState)

# Add all steps
builder.add_node("GenerateProblem", generate_problem_node)
builder.add_node("GenerateTestCases", generate_test_cases_node)
builder.add_node("Loop16", loop_generate_cpp_node)
builder.add_node("HumanFeedback", human_feedback_node)

# Set flow
builder.set_entry_point("GenerateProblem")
builder.add_edge("GenerateProblem", "GenerateTestCases")
builder.add_edge("GenerateTestCases", "Loop16")
builder.add_edge("Loop16", "HumanFeedback")
builder.add_edge("HumanFeedback", END)

# Compile app
app = builder.compile()

# Run
if __name__ == "__main__":
    initial_state: GraphState = {
        "instruction": "",
        "generated_problem": "",
        "test_cases": [],
        "cpp_codes": [],
        "topics": [],
        "accepted": False
    }
    asyncio.run(app.ainvoke(initial_state))
