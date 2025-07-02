import os
from dotenv import load_dotenv
from pg_agent.auto_solver_agent.graph import auto_solver_graph
from pg_agent.auto_solver_agent.schemas import SolverState

# --- Load Environment Variables ---
print("Attempting to load .env file...")
load_dotenv()
print(".env file loaded (if it exists).")

# --- DEBUGGING CHECK ---
# We will now check if the environment variable was loaded successfully.
api_key = os.getenv("ANTHROPIC_API_KEY")
print("\n--- API Key Check ---")
if api_key:
    # For security, we only print the first few and last few characters.
    print(f"SUCCESS: Anthropic API Key found. It starts with '{api_key[:5]}' and ends with '{api_key[-4:]}'.")
else:
    print("FAILURE: Anthropic API Key was NOT found in the environment.")
    print("Please check the following:")
    print("1. Is the .env file in the same directory as this script?")
    print("2. Is the variable name exactly ANTHROPIC_API_KEY in the .env file?")
    print("3. Did you save the .env file?")
    # We exit here because the script is guaranteed to fail without the key.
    exit() # Stop the script
print("---------------------\n")


# --- Define the problem to solve ---
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
    
    initial_state: SolverState = {
        "problem_statement": PROBLEM_STATEMENT.strip(),
        "num_test_generations": 3,
        "max_iterations": 5,
        "bruteforce_code": None,
        "test_generator_code": None,
        "solution_code": None,
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