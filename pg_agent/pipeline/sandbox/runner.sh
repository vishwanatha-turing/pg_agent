#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# We will handle errors gracefully within the script where needed.
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
    SOLUTION_FILE=$3 
    EXECUTABLE_NAME=$4

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
                echo "TIMEOUT" > "$outfile"
            else
                echo "${infile}: RUNTIME_ERROR"
                echo "RUNTIME_ERROR" > "$outfile"
            fi
        fi
    done
    exit 0

elif [ "$MODE" = "validate_suite" ]; then
    echo "--- Mode: VALIDATE SUITE ---"
    echo "Compiling validator.cpp..."
    g++ -std=c++14 -O2 -o validator validator.cpp

    if ! ls -d *.in > /dev/null 2>&1; then
        echo "Warning: No .in files found to validate."
        exit 0
    fi

    # Loop through all .in files in the directory
    for infile in *.in; do
        echo "--- Validating ${infile} ---"
        
        # --- THIS IS THE CRUCIAL FIX ---
        # We run the validator and check its exit code directly in an 'if' statement.
        # This prevents 'set -e' from terminating the whole script if the validator fails.
        # We also redirect stderr to a temporary file to capture the error message.
        if ./validator < "${infile}" 2> validator_error.log; then
            echo "VALID: ${infile}"
        else
            # If it failed, print the reason from the error log.
            # The '|| true' ensures this command doesn't fail if the log is empty.
            echo "INVALID: ${infile} REASON: $(cat validator_error.log || true)"
        fi
        # --- END OF FIX ---
    done
    exit 0

else
    echo "Error: Invalid mode specified."
    exit 1
fi
