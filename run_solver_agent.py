import os
import sys
import uuid # Import the uuid library
from dotenv import load_dotenv
from pg_agent.auto_solver_agent.graph import auto_solver_graph
from pg_agent.auto_solver_agent.schemas import SolverState

load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    print("FATAL ERROR: ANTHROPIC_API_KEY not found in .env file or environment.")
    sys.exit(1)

PROBLEM_STATEMENT = """
Write a C++ program that solves the "Two Sum" problem.
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.
You may assume that each input would have exactly one solution, and you may not use the same element twice.
You can return the answer in any order.
Input Format:
The first line contains an integer `n`, the number of elements in the array.
The second line contains `n` space-separated integers.
The third line contains the integer `target`.
Output Format:
Print the two indices (0-based) separated by a space.
"""

def main():
    """Main function to run the auto-solver agent."""
    
    # Generate a unique ID for this run
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    print(f"Starting a new run with ID: {run_id}")
    
    initial_state: SolverState = {
        "problem_statement": PROBLEM_STATEMENT.strip(),
        "num_test_generations": 3,
        "max_iterations": 5,
        "run_id": run_id, # <-- RE-ADDED: Pass the unique ID into the state
        "bruteforce_code": None,
        "test_generator_code": None,
        "solution_code": None,
        "test_cases_dir_path": None,
        "test_results": None,
        "iteration_count": 0,
        "final_verdict": "PENDING",
    }
    
    print("--- Invoking Auto-Solver Agent ---")
    
    for event in auto_solver_graph.stream(initial_state):
        node_name = list(event.keys())[0]
        print(f"\n--- Finished Node: {node_name} ---")
    
    print("\n--- Agent Finished ---")

if __name__ == "__main__":
    main()