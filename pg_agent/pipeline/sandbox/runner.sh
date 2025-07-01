#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Test Execution ---"

# 1. Create directories for test cases and outputs
mkdir -p testcases
mkdir -p outputs
mkdir -p outputs/bruteforce
mkdir -p outputs/suspected

# 2. Generate input test files
echo "Generating test cases..."
./testcaseGenerator

# 3. Run bruteforce solution to generate correct outputs
echo "Running bruteforce solution..."
for infile in testcases/*.in; do
    casenum=$(basename "$infile" .in)
    ./bruteforce < "$infile" > "outputs/bruteforce/${casenum}.out"
done

# 4. Run suspected solution and compare outputs
echo "Running suspected solution and comparing..."
failed_count=0
passed_count=0

for infile in testcases/*.in; do
    casenum=$(basename "$infile" .in)
    
    # Run the suspected solution
    ./suspectedSolution < "$infile" > "outputs/suspected/${casenum}.out"

    # Compare the output with the bruteforce output
    if diff -q "outputs/bruteforce/${casenum}.out" "outputs/suspected/${casenum}.out" > /dev/null; then
        echo "Test Case #${casenum}: PASSED"
        passed_count=$((passed_count + 1))
    else
        echo "Test Case #${casenum}: FAILED"
        failed_count=$((failed_count + 1))
        
        # --- Output details for the first failing test case ---
        echo "--- FAILURE DETAILS ---"
        echo "Input:"
        cat "$infile"
        echo
        echo "Expected Output:"
        cat "outputs/bruteforce/${casenum}.out"
        echo
        echo "Actual Output:"
        cat "outputs/suspected/${casenum}.out"
        echo "-----------------------"
        
        # Stop after the first failure as requested
        break
    fi
done

echo "--- Execution Finished ---"
echo "PASSED: $passed_count"
echo "FAILED: $failed_count"

# Final exit code determines success or failure for the Docker run command
if [ "$failed_count" -gt 0 ]; then
    exit 1
else
    exit 0
fi
