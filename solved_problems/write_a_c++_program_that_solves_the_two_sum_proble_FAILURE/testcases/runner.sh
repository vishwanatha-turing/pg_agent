#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

MODE=$1
GENERATION_ID=$2

if [ "$MODE" = "generate" ]; then
    # --- GENERATION MODE ---
    echo "--- Mode: GENERATE (Batch #${GENERATION_ID}) ---"
    
    echo "Compiling testcaseGenerator.cpp..."
    g++ -std=c++14 -O2 -o testcaseGenerator testcaseGenerator.cpp
    
    # Create the generation-specific directory directly in the current path.
    # The current path IS the shared volume.
    OUTPUT_DIR="generation${GENERATION_ID}"
    mkdir -p "$OUTPUT_DIR"
    
    # Change directory to write the .in files.
    cd "$OUTPUT_DIR"
    echo "Running testcaseGenerator..."
    ../testcaseGenerator # The executable is one level up.
    
    echo "Test cases generated in ${OUTPUT_DIR}"

elif [ "$MODE" = "execute" ]; then
    # --- EXECUTION MODE ---
    echo "--- Mode: EXECUTE ---"
    
    echo "Compiling solution files..."
    g++ -std=c++14 -O2 -o bruteforce bruteforce.cpp
    g++ -std=c++14 -O2 -o suspectedSolution suspectedSolution.cpp
    
    # Check if any 'generation*' directories exist in the current path.
    if ! ls -d generation* > /dev/null 2>&1; then
        echo "Error: No 'generation*' directories found to execute against."
        exit 1
    fi
    
    failed_count=0
    passed_count=0
    
    # Loop through each generation directory.
    for gen_dir in generation*; do
        echo "--- Running against batch: $(basename "$gen_dir") ---"
        
        mkdir -p "${gen_dir}/outputs/bruteforce"
        for infile in "${gen_dir}"/*.in; do
            casenum=$(basename "$infile" .in)
            ./bruteforce < "$infile" > "${gen_dir}/outputs/bruteforce/${casenum}.out"
        done

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