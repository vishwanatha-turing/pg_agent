import os
import shutil
from pathlib import Path
from pg_agent.auto_solver_agent.nodes import run_test_case_generator_node, run_tests_node
from pg_agent.auto_solver_agent.schemas import SolverState

# --- Hardcoded C++ Code for Focused Debugging ---

BRUTEFORCE_CODE = """
#include <iostream>
#include <vector>

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);
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
#include <vector>
#include <random>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <set>

int main() {
    unsigned seed = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    std::mt19937 gen(seed);
    std::uniform_int_distribution<int> size_distrib(10, 50);

    for (int i = 1; i <= 10; ++i) {
        std::ofstream outfile(std::to_string(i) + ".in");
        int n = size_distrib(gen);
        
        std::set<int> unique_nums_set;
        std::uniform_int_distribution<int> val_distrib(-500, 500);
        while(unique_nums_set.size() < n) {
            unique_nums_set.insert(val_distrib(gen));
        }
        
        std::vector<int> nums(unique_nums_set.begin(), unique_nums_set.end());
        std::shuffle(nums.begin(), nums.end(), gen);

        int idx1 = std::uniform_int_distribution<int>(0, n - 2)(gen);
        int idx2 = std::uniform_int_distribution<int>(idx1 + 1, n - 1)(gen);
        int target = nums[idx1] + nums[idx2];

        outfile << n << std::endl;
        for(int j=0; j<n; ++j) {
            outfile << nums[j] << " ";
        }
        outfile << std::endl;
        outfile << target << std::endl;
        outfile.close();
    }
    return 0;
}
"""

# --- UPDATED SOLUTION CODE ---
# This version now guarantees the output indices are sorted, making the
# output canonical and directly comparable to the bruteforce solution.
SOLUTION_CODE_PASS = """
#include <iostream>
#include <vector>
#include <unordered_map>
#include <algorithm> // Required for std::min and std::max

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int n;
    std::cin >> n;
    std::vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        std::cin >> nums[i];
    }
    int target;
    std::cin >> target;

    std::unordered_map<int, int> numMap;
    for (int i = 0; i < n; ++i) {
        int complement = target - nums[i];
        if (numMap.count(complement)) {
            // Ensure the smaller index is always printed first.
            int first_index = std::min(numMap[complement], i);
            int second_index = std::max(numMap[complement], i);
            std::cout << first_index << " " << second_index << std::endl;
            return 0;
        }
        numMap[nums[i]] = i;
    }
    return 0;
}
"""

def main():
    """A simplified script to debug the sandbox and test running nodes."""
    
    run_id = "debug_run_004"
    
    print("--- STEP 1: DEBUGGING TEST CASE GENERATION ---")
    gen_state: SolverState = {
        "bruteforce_time_limit" : 60,
        "run_id": run_id,
        "num_test_generations": 3,
        "test_generator_code": TEST_GENERATOR_CODE,
    }
    
    debug_dir = Path("temp_runs") / run_id
    if debug_dir.exists():
        shutil.rmtree(debug_dir)
        print(f"Cleaned up old debug directory: {debug_dir}")

    gen_result = run_test_case_generator_node(gen_state)
    test_cases_path = gen_result.get("test_cases_dir_path")
    
    if not test_cases_path:
        print("\n--- DEBUG FAILED (STEP 1) ---")
        print(gen_result.get("test_results", {}).get("details"))
        return

    print(f"\nSUCCESS: Test cases generated at: {test_cases_path}")
    print("-------------------------------------------\n")

    print("--- STEP 2: DEBUGGING SOLUTION RUNNER ---")
    
    test_state: SolverState = {
        "test_cases_dir_path": test_cases_path,
        "solution_code": SOLUTION_CODE_PASS,
        "bruteforce_code": BRUTEFORCE_CODE,
        "iteration_count": 0, 
    }
    
    test_result = run_tests_node(test_state)
    
    if test_result.get("test_results", {}).get("failed", 0) > 0:
        print("\n--- DEBUG FAILED (STEP 2) ---")
        print(test_result.get("test_results", {}).get("details"))
    else:
        print("\n--- DEBUG SUCCESS ---")
        print("All tests passed successfully!")
        print(f"Passed: {test_result.get('test_results', {}).get('passed')}")

    if Path(test_cases_path).exists():
        shutil.rmtree(test_cases_path)
        print(f"Cleaned up final debug directory: {test_cases_path}")

if __name__ == "__main__":
    main()