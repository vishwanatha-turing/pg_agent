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
from pg_agent.workflows.novel_problem_creator.graph import novel_problem_creator_graph
from pg_agent.workflows.novel_problem_creator.schemas import NovelProblemState

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

def run_novel_problem_creator(args):
    """Initializes and runs the novel problem creation workflow."""
    print(f"--- Starting Workflow: create_novel_problem for directory: {args.output_dir} ---")
    initial_state: NovelProblemState = {
        "output_dir": args.output_dir,
        "topics": args.topics,
        "context_dir": args.context_dir,
        "user_prompt": args.user_prompt,
        "previous_problem": None,
        "problem_statement": "",
        "human_feedback": None,
        "test_cases": [],
    }
    graph = novel_problem_creator_graph
    for event in graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    print("\n--- Workflow Finished ---")


def run_novel_problem_creator(args):
    """Initializes and runs the novel problem creation workflow."""
    print(f"--- Starting Workflow: create_novel_problem for directory: {args.output_dir} ---")
    initial_state: NovelProblemState = {
        "output_dir": args.output_dir,
        "topics": args.topics,
        "context_dir": args.context_dir,
        "user_prompt": args.user_prompt,
        "previous_problem": None,
        "problem_statement": "",
        "human_feedback": None,
        "test_cases": [],
    }
    graph = novel_problem_creator_graph
    for event in graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    print("\n--- Workflow Finished ---")


def main():
    """Parses command-line arguments and runs the selected workflow."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="PG-Agent Workflow Runner")
    parser.add_argument("--workflow", required=True, help="The name of the workflow to run.")
    
    # Arguments for existing workflows
    parser.add_argument("--problem_dir", help="Path to the problem directory for existing workflows.")
    
    # Arguments for the new novel problem creator workflow
    parser.add_argument("--output_dir", help="Path to the output directory for the new problem.")
    parser.add_argument("--topics", help="Comma-separated list of topics for problem generation.")
    parser.add_argument("--context_dir", help="Path to a directory with a previous problem for context.")
    parser.add_argument("--user_prompt", help="A specific prompt or idea for the problem.")
    
    args = parser.parse_args()
    
    # Dispatch based on workflow name
    if args.workflow == "create_brute_force":
        if not args.problem_dir: parser.error("--problem_dir is required for this workflow.")
        run_bruteforce_creator(args)
    elif args.workflow == "generate_test_cases":
        if not args.problem_dir: parser.error("--problem_dir is required for this workflow.")
        run_test_case_generator(args)
    elif args.workflow == "validate_and_run_tests":
        if not args.problem_dir: parser.error("--problem_dir is required for this workflow.")
        run_test_validator(args)
    # --- NEW: Add the new workflow to the dispatcher ---
    elif args.workflow == "create_novel_problem":
        if not args.output_dir: parser.error("--output_dir is required for this workflow.")
        run_novel_problem_creator(args)
    else:
        print(f"Error: Unknown workflow '{args.workflow}'")
        sys.exit(1)

if __name__ == "__main__":
    main()