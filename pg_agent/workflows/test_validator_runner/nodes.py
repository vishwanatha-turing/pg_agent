import os
import json
import shutil
from pathlib import Path
import tempfile
from .schemas import TestValidatorState
# Import the efficient suite runners
from ...pipeline.sandbox.sandbox_utils import run_generator_script, run_validation_suite, run_test_suite

def load_scripts_node(state: TestValidatorState) -> dict:
    """Loads the latest versions of all required C++ scripts from the automation directory."""
    print(f"--- Loading scripts from: {state['problem_dir_path']}/automation ---")
    problem_dir = Path(state['problem_dir_path'])
    automation_dir = problem_dir / "automation"
    settings_path = automation_dir / "automation_settings.json"

    if not settings_path.exists():
        raise FileNotFoundError("automation_settings.json not found. Please run previous workflows first.")

    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    
    def get_path(key, folder):
        version = settings.get(key, -1)
        if version == -1: raise FileNotFoundError(f"'{key}' not found in settings. Please run required workflows.")
        prefix = key.replace("Version", "")
        return str(automation_dir / folder / f"{prefix}_v{version}.cpp")

    bruteforce_path = get_path("bruteforceSolutionVersion", "bruteForceSol")
    small_test_gen_path = get_path("smallTestcaseGeneratorVersion", "testcaseGenScript")
    stress_test_gen_path = get_path("stressTestcaseGeneratorVersion", "testcaseGenScript")
    validator_path = get_path("testcaseValidatorVersion", "testcaseGenScript")
    
    run_dir = Path(tempfile.gettempdir()) / f"pg_agent_run_{os.urandom(4).hex()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created temporary run directory: {run_dir}")

    return {
        "bruteforce_path": bruteforce_path,
        "small_test_gen_path": small_test_gen_path,
        "stress_test_gen_path": stress_test_gen_path,
        "validator_path": validator_path,
        "run_dir_path": str(run_dir),
        "invalid_tests": []
    }

def run_generators_node(state: TestValidatorState) -> dict:
    """Runs the small and stress test case generator scripts in the sandbox."""
    print("--- Running test case generator scripts ---")
    run_dir = Path(state['run_dir_path'])
    
    print("  Generating small test cases...")
    small_tests_dir = run_dir / "small"
    small_tests_dir.mkdir()
    run_generator_script(state['small_test_gen_path'], small_tests_dir)
    
    print("  Generating stress test cases...")
    large_tests_dir = run_dir / "large"
    large_tests_dir.mkdir()
    run_generator_script(state['stress_test_gen_path'], large_tests_dir)
    
    print("Finished generating all test case inputs.")
    return {}

def validate_inputs_node(state: TestValidatorState) -> dict:
    """Runs the validator script against all generated and example .in files efficiently."""
    print("--- Validating all generated input files (Efficiently) ---")
    run_dir = Path(state['run_dir_path'])
    problem_dir = Path(state['problem_dir_path'])
    
    all_inputs = list((run_dir / "small").glob("*.in")) + \
                 list((run_dir / "large").glob("*.in")) + \
                 list((problem_dir / "test_cases").glob("example_*.in"))

    if not all_inputs:
        print("Warning: No input files found to validate.")
        return {"valid_small_tests": [], "valid_large_tests": [], "invalid_tests": []}

    valid_paths, invalid_dicts = run_validation_suite(state['validator_path'], all_inputs)

    valid_small_tests = []
    valid_large_tests = []
    for p in valid_paths:
        if "small" in str(p.parent) or "example" in p.name:
            valid_small_tests.append(str(p))
        elif "large" in str(p.parent):
            valid_large_tests.append(str(p))
            
    for invalid in invalid_dicts:
        print(f"  WARNING: Invalid test case file '{invalid['file']}'. Reason: {invalid['reason']}")

    print(f"Validation complete. Found {len(valid_small_tests)} valid small tests, {len(valid_large_tests)} valid large tests, and {len(invalid_dicts)} invalid files.")
    return {"valid_small_tests": valid_small_tests, "valid_large_tests": valid_large_tests, "invalid_tests": invalid_dicts}

