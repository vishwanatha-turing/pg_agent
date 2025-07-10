# Sample Problem Structure

## Table of Contents
- [Test Cases Structure](#test-cases-structure)
- [Test Generator](#test-generator)
  - [Modifying for Your Problem](#modifying-for-your-problem)
  - [Example Problem Adaptation](#example-problem-adaptation)
  - [Advanced Customization](#advanced-customization)
- [Testing and Delivery](#testing-and-delivery)
  - [Testing Solutions](#testing-solutions)
  - [Creating Delivery Package](#creating-delivery-package)

## Test Cases Structure

The `test_cases` directory contains both manual and generated test cases:

### Manual Test Cases
- `example_*.in/out`: Sample test cases from the problem statement
  - These should match the examples in `problem_statement.md`
  - Numbered sequentially: `example_1.in/out`, `example_2.in/out`, etc.
  - Used for initial solution verification

- `test_*.in/out`: Manually crafted test cases
  - Special cases that need precise control
  - Edge cases that might be missed by the generator
  - Numbered sequentially: `test_1.in/out`, `test_2.in/out`, etc.
  - Not overwritten by the generator

### Generated Test Cases
- `[number].in/out`: Automatically generated test cases
  - Created by `test_generator.cpp`
  - Numbered sequentially starting from the lowest available number
  - Example: `1.in/out`, `2.in/out`, etc.
  - Will not overwrite existing manual test cases

## Test Generator

The test generator (`test_generator.cpp`) creates a series of test cases with the following features:
- Generates 50 test cases by default
- Automatically numbers files sequentially (1.in/out, 2.in/out, etc.)
- Uses brute force solution by default
- Falls back to optimal solution if brute force times out (>10 seconds)
- Simulates stdin/stdout for solutions to make code reuse easier


### File Structure
```
sample_problem_structure/
├── test_generator.cpp    # Main test generator
├── problem_statement.md  # Problem description with examples
├── test_cases/          # All test cases
│   ├── example_1.in     # Sample input from problem statement
│   ├── example_1.out    # Sample output from problem statement
│   ├── test_1.in        # Manual test case input
│   ├── test_1.out       # Manual test case output
│   ├── 1.in            # Generated test case input
│   ├── 1.out           # Generated test case output
│   └── ...
└── README.md           # This file
```

### How to Use

1. Before running the generator:
   - Add sample test cases as `example_*.in/out`
   - Add any manual test cases as `test_*.in/out`
   - These will be preserved when generating additional tests

2. Compile the generator:
```bash
g++ -std=c++17 test_generator.cpp -o test_generator
```

3. Run the generator:
```bash
./test_generator
```

The generator will create additional test cases, skipping any existing file numbers to avoid overwriting manual tests.

### Modifying for Your Problem

To adapt the generator for your competitive programming problem, you need to modify several parts of `test_generator.cpp`:

1. **Input Generation**
```cpp
void generate_test_case(int test_num, int file_num) {
    string input_file = "test_cases/" + to_string(file_num) + ".in";
    ofstream fin(input_file);
    
    // MODIFY THIS PART: Generate your problem's input format
    int n = rand() % 100 + 1;  // Example: random number 1-100
    fin << n << "\n";
    
    fin.close();
    // ...
}
```

2. **Brute Force Solution**
```cpp
string solve_brute_force(const string& input_str) {
    IORedirector redirector(input_str);
    
    // REPLACE WITH YOUR BRUTE FORCE SOLUTION
    // Use normal cin/cout as you would in a contest
    int n;
    cin >> n;
    
    // Example slow solution trigger (remove this)
    if (n == 42 || n == 87) {
        this_thread::sleep_for(seconds(11));
    }
    
    cout << n << "\n";
    return redirector.get_output();
}
```

3. **Optimal Solution**
```cpp
string solve_optimal(const string& input_str) {
    IORedirector redirector(input_str);
    
    // REPLACE WITH YOUR OPTIMAL SOLUTION
    // Use normal cin/cout as you would in a contest
    int n;
    cin >> n;
    cout << n << "\n";
    
    return redirector.get_output();
}
```

### Example Problem Adaptation

Here's an example of how to modify the generator for a sum of two numbers problem:

```cpp
// In generate_test_case:
void generate_test_case(int test_num, int file_num) {
    ofstream fin("test_cases/" + to_string(file_num) + ".in");
    
    // Generate two random numbers
    int a = rand() % 1000;
    int b = rand() % 1000;
    fin << a << " " << b << "\n";
    
    fin.close();
    // ...
}

// Brute force solution
string solve_brute_force(const string& input_str) {
    IORedirector redirector(input_str);
    
    int a, b;
    cin >> a >> b;
    cout << a + b << "\n";
    
    return redirector.get_output();
}

// Optimal solution (same in this case)
string solve_optimal(const string& input_str) {
    IORedirector redirector(input_str);
    
    int a, b;
    cin >> a >> b;
    cout << a + b << "\n";
    
    return redirector.get_output();
}
```

### Advanced Customization

1. **Number of Test Cases**
   - Modify `num_tests` in main() (default: 50)

2. **Timeout Duration**
   - Modify the timeout in run_solution() (default: 10 seconds)
   ```cpp
   auto status = future.wait_for(seconds(10));  // Change 10 to your desired timeout
   ```

3. **Test Case Distribution**
   - Modify generate_test_case() to create different types of tests:
     - Corner cases
     - Maximum/minimum values
     - Special patterns
     - Random cases
     - Stress tests

4. **Custom Validation**
   - Add validation logic in generate_test_case() to ensure test cases meet problem constraints
   - Add result validation in run_solution() if needed

## Best Practices

1. **Test Case Generation**
   - Include edge cases
   - Cover minimum and maximum input values
   - Include random cases of various sizes
   - Consider special cases that might break solutions

2. **Solution Implementation**
   - Keep brute force and optimal solutions separate
   - Use the same input/output format as the actual problem
   - Include proper validation and error handling

3. **Verification**
   - Check that generated test cases meet problem constraints
   - Verify that both solutions produce identical outputs
   - Test with known edge cases first

## Common Modifications

1. **Adding Problem Constraints**
```cpp
const int MAX_N = 100000;
const int MAX_VALUE = 1000000000;

void generate_test_case(int test_num, int file_num) {
    // Generate values within constraints
    int n = rand() % MAX_N + 1;
    vector<int> a(n);
    for(int i = 0; i < n; i++) {
        a[i] = rand() % MAX_VALUE + 1;
    }
    // Write to file...
}
```

2. **Adding Special Test Cases**
```cpp
void generate_test_case(int test_num, int file_num) {
    if(test_num == 1) {
        // Minimum case
        // ...
    } else if(test_num == 2) {
        // Maximum case
        // ...
    } else if(test_num <= 5) {
        // Special patterns
        // ...
    } else {
        // Random cases
        // ...
    }
}
```

Remember to update this README when you modify the generator for your specific problem!

## Testing and Delivery

Before submitting the problem, it's important to verify that it meets all requirements and can be properly packaged for delivery. The [utilities repository](https://github.com/Dragon-POC/utilities) provides tools for testing and delivery package creation.

### Prerequisites

Install required tools:
```bash
# On macOS
brew install coreutils gnu-time jq

# On Linux
# These tools are usually pre-installed
```

### Testing Solutions

Use `test_run.sh` from the utilities repository to test all solutions:

```bash
# Test all solutions in the repository
./test_run.sh path/to/sample_problem_structure

# Test a specific solution
./test_run.sh path/to/sample_problem_structure --solution standard.cpp
```

The script will:
1. Test the optimal solution(s) specified in `requirements.json`
2. Test all Qwen-generated solutions in the `qwen/` directory
3. Create detailed logs in `logs/sample_problem_structure/`
4. Show a summary of passed/failed tests for each solution

Example output:
```
Testing all solutions...
Detailed logs will be saved in logs/sample_problem_structure directory

Testing optimal solutions from requirements.json...
Testing optimal solution standard.cpp... done: 50 passed / 0 failed / 0 crashed / 50 total.

Optimal Solutions Summary:
Solutions: 1 passed / 0 failed from 1 total

Testing Qwen solutions...
Testing solution_01.cpp... done: 30 passed / 20 failed / 0 crashed / 50 total.
...

Individual test logs are available in logs/sample_problem_structure directory
```

### Creating Delivery Package

Use `delivery_gen.py` to create a standardized delivery package:

```bash
# Create delivery package from the repository
python delivery_gen.py path/to/sample_problem_structure

# Optionally specify custom problem ID and output directory
python delivery_gen.py path/to/sample_problem_structure \
    --problem-id custom_name \
    --delivery-dir path/to/output
```

The script will:
1. Verify repository structure
2. Convert test cases to sequential numbering
3. Create a delivery package with:
   - `problem.json` (from `requirements.json`)
   - Renamed test cases
   - Standard solution
   - Solution explanation
   - Qwen test solutions

Example output:
```
Created new directory: delivery/sample_problem_structure
Reading requirements from: .../sample_problem_structure/requirements.json
Reading statement from: .../sample_problem_structure/problem_statement.md
Found 2 example_*.in cases
Writing problem.json...
Copying and renaming test cases...
Copying solutions...

✅ Successfully created delivery package
   Output directory: delivery/sample_problem_structure
```

### Repository Requirements

For successful testing and delivery package creation, ensure:

1. Required Files:
   - `requirements.json`: Problem metadata
   - `problem_statement.md`: Problem description
   - `solution.md`: Solution explanation
   - `standard.cpp`: Main correct solution

2. Test Cases:
   - `example_*.in/out`: From problem statement
   - `test_*.in/out`: Manual test cases
   - Generated test cases with numeric names

3. Solutions:
   - Standard solution in `standard.cpp`
   - Qwen solutions in `qwen/run_XX.cpp`
   - Prompt used to get Qwen solutions in `qwen/prompt.txt`

4. Metadata (`requirements.json`):
   ```json
   {
       "title": "Sample Problem",
       "difficulty": "Medium",
       "tags": ["DS/Array", "Algo/Implementation"],
       "time": 1,
       "space": 256,
       "problem_statement": "problem_statement.md",
       "standard_program": ["standard.cpp"],
       "explanation": "solution.md",
       "test_case_generator": "test_generator.cpp"
   }
   ```