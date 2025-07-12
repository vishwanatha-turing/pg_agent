import argparse
import os
import sys
from dotenv import load_dotenv
import questionary

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from pg_agent.workflows.brute_force_creator.graph import bruteforce_creator_graph
from pg_agent.workflows.brute_force_creator.schemas import BruteForceState
from pg_agent.workflows.test_case_generator.graph import test_case_generator_graph
from pg_agent.workflows.test_case_generator.schemas import TestCaseGeneratorState
from pg_agent.workflows.test_validator_runner.graph import test_validator_graph
from pg_agent.workflows.test_validator_runner.schemas import TestValidatorState
from pg_agent.workflows.novel_problem_creator.graph import novel_problem_creator_graph
from pg_agent.workflows.novel_problem_creator.schemas import NovelProblemState

def run_bruteforce_creator(problem_dir):
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

def run_test_case_generator(problem_dir):
    print(f"--- Starting Workflow: generate_test_cases for directory: {problem_dir} ---")
    initial_state: TestCaseGeneratorState = {
        "problem_dir_path": problem_dir, "problem_statement": "", "bruteforce_code": "",
        "small_test_gen_path": None, "stress_test_gen_path": None,
        "validator_path": None, "final_verdict": "PENDING",
    }
    graph = test_case_generator_graph
    for event in graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    print("\n--- Workflow Finished ---")

def run_test_validator(problem_dir):
    print(f"--- Starting Workflow: validate_and_run_tests for directory: {problem_dir} ---")
    initial_state: TestValidatorState = {
        "problem_dir_path": problem_dir, "bruteforce_time_limit": 2.0,
        "bruteforce_path": "", "small_test_gen_path": "", "stress_test_gen_path": "",
        "validator_path": "", "run_dir_path": "", "valid_small_tests": None,
        "valid_large_tests": None, "invalid_tests": None, "final_verdict": "PENDING",
    }
    graph = test_validator_graph
    for event in graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    print("\n--- Workflow Finished ---")

def run_novel_problem_creator(output_dir):
    """Initializes and runs the novel problem creation workflow."""
    print(f"--- Starting Workflow: create_novel_problem for directory: {output_dir} ---")
    initial_state: NovelProblemState = {
        "output_dir": output_dir,
        "strategy": "", "topics": None, "user_prompt": None,
        "previous_problem": None, "problem_statement": "",
        "human_feedback": None, "test_cases": [],
    }
    graph = novel_problem_creator_graph
    try:
        for event in graph.stream(initial_state):
            node_name = list(event.keys())[0]
            print(f"\n--- Finished Node: {node_name} ---")
        print("\n--- Workflow Finished ---")
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user. Exiting.")

def main():
    """Parses command-line arguments and runs the selected workflow."""
    load_dotenv()
    
    # Master interactive menu
    try:
        workflow_choice = questionary.select(
            "Which workflow would you like to run?",
            choices=[
                "[1] Create a New Novel Problem from Scratch",
                "[2] Create a Bruteforce Solution for an Existing Problem",
                "[3] Generate Test Case Scripts for an Existing Problem",
                "[4] Validate and Run Test Cases for an Existing Problem",
                "Exit"
            ],
            qmark="?",
            pointer="»"
        ).ask()

        if not workflow_choice or workflow_choice == "Exit":
            print("Exiting.")
            sys.exit(0)

        if "[1]" in workflow_choice:
            output_dir = questionary.text("Please enter the path for the new problem directory:").ask()
            if not output_dir: raise KeyboardInterrupt
            run_novel_problem_creator(os.path.abspath(output_dir))

        elif "[2]" in workflow_choice or "[3]" in workflow_choice or "[4]" in workflow_choice:
            problem_dir = questionary.path("Please enter the path to the existing problem directory:").ask()
            if not problem_dir: raise KeyboardInterrupt
            
            problem_dir_abs = os.path.abspath(problem_dir)
            if not os.path.isdir(problem_dir_abs):
                print(f"Error: Directory not found at '{problem_dir_abs}'")
                sys.exit(1)

            if "[2]" in workflow_choice:
                run_bruteforce_creator(problem_dir_abs)
            elif "[3]" in workflow_choice:
                run_test_case_generator(problem_dir_abs)
            elif "[4]" in workflow_choice:
                run_test_validator(problem_dir_abs)
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()