#!/bin/bash

# Parse arguments
FOLDER_PATH="."
SOLUTION_FILE=""
RUN_FULL_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --solution)
            SOLUTION_FILE="$2"
            shift 2
            ;;
        --full)
            RUN_FULL_TESTS=true
            shift
            ;;
        *)
            FOLDER_PATH="$1"
            shift
            ;;
    esac
done

# Get absolute paths before changing directory
SCRIPT_DIR=$(pwd)
FOLDER_PATH=$(realpath "$FOLDER_PATH")
DIR_NAME=$(basename "$FOLDER_PATH")
LOGS_DIR="$SCRIPT_DIR/logs/$DIR_NAME"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Change to the target directory
cd "$FOLDER_PATH" || { echo "Error: Could not change to directory $FOLDER_PATH"; exit 1; }

# Try tests directory first, then QwenTest
if [ -d "tests" ]; then
    INPUT_DIR="tests"
    OUTPUT_DIR="tests"
else
    INPUT_DIR="test_cases"
    OUTPUT_DIR="test_cases"
fi

TMP_OUTPUT="temp_output.txt"
EXEC_NAME="exec_temp"

# Set REQUIREMENTS to whichever file exists
if [ -f "requirements.json" ]; then
    REQUIREMENTS="requirements.json"
elif [ -f "problem.json" ]; then
    REQUIREMENTS="problem.json"
else
    echo "Error: Neither requirements.json nor problem.json found"
    exit 1
fi

# Determine which directory to use for Qwen solutions
if [ -d "qwen" ]; then
    QWEN_DIR="qwen"
elif [ -d "QwenTest" ]; then
    QWEN_DIR="QwenTest"
else
    echo "Error: Neither qwen nor QwenTest directory found"
    exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    TIME_CMD="/opt/homebrew/bin/gtime"
else
    TIME_CMD="time"
fi

# Function to run a test and compare output
run_test() {
    local input_file=$1
    local output_dest=$2
    local test_name=$(basename "$input_file" .in)
    local output_file="$OUTPUT_DIR/$test_name.out"

    if [ ! -f "$output_file" ]; then
        echo "$test_name: Missing output file, skipping." >> "$output_dest"
        return 1
    fi

    ((total++))

    local runtime=0
    local mem_mb="N/A"
    local verdict=""
    local perf_file=$(mktemp)

    $TIME_CMD -f "%U %M" -o "$perf_file" timeout --foreground "${time_limit}s" ./"$EXEC_NAME" < "$input_file" > "$TMP_OUTPUT" 2>&1
    local exit_code=$?

    # Check if the process was interrupted by Ctrl+C (SIGINT)
    if [ $exit_code -eq 130 ]; then
        echo -e "\nScript interrupted by user" >> "$output_dest"
        rm -f "$TMP_OUTPUT" "$EXEC_NAME" "$perf_file"
        exit 130
    fi

    if [ -s "$perf_file" ]; then
        local mem_kb=0
        read runtime mem_kb < <(tail -n 1 "$perf_file")
        if [[ "$mem_kb" =~ ^[0-9]+$ ]]; then
            mem_mb="$(echo "scale=2; $mem_kb / 1024" | bc)MB"
        fi
    fi
    rm -f "$perf_file"

    if [ $exit_code -eq 124 ]; then
        verdict="TIMEOUT"
        runtime=$time_limit
        ((failed++))
    elif [ $exit_code -ne 0 ]; then
        verdict="CRASH"
        ((crashed++))
    elif (( $(echo "$runtime > $time_limit" | bc -l) )); then
        verdict="TIMEOUT"
        runtime=$time_limit
        ((failed++))
    elif [[ "$mem_kb" != "N/A" ]] && (( mem_kb > space_limit )); then
        verdict="MEMORY"
        ((failed++))
    elif diff -w "$TMP_OUTPUT" "$output_file" > /dev/null; then
        verdict="PASS"
        ((passed++))
    else
        verdict="FAIL"
        ((failed++))
    fi

    echo "$test_name: $verdict (${runtime}s, ${mem_mb})" >> "$output_dest"

    if [ "$first_entry" = true ]; then
        first_entry=false
    else
        echo "," >> "$JSON_LOG"
    fi

    echo "  {\"testcase_id\": \"$test_name\", \"verdict\": \"$verdict\", \"time\": $runtime, \"space\": $mem_kb}" >> "$JSON_LOG"

    # Return 1 if test failed and we're not in full test mode
    if [ "$RUN_FULL_TESTS" = false ] && [ "$verdict" != "PASS" ]; then
        return 1
    fi
    return 0
}

