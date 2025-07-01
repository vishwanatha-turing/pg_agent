#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Starting Test Execution Inside Container ---"

# --- COMPILE STAGE ---
# Compile all the C++ source files that were copied into this container.
# We use C++14 standard and enable optimizations.
echo "Compiling C++ source files..."
g++ -std=c++14 -O2 -o testcaseGenerator testcaseGenerator.cpp
g++ -std=c++14 -O2 -o bruteforce bruteforce.cpp
g++ -std=c++14 -O2 -o suspectedSolution suspectedSolution.cpp
echo "Compilation successful."

# --- TEST CASE GENERATION ---
mkdir -p testcases
echo "Generating test cases..."
./testcaseGenerator

# --- BRUTEFORCE EXECUTION ---
mkdir -p outputs/bruteforce
echo "Running bruteforce solution..."
for infile in testcases/*.in; do
    casenum=$(basename "$infile" .in)
    ./bruteforce < "$infile" > "outputs/bruteforce/${casenum}.out"
done

# --- SUSPECTED SOLUTION EXECUTION & COMPARISON ---
mkdir -p outputs/suspected
echo "Running suspected solution and comparing..."
failed_count=0
passed_count=0

for infile in testcases/*.in; do
    casenum=$(basename "$infile" .in)
    
    ./suspectedSolution < "$infile" > "outputs/suspected/${casenum}.out"

    if diff -q "outputs/bruteforce/${casenum}.out" "outputs/suspected/${casenum}.out" > /dev/null; then
        echo "Test Case #${casenum}: PASSED"
        passed_count=$((passed_count + 1))
    else
        echo "Test Case #${casenum}: FAILED"
        failed_count=$((failed_count + 1))
        
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
        
        break
    fi
done

echo "--- Execution Finished ---"
echo "PASSED: $passed_count"
echo "FAILED: $failed_count"

if [ "$failed_count" -gt 0 ]; then
    exit 1
else
    exit 0
fi