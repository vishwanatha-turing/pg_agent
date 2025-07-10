#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

MODE=$1

if [ "$MODE" = "generate" ]; then
    GENERATION_ID=$2
    echo "--- Mode: GENERATE (Batch #${GENERATION_ID}) ---"
    
    echo "Compiling testcaseGenerator.cpp..."
    g++ -std=c++14 -O2 -o testcaseGenerator testcaseGenerator.cpp
    
    OUTPUT_DIR="generation${GENERATION_ID}"
    mkdir -p "$OUTPUT_DIR"
    
    cd "$OUTPUT_DIR"
    echo "Running testcaseGenerator..."
    ../testcaseGenerator
    
    echo "Test cases generated in ${OUTPUT_DIR}"

elif [ "$MODE" = "execute_suite" ]; then
    TIME_LIMIT=$2
    SOLUTION_FILE=$3 # e.g., "bruteforce.cpp"
    EXECUTABLE_NAME=$4 # e.g., "bruteforce_solution"

    echo "--- Mode: EXECUTE SUITE (Time Limit: ${TIME_LIMIT}s) ---"
    
    echo "Compiling ${SOLUTION_FILE}..."
    g++ -std=c++14 -O2 -o "${EXECUTABLE_NAME}" "${SOLUTION_FILE}"
    
    if ! ls -d *.in > /dev/null 2>&1; then
        echo "Warning: No .in files found in this directory to execute against."
        exit 0
    fi
    
    for infile in *.in; do
        casenum=$(basename "$infile" .in)
        outfile="${casenum}.out"
        
        echo "Running ${EXECUTABLE_NAME} on ${infile}..."
        if timeout "$TIME_LIMIT" ./"${EXECUTABLE_NAME}" < "$infile" > "$outfile"; then
            echo "${infile}: SUCCESS"
        else
            if [ $? -eq 124 ]; then
                echo "${infile}: TIMEOUT"
                # Create an output file indicating timeout
                echo "TIMEOUT" > "$outfile"
            else
                echo "${infile}: RUNTIME_ERROR"
                echo "RUNTIME_ERROR" > "$outfile"
            fi
        fi
    done
    exit 0

else
    echo "Error: Invalid mode specified. Use 'generate' or 'execute_suite'."
    exit 1
fi
