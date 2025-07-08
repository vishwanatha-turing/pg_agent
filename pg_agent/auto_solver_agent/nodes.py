import os
import re
import shutil
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from ..pipeline.sandbox.sandbox_utils import generate_test_case_batches, run_solution_against_tests
from .schemas import SolverState

# Helper functions...
def _extract_cpp_code(response_content: str) -> str:
    match = re.search(r'```(?:[a-zA-Z\+]+)?\s*([\s\S]+?)\s*```', response_content)
    if match: return match.group(1).strip()
    return response_content.strip()

def _sanitize_filename(text: str) -> str:
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = text.replace(' ', '_')
    return text.lower()[:50]

def get_llm_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment for this node.")
    return ChatAnthropic(
        model="claude-3-7-sonnet-20250219",
        api_key=api_key,
        max_tokens=8192
    )

# Node definitions...
def gen_bruteforce_node(state: SolverState) -> dict:
    print("--- Generating: bruteforce_code ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/gen_bruteforce_solution.txt").read_text()) | get_llm_client()
    response = chain.invoke({"problem_statement": state["problem_statement"]})
    return {"bruteforce_code": _extract_cpp_code(response.content)}

def gen_optimal_solution_node(state: SolverState) -> dict:
    print("--- Generating: solution_code ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/gen_optimal_solution.txt").read_text()) | get_llm_client()
    response = chain.invoke({"problem_statement": state["problem_statement"]})
    return {"solution_code": _extract_cpp_code(response.content)}

def gen_test_case_code_node(state: SolverState) -> dict:
    print("--- Generating: test_generator_code ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/gen_test_case_generator.txt").read_text()) | get_llm_client()
    response = chain.invoke({"problem_statement": state["problem_statement"]})
    return {"test_generator_code": _extract_cpp_code(response.content)}

def run_test_case_generator_node(state: SolverState) -> dict:
    """Creates a persistent run directory and generates test cases inside it."""
    print(f"--- Creating {state['num_test_generations']} batches of test cases ---")
    
    # This node must use the run_id from the state to create the directory
    run_dir = Path("temp_runs") / state["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        generate_test_case_batches(
            test_generator_code=state["test_generator_code"],
            num_batches=state['num_test_generations'],
            output_dir=run_dir
        )
        print(f"Test cases generated and stored at: {run_dir}")
        return {"test_cases_dir_path": str(run_dir)}
    except Exception as e:
        return {"test_results": {"failed": 1, "details": f"FATAL: Could not generate test cases. Error: {e}"}}

def run_tests_node(state: SolverState) -> dict:
    print("--- 🚀 Running Sandbox Tests on All Batches ---")
    test_cases_dir = state.get("test_cases_dir_path")
    if not test_cases_dir or not Path(test_cases_dir).exists():
        return {"test_results": {"failed": 1, "details": "FATAL: Test cases directory path not found in state or directory does not exist."}}
    results = run_solution_against_tests(
        solution_code=state["solution_code"],
        bruteforce_code=state["bruteforce_code"],
        test_cases_dir=Path(test_cases_dir)
    )
    print(f"--- ✅ Sandbox Finished: Passed: {results['passed']}, Failed: {results['failed']} ---")
    return {"test_results": results, "iteration_count": state.get("iteration_count", 0) + 1}

def refine_solution_node(state: SolverState) -> dict:
    print(f"--- Refining Solution (Attempt #{state['iteration_count'] + 1}) ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/refine_solution.txt").read_text()) | get_llm_client()
    response = chain.invoke({
        "problem_statement": state["problem_statement"],
        "solution_code": state["solution_code"],
        "test_results": state["test_results"]["details"],
    })
    return {"solution_code": _extract_cpp_code(response.content)}

def cleanup_node(state: SolverState) -> dict:
    print("--- Cleaning Up and Saving Final State ---")
    test_cases_dir_path = state.get("test_cases_dir_path")
    verdict = "SUCCESS" if state.get("test_results", {}).get("failed", 1) == 0 else "FAILURE"
    
    problem_name = _sanitize_filename(state["problem_statement"].split('\n')[0])
    output_dir = Path("solved_problems") / f"{problem_name}_{verdict}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving all generated files to: {output_dir}")

    if state.get("problem_statement"): (output_dir / "problem_statement.md").write_text(state["problem_statement"])
    if state.get("solution_code"): (output_dir / "solution.cpp").write_text(state["solution_code"])
    if state.get("bruteforce_code"): (output_dir / "bruteforce.cpp").write_text(state["bruteforce_code"])
    if state.get("test_generator_code"): (output_dir / "test_generator.cpp").write_text(state["test_generator_code"])

    if test_cases_dir_path and Path(test_cases_dir_path).exists():
        test_case_dest = output_dir / "testcases"
        if test_case_dest.exists(): shutil.rmtree(test_case_dest)
        shutil.copytree(test_cases_dir_path, test_case_dest)
        print(f"Saved test cases to: {test_case_dest}")
        shutil.rmtree(test_cases_dir_path)
        print(f"Removed temporary test directory: {test_cases_dir_path}")
        
    return {"final_verdict": verdict}