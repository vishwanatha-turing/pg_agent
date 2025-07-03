import os
import re
import shutil
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from ..pipeline.sandbox.sandbox_utils import generate_test_case_batches, run_solution_against_tests
from .schemas import SolverState

# --- Helper functions (unchanged) ---
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
    return ChatAnthropic(model="claude-3-7-sonnet-20250219", api_key=api_key, max_tokens=8192)

# --- Node Definitions (Updated to use state for path) ---

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

# --- NEW: Node to generate ONLY the test case generator code ---
def gen_test_case_code_node(state: SolverState) -> dict:
    """Generates the C++ code for the test case generator program."""
    print("--- Generating: test_generator_code ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/gen_test_case_generator.txt").read_text()) | get_llm_client()
    response = chain.invoke({"problem_statement": state["problem_statement"]})
    return {"test_generator_code": _extract_cpp_code(response.content)}

# --- NEW: Node to RUN the test case generator code in the sandbox ---
def run_test_case_generator_node(state: SolverState) -> dict:
    """Runs the generated code to create persistent test case batches."""
    print(f"--- Creating {state['num_test_generations']} batches of test cases ---")
    try:
        test_cases_dir = generate_test_case_batches(
            test_generator_code=state["test_generator_code"],
            num_batches=state['num_test_generations']
        )
        print(f"Test cases generated and stored at: {test_cases_dir}")
        # Return the path to be stored in the state
        return {"test_cases_dir_path": str(test_cases_dir)}
    except Exception as e:
        # If generation fails, we must stop the graph by reporting a failure
        return {"test_results": {"failed": 1, "details": f"FATAL: Could not generate test cases. Error: {e}"}}

def run_tests_node(state: SolverState) -> dict:
    """Runs the solution against the test cases from the path in the state."""
    print("--- 🚀 Running Sandbox Tests on All Batches ---")
    
    # Read the path from the state, not a global variable
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
    """Refines the solution code based on test failures."""
    print(f"--- Refining Solution (Attempt #{state['iteration_count'] + 1}) ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/refine_solution.txt").read_text()) | get_llm_client()
    response = chain.invoke({
        "problem_statement": state["problem_statement"],
        "solution_code": state["solution_code"],
        "test_results": state["test_results"]["details"],
    })
    return {"solution_code": _extract_cpp_code(response.content)}

def cleanup_node(state: SolverState) -> dict:
    """Saves files and cleans up the temporary test directory from the path in the state."""
    print("--- Cleaning Up and Saving Final State ---")
    
    # Read the path from the state for cleanup
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