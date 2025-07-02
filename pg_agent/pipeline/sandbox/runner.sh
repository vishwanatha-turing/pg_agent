#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

MODE=$1
GENERATION_ID=$2

# --- COMPILE STAGE ---
# This is always required, regardless of mode.
echo "Compiling C++ source files..."
g++ -std=c++14 -O2 -o testcaseGenerator testcaseGenerator.cpp
g++ -std=c++14 -O2 -o bruteforce bruteforce.cpp
g++ -std=c++14 -O2 -o suspectedSolution suspectedSolution.cpp
echo "Compilation successful."


if [ "$MODE" = "generate" ]; then
    # --- GENERATION MODE ---
    # Creates one batch of test cases in a specific directory.
    echo "--- Mode: GENERATE (Batch #${GENERATION_ID}) ---"
    
    OUTPUT_DIR="testcases/generation${GENERATION_ID}"
    mkdir -p "$OUTPUT_DIR"
    
    # We need to change directory so the generator code can write locally
    cd "$OUTPUT_DIR"
    ../../testcaseGenerator # Run the generator from the new directory
    
    echo "Test cases generated in ${OUTPUT_DIR}"

elif [ "$MODE" = "execute" ]; then
    # --- EXECUTION MODE ---
    # Runs the solution against all existing test case batches.
    echo "--- Mode: EXECUTE ---"
    
    if [ ! -d "testcases" ] || [ -z "$(ls -A testcases)" ]; then
        echo "Error: No testcases directory found to execute against."
        exit 1
    fi
    
    failed_count=0
    passed_count=0
    
    # Loop through each generation directory (generation1, generation2, etc.)
    for gen_dir in testcases/generation*; do
        echo "--- Running against batch: $(basename "$gen_dir") ---"
        
        # Run bruteforce to generate correct outputs for this batch
        mkdir -p "${gen_dir}/outputs/bruteforce"
        for infile in "${gen_dir}"/*.in; do
            casenum=$(basename "$infile" .in)
            ./bruteforce < "$infile" > "${gen_dir}/outputs/bruteforce/${casenum}.out"
        done

        # Run suspected solution and compare
        mkdir -p "${gen_dir}/outputs/suspected"
        for infile in "${gen_dir}"/*.in; do
            casenum=$(basename "$infile" .in)
            
            ./suspectedSolution < "$infile" > "${gen_dir}/outputs/suspected/${casenum}.out"

            if diff -q "${gen_dir}/outputs/bruteforce/${casenum}.out" "${gen_dir}/outputs/suspected/${casenum}.out" > /dev/null; then
                passed_count=$((passed_count + 1))
            else
                failed_count=$((failed_count + 1))
                
                echo "Test Case #${casenum} in $(basename "$gen_dir"): FAILED"
                echo "--- FAILURE DETAILS ---"
                echo "Input:"
                cat "$infile"
                echo
                echo "Expected Output:"
                cat "${gen_dir}/outputs/bruteforce/${casenum}.out"
                echo
                echo "Actual Output:"
                cat "${gen_dir}/outputs/suspected/${casenum}.out"
                echo "-----------------------"
                
                # Exit after the first failure across all batches
                echo "--- Execution Finished ---"
                echo "PASSED: $passed_count"
                echo "FAILED: $failed_count"
                exit 1
            fi
        done
        echo "Batch $(basename "$gen_dir") PASSED."
    done

    echo "--- Execution Finished ---"
    echo "All batches PASSED."
    echo "PASSED: $passed_count"
    echo "FAILED: $failed_count"
    exit 0

else
    echo "Error: Invalid mode specified. Use 'generate' or 'execute'."
    exit 1
fi