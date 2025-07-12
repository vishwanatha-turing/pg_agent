import os
import re
import json
from pathlib import Path
import tempfile 
import shutil 
import subprocess
import questionary
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# --- THIS IS THE FIX ---
# Import the correct, existing sandbox function
from ...pipeline.sandbox.sandbox_utils import run_single_test
from .schemas import BruteForceState

def _open_in_editor(file_path: Path):
    """Opens a file in the default text editor."""
    editor = os.environ.get('EDITOR', 'notepad' if os.name == 'nt' else 'vim')
    print(f"Opening {file_path.name} with '{editor}' for your review...")
    subprocess.run([editor, str(file_path)], check=True)

def _extract_cpp_code(response_content: str) -> str:
    match = re.search(r'```(?:cpp)?\s*([\s\S]+?)\s*```', response_content)
    if match: return match.group(1).strip()
    return response_content.strip()

def get_llm_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: raise ValueError("OPENAI_API_KEY not found in environment.")
    return ChatOpenAI(model="o4-mini", api_key=api_key, max_tokens=8192)

# --- Node Definitions ---

def load_problem_node(state: BruteForceState) -> dict:
    """Loads the problem statement and example test cases from the user's directory."""
    print(f"--- Loading problem from: {state['problem_dir_path']} ---")
    problem_dir = Path(state['problem_dir_path'])
    
    problem_statement = (problem_dir / "problem_statement.md").read_text(encoding="utf-8")
    
    examples = []
    test_cases_dir = problem_dir / "test_cases"
    if test_cases_dir.exists():
        for in_file in sorted(test_cases_dir.glob("example_*.in")):
            out_file = in_file.with_suffix(".out")
            if out_file.exists():
                examples.append({
                    "input": in_file.read_text(encoding="utf-8"),
                    "output": out_file.read_text(encoding="utf-8").strip(),
                    "name": in_file.name
                })
    
    print(f"Loaded problem statement and {len(examples)} example test cases.")
    return {"problem_statement": problem_statement, "example_test_cases": examples}

def gen_bruteforce_node(state: BruteForceState) -> dict:
    """Generates the initial bruteforce C++ solution."""
    print("--- Generating initial bruteforce solution ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/gen_bruteforce_from_problem.txt").read_text()) | get_llm_client()
    response = chain.invoke({"problem_statement": state["problem_statement"]})
    return {"bruteforce_code": _extract_cpp_code(response.content)}

def test_bruteforce_on_examples_node(state: BruteForceState) -> dict:
    """Tests the current bruteforce code against all loaded example cases."""
    print("--- Testing bruteforce against examples ---")
    failures = []
    if not state["example_test_cases"]:
        print("Warning: No example test cases found to validate against.")
        return {"test_failures": [], "iteration_count": state.get("iteration_count", 0) + 1}

    for i, example in enumerate(state["example_test_cases"]):
        print(f"  Running example #{i+1} ({example['name']})...")
        
        # --- THIS IS THE FIX ---
        # Use the correct sandbox function: run_single_test
        passed, actual_output = run_single_test(
            solution_code=state["bruteforce_code"],
            input_data=example["input"]
        )
        
        actual_output_stripped = actual_output.strip()

        # The run_single_test function doesn't have a timeout feature,
        # so we only check for correctness.
        if not passed or actual_output_stripped != example["output"]:
            failures.append({
                "example_number": i + 1, "input": example["input"],
                "expected_output": example["output"], "actual_output": actual_output_stripped
            })
    
    if failures:
        print(f"--- Test FAILED on {len(failures)} examples. ---")
    else:
        print("--- All examples PASSED. ---")
        
    return {
        "test_failures": failures,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def refine_bruteforce_node(state: BruteForceState) -> dict:
    """Refines the bruteforce code based on the failures."""
    print(f"--- Refining bruteforce solution (Attempt #{state['iteration_count']}) ---")
    chain = ChatPromptTemplate.from_template((Path(__file__).parent / "prompts/refine_bruteforce_from_examples.txt").read_text()) | get_llm_client()
    response = chain.invoke({
        "problem_statement": state["problem_statement"],
        "bruteforce_code": state["bruteforce_code"],
        "test_failures": json.dumps(state["test_failures"], indent=2),
    })
    return {"bruteforce_code": _extract_cpp_code(response.content)}

# --- NEW: Node for optional human review ---
def interactive_review_node(state: BruteForceState) -> dict:
    """Optionally allows the user to review and edit the generated code."""
    print("\n" + "="*60)
    wants_to_review = questionary.confirm(
        "A bruteforce solution has been generated. Would you like to review or edit it before testing?",
        default=False,
        qmark="?"
    ).ask()
    
    if not wants_to_review:
        print("--- Skipping review. Proceeding with AI-generated code. ---")
        return {}

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".cpp", encoding="utf-8") as tf:
        temp_code_path = Path(tf.name)
        tf.write(state["bruteforce_code"])
    
    _open_in_editor(temp_code_path)
    
    # Read the potentially modified code back
    modified_code = temp_code_path.read_text(encoding="utf-8")
    os.unlink(temp_code_path)
    
    print("--- Code updated with your changes. ---")
    return {"bruteforce_code": modified_code}

def save_and_version_node(state: BruteForceState) -> dict:
    """Saves the final correct code to the automation hub inside the problem directory."""
    print("--- Saving and versioning final bruteforce solution ---")
    problem_dir = Path(state['problem_dir_path'])
    automation_dir = problem_dir / "automation"
    automation_dir.mkdir(exist_ok=True)
    settings_path = automation_dir / "automation_settings.json"
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    else:
        settings = { "bruteforceSolutionVersion": -1 }
    version_key = "bruteforceSolutionVersion"
    new_version = settings.get(version_key, -1) + 1
    file_prefix = version_key.replace("Version", "")
    bf_dir = automation_dir / "bruteForceSol"
    bf_dir.mkdir(parents=True, exist_ok=True)
    final_path = bf_dir / f"{file_prefix}_v{new_version}.cpp"
    final_path.write_text(state["bruteforce_code"], encoding="utf-8")
    settings[version_key] = new_version
    settings_path.write_text(json.dumps(settings, indent=4), encoding="utf-8")
    print(f"Saved new version {new_version} to: {final_path}")
    return {"final_verdict": "SUCCESS", "final_bruteforce_path": str(final_path)}
