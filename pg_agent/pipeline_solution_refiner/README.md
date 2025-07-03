# Solution Refiner Pipeline

This module provides an iterative solution refinement pipeline that generates and fixes C++ solutions until all user-supplied tests pass (maximum 20 attempts).

## Structure

The code has been refactored into a modular structure for better maintainability:

### `__init__.py`
Main entry point that exports the public API:
- `RefineState` - Type definition for the pipeline state
- `solution_graph` - The compiled LangGraph pipeline
- `compile_with_memory()` - Function to compile the graph with memory checkpointing

### `types.py`
Contains the `RefineState` TypedDict definition that defines the schema for the pipeline state.

### `utils.py`
Contains all utility functions:
- Compilation and execution functions (single canonical method)
- LLM configuration helpers
- Code processing utilities (like `strip_code_fences`)

### `nodes.py`
Contains the graph node functions:
- `llm_solution()` - Generates or fixes C++ solutions using LLM
- `format_test_cases_node()` - Formats test cases to match the C++ solution's expected input format
- `judge_node()` - Determines if all tests passed and increments attempt counter
- `route_after_judge()` - Router that decides whether to continue or end
- `compile_and_run_node()` - Compiles and executes the C++ solution

### `graph.py`
Contains the graph construction logic:
- `build_solution_graph()` - Builds the StateGraph with all nodes and edges
- `compile_with_memory()` - Compiles the graph with memory checkpointing

## Graph Flow

```
LLM_Solution → FormatTestCases → CompileRun → Judge → [Router] → LLM_Solution (loop) or END
```

1. **LLM_Solution**: Generates or fixes C++ solution
2. **FormatTestCases**: Adapts test cases to match the solution's expected input format
3. **CompileRun**: Compiles and executes the solution against formatted test cases
4. **Judge**: Evaluates results and manages attempt counter
5. **Router**: Decides whether to continue refining or end

## State Schema

The pipeline tracks comprehensive test execution results:

- `test_cases`: User-provided test cases (any format)
- `formatted_test_cases`: Test cases formatted for the solution
- `passing_tests`: List of test cases that passed execution
- `failing_tests`: List of test cases that failed execution
- `attempt`: Current refinement attempt number
- `all_passed`: Whether all tests passed successfully

## Usage

```python
from pg_agent.pipeline_solution_refiner import RefineState, solution_graph, compile_with_memory

# Create initial state - test_cases can be in any format
state: RefineState = {
    "problem_statement": "Your problem here",
    "test_cases": """
    Input: 5, Expected: 10
    Input: 3, Expected: 6
    Input: abc, Expected: ERROR
    """,
}

# Or as JSON string:
state: RefineState = {
    "problem_statement": "Your problem here", 
    "test_cases": '[["5", "10"], ["3", "6"], ["abc", "ERROR"]]',
}

# Or as CSV-like format:
state: RefineState = {
    "problem_statement": "Your problem here",
    "test_cases": "5,10\n3,6\nabc,ERROR",
}

# The format_test_cases_node will automatically parse and adapt test cases to match the solution's format

# Compile and run the graph
compiled_graph = compile_with_memory()
result = compiled_graph.invoke(state)
```

## Test Case Formatting

The `format_test_cases_node` automatically:
- **Accepts test cases in any format** (string, JSON, CSV, text, etc.)
- **Parses the input format** intelligently using LLM
- **Analyzes the generated C++ solution** to understand expected input format
- **Converts test cases** to match this expected format
- **Handles edge cases** and invalid input scenarios
- **Falls back gracefully** if formatting fails

**Note:** Users can provide test cases in any format they're comfortable with. The pipeline will automatically parse and adapt them to match what the solution expects.

## Migration from Old Structure

The original `solution_refiner.py` file has been moved to `solution_refiner_original.py` as a backup. All functionality has been preserved in the new modular structure. 