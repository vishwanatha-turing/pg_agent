import argparse
import os
import sys
from dotenv import load_dotenv


# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from pg_agent.workflows.brute_force_creator.graph import bruteforce_creator_graph
from pg_agent.workflows.brute_force_creator.schemas import BruteForceState
from pg_agent.workflows.test_case_generator.graph import test_case_generator_graph
from pg_agent.workflows.test_case_generator.schemas import TestCaseGeneratorState
from pg_agent.workflows.test_validator_runner.graph import test_validator_graph
from pg_agent.workflows.test_validator_runner.schemas import TestValidatorState

def run_bruteforce_creator(problem_dir: str):
    """Initializes and runs the bruteforce creator workflow."""
    print(f"--- Starting Workflow: create_brute_force for directory: {problem_dir} ---")
    initial_state: BruteForceState = {
        "problem_dir_path": problem_dir, "max_iterations": 5,
        "problem_statement": "", "example_test_cases": [],
        "bruteforce_code": None, "test_failures": None,
        "iteration_count": 0, "final_verdict": "PENDING",
        "final_bruteforce_path": None,
    }
    graph = bruteforce_creator_graph
    for event in graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    print("\n--- Workflow Finished ---")

def run_test_case_generator(problem_dir: str):
    """Initializes and runs the test case generator workflow."""
    print(f"--- Starting Workflow: generate_test_cases for directory: {problem_dir} ---")
    initial_state: TestCaseGeneratorState = {
        "problem_dir_path": problem_dir,
        "problem_statement": "",
        "bruteforce_code": "",
        "small_test_gen_path": None,
        "stress_test_gen_path": None,
        "validator_path": None,
        "final_verdict": "PENDING",
    }
    graph = test_case_generator_graph
    for event in graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    print("\n--- Workflow Finished ---")

def run_test_validator(problem_dir: str):
    """Initializes and runs the test validator and runner workflow."""
    print(f"--- Starting Workflow: validate_and_run_tests for directory: {problem_dir} ---")
    initial_state: TestValidatorState = {
        "problem_dir_path": problem_dir,
        "bruteforce_time_limit": 2.0,
        "bruteforce_path": "",
        "small_test_gen_path": "",
        "stress_test_gen_path": "",
        "validator_path": "",
        "run_dir_path": "",
        "valid_small_tests": None,
        "valid_large_tests": None,
        "invalid_tests": None, # <-- ADD THIS LINE
        "final_verdict": "PENDING",
    }
    graph = test_validator_graph
    for event in graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    print("\n--- Workflow Finished ---")

def main():
    """Parses command-line arguments and runs the selected workflow."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="PG-Agent Workflow Runner")
    parser.add_argument("--workflow", required=True, help="The name of the workflow to run.")
    parser.add_argument("--problem_dir", required=True, help="Path to the problem directory.")
    
    args = parser.parse_args()
    
    problem_dir_abs = os.path.abspath(args.problem_dir)
    if not os.path.isdir(problem_dir_abs):
        print(f"Error: Directory not found at '{problem_dir_abs}'")
        sys.exit(1)

    if args.workflow == "create_brute_force":
        run_bruteforce_creator(problem_dir_abs)
    elif args.workflow == "generate_test_cases":
        run_test_case_generator(problem_dir_abs)
    elif args.workflow == "validate_and_run_tests":
        run_test_validator(problem_dir_abs)
    else:
        print(f"Error: Unknown workflow '{args.workflow}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