# --- CORRECTED: This node is now much more efficient ---
def run_bruteforce_on_small_tests_node(state: TestValidatorState) -> dict:
    """Runs the bruteforce solution on all valid small tests efficiently in a single container."""
    print("--- Generating outputs for small test cases using bruteforce (Efficiently) ---")
    
    invalid_tests = state.get("invalid_tests", [])
    valid_small_test_paths = [Path(p) for p in state.get('valid_small_tests', [])]

    if not valid_small_test_paths:
        print("No valid small tests to run.")
        return {"valid_small_tests": [], "invalid_tests": invalid_tests}

    # Create a single temporary directory to hold all valid small tests
    with tempfile.TemporaryDirectory() as temp_small_test_dir_str:
        temp_small_test_dir = Path(temp_small_test_dir_str)
        
        # Copy all valid small test .in files to this single directory
        for in_file_path in valid_small_test_paths:
            shutil.copy(in_file_path, temp_small_test_dir)
            
        # Run the entire suite in one go
        run_test_suite(
            solution_path=state['bruteforce_path'],
            test_cases_dir=temp_small_test_dir,
            time_limit=state['bruteforce_time_limit']
        )
        
        # Now, process the results from the temp directory
        final_valid_small_tests = []
        for in_file_path in valid_small_test_paths:
            # The corresponding .out file was created in our temp directory
            out_file_in_temp = temp_small_test_dir / in_file_path.name.replace(".in", ".out")
            
            if out_file_in_temp.exists():
                content = out_file_in_temp.read_text(encoding="utf-8").strip()
                if content == "TIMEOUT":
                    print(f"  WARNING: Bruteforce timed out on '{in_file_path.name}'. Discarding.")
                    invalid_tests.append({"file": in_file_path.name, "reason": "Bruteforce Timed Out"})
                else:
                    # Copy the generated .out file back to the original location
                    shutil.copy(out_file_in_temp, in_file_path.with_suffix(".out"))
                    final_valid_small_tests.append(str(in_file_path))
            else:
                # This case handles runtime errors where an out file might not be created
                print(f"  WARNING: No output file for '{in_file_path.name}'. Assuming runtime error.")
                invalid_tests.append({"file": in_file_path.name, "reason": "Bruteforce Runtime Error"})

    print("Finished generating all outputs for valid small tests.")
    return {"valid_small_tests": final_valid_small_tests, "invalid_tests": invalid_tests}

def save_results_node(state: TestValidatorState) -> dict:
    """Copies the final, validated test suite into the problem's automation directory."""
    print("--- Saving final test suite to automation folder ---")
    run_dir = Path(state['run_dir_path'])
    automation_test_cases_dir = Path(state['problem_dir_path']) / "automation" / "testcases"
    automation_test_cases_dir.mkdir(parents=True, exist_ok=True)
    
    (automation_test_cases_dir / "small").mkdir(exist_ok=True)
    (automation_test_cases_dir / "large").mkdir(exist_ok=True)
    (automation_test_cases_dir / "example").mkdir(exist_ok=True)

    for test_path_str in state.get('valid_small_tests', []):
        test_path = Path(test_path_str)
        dest_dir = automation_test_cases_dir / "small"
        if "example" in test_path.name:
            dest_dir = automation_test_cases_dir / "example"
        if test_path.exists(): shutil.copy(test_path, dest_dir / test_path.name)
        out_path = test_path.with_suffix(".out")
        if out_path.exists(): shutil.copy(out_path, dest_dir / out_path.name)

    for test_path_str in state.get('valid_large_tests', []):
        test_path = Path(test_path_str)
        if test_path.exists(): shutil.copy(test_path, automation_test_cases_dir / "large" / test_path.name)

    invalid_log_path = automation_test_cases_dir / "invalid_testcases.json"
    invalid_log_path.write_text(json.dumps(state.get("invalid_tests", []), indent=2), encoding="utf-8")
            
    if run_dir.exists():
        shutil.rmtree(run_dir)
        
    print(f"Final test suite artifacts saved to {automation_test_cases_dir}. Temporary directory cleaned up.")
    return {"final_verdict": "SUCCESS"}
