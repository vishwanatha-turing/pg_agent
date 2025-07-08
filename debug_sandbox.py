import os
import shutil
from pathlib import Path
from pg_agent.auto_solver_agent.nodes import run_test_case_generator_node, run_tests_node
from pg_agent.auto_solver_agent.schemas import SolverState

# --- Hardcoded C++ Code for Focused Debugging ---

BRUTEFORCE_CODE = """
#include <iostream>
#include <vector>
#include <numeric>

int main() {
    int n;
    std::cin >> n;
    std::vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        std::cin >> nums[i];
    }
    int target;
    std::cin >> target;

    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (nums[i] + nums[j] == target) {
                std::cout << i << " " << j << std::endl;
                return 0;
            }
        }
    }
    return 0;
}
"""

TEST_GENERATOR_CODE = """
#include <iostream>
#include <fstream>
#include <string>
#include <random>
#include <chrono>

int main() {
    unsigned seed = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    std::mt19937 gen(seed);
    std::uniform_int_distribution<int> distrib(-100, 100);

    for (int i = 1; i <= 5; ++i) {
        std::ofstream outfile(std::to_string(i) + ".in");
        int a = distrib(gen);
        int b = distrib(gen);
        outfile << 2 << std::endl;
        outfile << a << " " << b << std::endl;
        outfile << a + b << std::endl;
        outfile.close();
    }
    return 0;
}
"""

SOLUTION_CODE_PASS = BRUTEFORCE_CODE

def main():
    """A simplified script to debug the sandbox and test running nodes."""
    
    run_id = "debug_run_001"
    
    # --- Step 1: Test the Test Case Generation ---
    print("--- STEP 1: DEBUGGING TEST CASE GENERATION ---")
    
    # This state dictionary has only what the generator node needs
    gen_state: SolverState = {
        "run_id": run_id,
        "num_test_generations": 3,
        "test_generator_code": TEST_GENERATOR_CODE,
    }
    
    # Clean up previous debug runs if they exist
    debug_dir = Path("temp_runs") / run_id
    if debug_dir.exists():
        shutil.rmtree(debug_dir)
        print(f"Cleaned up old debug directory: {debug_dir}")

    gen_result = run_test_case_generator_node(gen_state)
    
    test_cases_path = gen_result.get("test_cases_dir_path")
    
    if not test_cases_path:
        print("\n--- DEBUG FAILED ---")
        print("Test case generation failed. Error details:")
        print(gen_result.get("test_results", {}).get("details"))
        return

    print(f"\nSUCCESS: Test cases seem to be generated at: {test_cases_path}")
    print("-------------------------------------------\n")


    # --- Step 2: Test the Solution Runner ---
    print("--- STEP 2: DEBUGGING SOLUTION RUNNER ---")
    
    # This state has only what the test runner node needs
    test_state: SolverState = {
        "test_cases_dir_path": test_cases_path,
        "solution_code": SOLUTION_CODE_PASS,
        "bruteforce_code": BRUTEFORCE_CODE,
        # iteration_count is needed by the node
        "iteration_count": 0, 
    }
    
    test_result = run_tests_node(test_state)
    
    if test_result.get("test_results", {}).get("failed", 0) > 0:
        print("\n--- DEBUG FAILED ---")
        print("Running tests failed. Error details:")
        print(test_result.get("test_results", {}).get("details"))
    else:
        print("\n--- DEBUG SUCCESS ---")
        print("All tests passed successfully!")
        print(f"Passed: {test_result.get('test_results', {}).get('passed')}")

    # Final cleanup
    if Path(test_cases_path).exists():
        shutil.rmtree(test_cases_path)
        print(f"Cleaned up final debug directory: {test_cases_path}")

if __name__ == "__main__":
    # Make sure Docker is running before executing
    main()