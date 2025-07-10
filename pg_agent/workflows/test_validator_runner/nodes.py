import os
import json
import shutil
from pathlib import Path
import tempfile
from .schemas import TestValidatorState
from ...pipeline.sandbox.sandbox_utils import run_generator_script, run_validator_script, run_solution_on_test_case

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
        "invalid_tests": [] # Initialize the list of invalid tests
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
    """Runs the validator script against all generated and example .in files."""
    print("--- Validating all generated input files ---")
    run_dir = Path(state['run_dir_path'])
    problem_dir = Path(state['problem_dir_path'])
    
    valid_small_tests = []
    valid_large_tests = []
    invalid_tests = []
    
    # Combine user examples with generated files for validation
    all_inputs = list((run_dir / "small").glob("*.in")) + \
                 list((run_dir / "large").glob("*.in")) + \
                 list((problem_dir / "test_cases").glob("example_*.in"))

    for in_file in all_inputs:
        print(f"  Validating {in_file.name}...")
        is_valid, error_msg = run_validator_script(state['validator_path'], in_file)
        if is_valid:
            if "small" in str(in_file.parent):
                valid_small_tests.append(str(in_file))
            elif "large" in str(in_file.parent):
                valid_large_tests.append(str(in_file))
            elif "example" in in_file.name:
                valid_small_tests.append(str(in_file))
        else:
            print(f"  WARNING: Invalid test case file '{in_file.name}'. Discarding. Reason: {error_msg}")
            invalid_tests.append({"file": in_file.name, "reason": f"Invalid Format: {error_msg}"})
            # We no longer delete the file, just log it as invalid.

    print(f"Validation complete. Found {len(valid_small_tests)} valid small tests, {len(valid_large_tests)} valid large tests, and {len(invalid_tests)} invalid files.")
    return {"valid_small_tests": valid_small_tests, "valid_large_tests": valid_large_tests, "invalid_tests": invalid_tests}

def run_bruteforce_on_small_tests_node(state: TestValidatorState) -> dict:
    """Runs the bruteforce solution on all valid small tests to generate .out files."""
    print("--- Generating outputs for small test cases using bruteforce ---")
    
    final_valid_small_tests = []
    # Get the current list of invalid tests to append to it
    invalid_tests = state.get("invalid_tests", [])

    for in_file_path_str in state['valid_small_tests']:
        in_file = Path(in_file_path_str)
        print(f"  Running bruteforce on {in_file.name}...")
        
        timed_out, output = run_solution_on_test_case(
            solution_path=state['bruteforce_path'],
            input_file=in_file,
            time_limit=state['bruteforce_time_limit']
        )
        
        if timed_out:
            print(f"  WARNING: Bruteforce timed out on '{in_file.name}'. Discarding this test case.")
            invalid_tests.append({"file": in_file.name, "reason": "Bruteforce Timed Out"})
        else:
            # Create the corresponding .out file
            out_file = in_file.with_suffix(".out")
            out_file.write_text(output, encoding="utf-8")
            final_valid_small_tests.append(in_file_path_str)
            
    print("Finished generating all outputs for valid small tests.")
    # Update the state with the final lists of valid and invalid tests
    return {"valid_small_tests": final_valid_small_tests, "invalid_tests": invalid_tests}

def save_results_node(state: TestValidatorState) -> dict:
    """Copies the final, validated test suite into the problem's automation directory."""
    print("--- Saving final test suite to automation folder ---")
    run_dir = Path(state['run_dir_path'])
    automation_test_cases_dir = Path(state['problem_dir_path']) / "automation" / "testcases"
    automation_test_cases_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for clarity
    (automation_test_cases_dir / "small").mkdir(exist_ok=True)
    (automation_test_cases_dir / "large").mkdir(exist_ok=True)
    (automation_test_cases_dir / "example").mkdir(exist_ok=True)

    # Copy valid small tests and their generated outputs
    for test_path_str in state.get('valid_small_tests', []):
        test_path = Path(test_path_str)
        if "example" in test_path.name:
            dest_dir = automation_test_cases_dir / "example"
        else:
            dest_dir = automation_test_cases_dir / "small"
        
        if test_path.exists(): shutil.copy(test_path, dest_dir / test_path.name)
        out_path = test_path.with_suffix(".out")
        if out_path.exists(): shutil.copy(out_path, dest_dir / out_path.name)

    # Copy valid large tests (only .in files)
    for test_path_str in state.get('valid_large_tests', []):
        test_path = Path(test_path_str)
        if test_path.exists(): shutil.copy(test_path, automation_test_cases_dir / "large" / test_path.name)

    # Save the list of invalid tests for auditing
    invalid_log_path = automation_test_cases_dir / "invalid_testcases.json"
    invalid_log_path.write_text(json.dumps(state.get("invalid_tests", []), indent=2), encoding="utf-8")
            
    # Clean up the temporary run directory
    if run_dir.exists():
        shutil.rmtree(run_dir)
        
    print(f"Final test suite artifacts saved to {automation_test_cases_dir}. Temporary directory cleaned up.")
    return {"final_verdict": "SUCCESS"}
