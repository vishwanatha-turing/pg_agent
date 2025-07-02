import os
from pg_agent.pipeline.solution_validator_graph import solution_validator_graph
from pg_agent.pipeline.schemas import ValidationState

# --- Example Data for a C++ "Add Two Numbers" problem ---

PROBLEM_STATEMENT = "Given two integers on a single line, read them and print their sum."

# Example 1: An incorrect solution that subtracts instead of adds
SOLUTION_CODE_FAIL = """
#include <iostream>
int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a - b; // Incorrect logic: should be a + b
    return 0;
}
"""

# Example 2: A correct solution
SOLUTION_CODE_PASS = """
#include <iostream>
int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a + b;
    return 0;
}
"""

# This C++ code generates the test case input files (e.g., 1.in, 2.in, ...)
TEST_GENERATOR_CODE = """
#include <iostream>
#include <fstream>
#include <string>

int main() {
    // Create 3 simple test cases
    for (int i = 1; i <= 10; ++i) {
        std::ofstream outfile("testcases/" + std::to_string(i) + ".in");
        outfile << i * 2 << " " << i * 3 << std::endl; // e.g., "2 3", "4 6", "6 9"
        outfile.close();
    }
    return 0;
}
"""

# For this simple problem, the correct solution is also the bruteforce solution.
BRUTEFORCE_SOLUTION_CODE = SOLUTION_CODE_PASS

def run_test(state: ValidationState):
    """Helper function to invoke the graph and print results."""
    # Invoke the graph with the initial state
    result = solution_validator_graph.invoke(state)
    
    print("\n" + "="*50)
    print(f"Final Verdict: {result['verdict']}")
    
    # If the verdict is FAIL, print the critique and test details
    if result.get('critique'):
        print("\nCritique:")
        print("-" * 15)
        print(result['critique'])
    
    print("\nFull Test Details:")
    print("-" * 15)
    print(result['test_results']['details'])
    print("="*50 + "\n")


def main():
    """Main function to run the tests."""
    print("### 1. Running validator with an INCORRECT C++ solution ###")
    
    # Define the initial state for the failing test
    initial_state_fail: ValidationState = {
        "problem_statement": PROBLEM_STATEMENT,
        "solution_code": SOLUTION_CODE_FAIL,
        "test_generator_code": TEST_GENERATOR_CODE,
        "bruteforce_solution_code": BRUTEFORCE_SOLUTION_CODE,
        "test_results": None,
        "critique": None,
        "verdict": None,
    }
    
    run_test(initial_state_fail)

    print("\n### 2. Running validator with a CORRECT C++ solution ###")

    # Define the initial state for the passing test
    initial_state_pass: ValidationState = {
        "problem_statement": PROBLEM_STATEMENT,
        "solution_code": SOLUTION_CODE_PASS,
        "test_generator_code": TEST_GENERATOR_CODE,
        "bruteforce_solution_code": BRUTEFORCE_SOLUTION_CODE,
        "test_results": None,
        "critique": None,
        "verdict": None,
    }
    run_test(initial_state_pass)


if __name__ == "__main__":
    # --- Prerequisites ---
    # 1. Make sure Docker Desktop is running.
    # 2. Make sure you have the required Python packages:
    #    pip install docker langchain-anthropic langgraph
    # 3. Set your Anthropic API key as an environment variable:
    #    set ANTHROPIC_API_KEY=your_key_here  (on Windows)
    #    export ANTHROPIC_API_KEY=your_key_here (on Mac/Linux)
    main()