run_tests() {
    local source_file="$1"
    local is_batch_mode="$2"
    
    source_file=$(realpath "$source_file")
    base_name=$(basename "$source_file" .cpp)
    JSON_LOG="$LOGS_DIR/${base_name}-performance.json"
    TEST_LOG="$LOGS_DIR/${base_name}-log.txt"
    
    # Set output destination
    if [ "$is_batch_mode" = true ]; then
        OUTPUT="$TEST_LOG"
        # Clear the log file at the start
        > "$OUTPUT"
    else
        OUTPUT=/dev/stdout
    fi

    # Read limits from JSON
    time_limit=$(jq -r '.time // empty' "$REQUIREMENTS")
    space_limit=$(jq -r '.space // empty' "$REQUIREMENTS")

    # Validate that both limits are provided and are integers
    if [ -z "$time_limit" ] || [ -z "$space_limit" ] || ! [[ "$time_limit" =~ ^[0-9]+$ ]] || ! [[ "$space_limit" =~ ^[0-9]+$ ]]; then
        local error_msg="Invalid configuration in $REQUIREMENTS - time and space limits must be integers"
        local values_msg="Current values: time=$time_limit, space=$space_limit"
        echo "$error_msg" >> "$OUTPUT"
        echo "$values_msg" >> "$OUTPUT"
        if [ "$is_batch_mode" = true ]; then
            echo "done: configuration error - missing or invalid time/space limits."
        fi
        return 1
    fi

    # Compile source
    compiler="g++"
    # On macOS, we can't use static linking
    if [[ "$OSTYPE" == "darwin"* ]]; then
        compiler_flags="-std=c++20 -O2"
    else
        compiler_flags="-std=c++20 -O2 -static"
    fi
    
    if ! $compiler $compiler_flags "$source_file" -o "$EXEC_NAME" 2>/dev/null; then
        local msg="Test Summary ($(basename "$source_file")): Compilation failed"
        echo "$msg" >> "$OUTPUT"
        echo "Performance log was not created" >> "$OUTPUT"
        # Return special result for compilation failure
        echo "COMPILATION_FAILED"
        return 0
    fi

    local mode_str="Running test cases"
    if [ "$RUN_FULL_TESTS" = true ]; then
        mode_str="$mode_str (full test mode)"
    else
        mode_str="$mode_str (stopping at first failure)"
    fi
    echo "$mode_str with time=${time_limit}s, space=${space_limit}MB..." >> "$OUTPUT"
    echo "" >> "$OUTPUT"  # Add blank line after header
    
    space_limit=$((space_limit * 1024))

    echo "[" > "$JSON_LOG"
    first_entry=true

    passed=0
    failed=0
    crashed=0
    total=0

    # Run all tests
    for input_file in $(find "$INPUT_DIR" -name "*.in" | sort -V); do
        if ! run_test "$input_file" "$OUTPUT"; then
            if [ "$RUN_FULL_TESTS" = false ]; then
                break
            fi
        fi
    done

    echo "]" >> "$JSON_LOG"
    rm -f "$TMP_OUTPUT" "$EXEC_NAME"

    echo "" >> "$OUTPUT"  # Add blank line before summary
    echo "Performance log: $JSON_LOG" >> "$OUTPUT"
    local summary="Test Summary ($(basename "$source_file")): $passed passed / $failed failed / $crashed crashed / $total total."
    echo "$summary" >> "$OUTPUT"
    
    # Return just the numbers for batch mode processing
    if [ "$is_batch_mode" = true ]; then
        echo "RESULTS $passed $failed $crashed $total"
    fi
}

