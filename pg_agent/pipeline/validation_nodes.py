import os
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from .schemas import ValidationState
from .sandbox.sandbox_utils import run_docker_sandbox

def sandbox_run_test(state: ValidationState) -> dict:
    """
    The LangGraph node that orchestrates the Docker-based C++ sandbox execution.
    """
    print("--- 🚀 Kicking off Sandbox Test Node ---")

    results = run_docker_sandbox(
        solution_code=state["solution_code"],
        test_generator_code=state["test_generator_code"],
        bruteforce_solution_code=state["bruteforce_solution_code"]
    )

    print(f"--- ✅ Sandbox Execution Finished ---")
    print(f"  Passed: {results.get('passed', 0)}, Failed: {results.get('failed', 0)}")

    return {"test_results": results}


def critique_node(state: ValidationState) -> dict:
    """
    Generates a critique of the failing C++ solution using an LLM.
    This node populates the 'critique' key in the state.
    """
    print("--- Generating Critique ---")
    if not state.get("test_results") or state["test_results"]["failed"] == 0:
        return {}

    prompt_path = Path(__file__).parent.parent / "prompts" / "critique.txt"

    if not os.path.exists(prompt_path):
         return {"critique": "Critique prompt file not found."}

    prompt_template = ChatPromptTemplate.from_template(prompt_path.read_text())

    model = ChatAnthropic(model="claude-3-haiku-20240307")
    chain = prompt_template | model

    response = chain.invoke({
        "problem": state["problem_statement"],
        "solution_code": state["solution_code"],
        "results": state["test_results"]["details"]
    })

    print("  Critique generated.")
    return {"critique": response.content}


def verdict_node(state: ValidationState) -> dict:
    """
    Makes the final PASS/FAIL verdict based on test results.
    This node populates the 'verdict' key in the state.
    """
    print("--- Making Verdict ---")
    verdict_status = "PASS" if state["test_results"]["failed"] == 0 else "FAIL"
    print(f"  Verdict: {verdict_status}")
    return {"verdict": verdict_status}