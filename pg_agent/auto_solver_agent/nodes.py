import os
import shutil
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from ..pipeline.sandbox.sandbox_utils import generate_test_case_batches, run_solution_against_tests
from .schemas import SolverState

# --- Load the API Key Directly ---
# We load the key here once when the module is imported.
# This is guaranteed to happen in the main thread where the .env file was loaded.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

print("\n--- API Key Check ---")
if ANTHROPIC_API_KEY:
    # For security, we only print the first few and last few characters.
    print(f"SUCCESS: Anthropic API Key found. It starts with '{ANTHROPIC_API_KEY[:5]}' and ends with '{ANTHROPIC_API_KEY[-4:]}'.")
else:
    print("FAILURE: Anthropic API Key was NOT found in the environment.")
    print("Please check the following:")
    print("1. Is the .env file in the same directory as this script?")
    print("2. Is the variable name exactly ANTHROPIC_API_KEY in the .env file?")
    print("3. Did you save the .env file?")
    # We exit here because the script is guaranteed to fail without the key.
    exit()
# --- Pre-build Chains for each Node ---
# Now, we explicitly pass the api_key to the constructor.

# --- Chain for Bruteforce Generation ---
bruteforce_prompt_template = ChatPromptTemplate.from_template(
    (Path(__file__).parent / "prompts/gen_bruteforce_solution.txt").read_text()
)
bruteforce_chain = bruteforce_prompt_template | ChatAnthropic(model="claude-3-opus-20240229", api_key=ANTHROPIC_API_KEY)

def gen_bruteforce_node(state: SolverState) -> dict:
    """Generates the bruteforce C++ solution using its dedicated chain."""
    print("--- Generating: bruteforce_code ---")
    response = bruteforce_chain.invoke({"problem_statement": state["problem_statement"]})
    return {"bruteforce_code": response.content}


# --- Chain for Optimal Solution Generation ---
optimal_prompt_template = ChatPromptTemplate.from_template(
    (Path(__file__).parent / "prompts/gen_optimal_solution.txt").read_text()
)
optimal_chain = optimal_prompt_template | ChatAnthropic(model="claude-3-opus-20240229", api_key=ANTHROPIC_API_KEY)

def gen_optimal_solution_node(state: SolverState) -> dict:
    """Generates the initial optimal C++ solution using its dedicated chain."""
    print("--- Generating: solution_code ---")
    response = optimal_chain.invoke({"problem_statement": state["problem_statement"]})
    return {"solution_code": response.content}


# --- Chain for Test Case Generator Code ---
test_gen_prompt_template = ChatPromptTemplate.from_template(
    (Path(__file__).parent / "prompts/gen_test_case_generator.txt").read_text()
)
test_gen_chain = test_gen_prompt_template | ChatAnthropic(model="claude-3-opus-20240229", api_key=ANTHROPIC_API_KEY)

# Keep a global reference to the test cases directory path
TEST_CASES_DIR = None

def gen_and_run_test_cases_node(state: SolverState) -> dict:
    """Generates the test case generator code AND runs it to create persistent test batches."""
    global TEST_CASES_DIR
    print("--- Generating: test_generator_code ---")
    
    response = test_gen_chain.invoke({"problem_statement": state["problem_statement"]})
    test_gen_code = response.content
    
    print(f"--- Creating {state['num_test_generations']} batches of test cases ---")
    try:
        if TEST_CASES_DIR and Path(TEST_CASES_DIR).exists():
            shutil.rmtree(TEST_CASES_DIR)
            
        TEST_CASES_DIR = generate_test_case_batches(
            test_generator_code=test_gen_code,
            num_batches=state['num_test_generations']
        )
        print(f"Test cases generated and stored at: {TEST_CASES_DIR}")
    except Exception as e:
        return {"test_results": {"failed": 1, "details": f"FATAL: Could not generate test cases. Error: {e}"}}

    return {"test_generator_code": test_gen_code}


# --- Node for running tests (no LLM, so no chain needed) ---
def run_tests_node(state: SolverState) -> dict:
    """Runs the solution against all persistent test case batches."""
    global TEST_CASES_DIR
    print("--- 🚀 Running Sandbox Tests on All Batches ---")

    if not TEST_CASES_DIR or not Path(TEST_CASES_DIR).exists():
        return {"test_results": {"failed": 1, "details": "FATAL: Test cases directory not found."}}

    results = run_solution_against_tests(
        solution_code=state["solution_code"],
        bruteforce_code=state["bruteforce_code"],
        test_cases_dir=TEST_CASES_DIR
    )
    
    print(f"--- ✅ Sandbox Finished: Passed: {results['passed']}, Failed: {results['failed']} ---")
    return {
        "test_results": results,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


# --- Chain for Refining the Solution ---
refine_prompt_template = ChatPromptTemplate.from_template(
    (Path(__file__).parent / "prompts/refine_solution.txt").read_text()
)
refine_chain = refine_prompt_template | ChatAnthropic(model="claude-3-opus-20240229", api_key=ANTHROPIC_API_KEY)

def refine_solution_node(state: SolverState) -> dict:
    """Refines the solution code based on test failures using its dedicated chain."""
    print(f"--- Refining Solution (Attempt #{state['iteration_count'] + 1}) ---")
    response = refine_chain.invoke({
        "problem_statement": state["problem_statement"],
        "solution_code": state["solution_code"],
        "test_results": state["test_results"]["details"],
    })
    return {"solution_code": response.content}


# --- Node for cleanup (no LLM) ---
def cleanup_node(state: SolverState) -> dict:
    """Cleans up temporary directories and sets final verdict."""
    global TEST_CASES_DIR
    print("--- Cleaning Up and Finalizing ---")
    
    if TEST_CASES_DIR and Path(TEST_CASES_DIR).exists():
        shutil.rmtree(TEST_CASES_DIR)
        print(f"Removed temporary test directory: {TEST_CASES_DIR}")
        TEST_CASES_DIR = None
    
    verdict = "SUCCESS" if state["test_results"]["failed"] == 0 else "FAILURE"
    
    if verdict == "SUCCESS":
        problem_name = state["problem_statement"].split('\n')[0].replace(' ', '_').lower()[:50]
        output_dir = Path("solved_problems") / problem_name
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "problem_statement.md").write_text(state["problem_statement"])
        (output_dir / "solution.cpp").write_text(state["solution_code"])
        (output_dir / "bruteforce.cpp").write_text(state["bruteforce_code"])
        (output_dir / "test_generator.cpp").write_text(state["test_generator_code"])
        print(f"Files saved to: {output_dir}")
        
    return {"final_verdict": verdict}