# Function to run tests and capture results
run_and_capture_results() {
    local source_file="$1"
    local description="$2"
    
    echo -n "Testing $description... "
    
    # Run the test and capture the results
    while IFS= read -r line; do
        if [[ $line == "RESULTS"* ]]; then
            # Parse the space-separated numbers after "RESULTS"
            read -r _ p f c t <<< "$line"
            if [ "$f" -eq 0 ] && [ "$c" -eq 0 ]; then
                ((solutions_passed++))
            fi
            echo -n "done: "
            echo "$p passed / $f failed / $c crashed / $t total."
        elif [[ $line == "COMPILATION_FAILED" ]]; then
            echo "done: compilation failed."
            ((compilation_failed++))
        elif [[ $line == "done:"* ]]; then
            echo "$line"
            ((compilation_failed++))
        fi
    done < <(run_tests "$source_file" true)
}

if [ -n "$SOLUTION_FILE" ]; then
    # Test specific solution file
    if [ ! -f "$SOLUTION_FILE" ]; then
        echo "Error: Solution file $SOLUTION_FILE not found"
        exit 1
    fi
    run_tests "$SOLUTION_FILE" false
    exit $?
else
    # No arguments provided, test all cpp files in qwen/QwenTest folder
    echo "Testing all solutions in $QWEN_DIR folder..."
    echo "Detailed logs will be saved in $LOGS_DIR directory"
    echo ""
    
    # First test optimal solutions from requirements.json if they exist
    optimal_total=0
    solutions_passed=0
    compilation_failed=0
    optimal_solutions=$(jq -r '.standard_program[]?' "$REQUIREMENTS" 2>/dev/null)
    if [ -n "$optimal_solutions" ]; then
        echo "Testing optimal solutions from $REQUIREMENTS..."
        while IFS= read -r source_file; do
            if [ -f "$source_file" ]; then
                ((optimal_total++))
                run_and_capture_results "$source_file" "optimal solution $source_file"
            else
                echo "Warning: Optimal solution $source_file not found"
            fi
        done <<< "$optimal_solutions"
        echo ""
    else
        # If no standard_program specified, test all standard*.cpp files
        echo "No standard_program specified in $REQUIREMENTS, testing all standard*.cpp files..."
        for source_file in standard*.cpp; do
            if [ -f "$source_file" ]; then
                ((optimal_total++))
                run_and_capture_results "$source_file" "standard solution $source_file"
            fi
        done
        if [ ! -f standard*.cpp ]; then
            echo "No standard*.cpp files found"
        fi
        echo ""
    fi

    # Show optimal solutions summary
    echo "Optimal Solutions Summary:"
    echo "Solutions: $solutions_passed passed / $((optimal_total - solutions_passed)) failed from $optimal_total total"
    echo ""

    # Reset counters for Qwen solutions
    solutions_passed=0
    compilation_failed=0
    
    echo "Testing Qwen solutions..."
    qwen_total=0
    for source_file in "$QWEN_DIR"/*.cpp; do
        ((qwen_total++))
        base_name=$(basename "$source_file")
        run_and_capture_results "$source_file" "$base_name"
    done
    
    echo "Qwen Solutions Summary:"
    echo "Solutions: $solutions_passed passed / $((qwen_total - solutions_passed)) failed from $qwen_total total"
    echo ""
    echo "Individual test logs are available in $LOGS_DIR directory"
    echo ""
    exit 0
fi
