# Novel Prompt Pipeline

This pipeline generates programming problem statements and test cases based on topics and optional context.

## Overview

The novel prompt pipeline takes topics, optional previous problems, and user prompts to generate:
- A complete problem statement in markdown format
- 4-6 comprehensive test cases saved as `example_*.in` and `example_*.out` files
- Uses the `sample_problem_structure` template for consistent output format

## Pipeline Flow

1. **Setup Output** - Copies the template structure from `sample_problem_structure`
2. **Generate Problem Statement** - Creates a problem statement based on topics and context
3. **Generate Test Cases** - Creates 4-6 test cases based on the problem statement
4. **Save Outputs** - Saves everything to the specified output folder

## State Schema

```python
class NovelPromptState(TypedDict):
    # Inputs
    topics: Optional[str]  # Topic(s) for initial generation (optional if previous problem exists)
    previous_problem: Optional[str]  # Previous problem statement if exists
    user_prompt: Optional[str]  # User's prompt if provided
    
    # Generated content
    problem_statement: str  # Generated problem statement
    test_cases: list[tuple[str, str]]  # List of (input, expected_output) pairs
    
    # Output folder (copied from template)
    output_folder: str  # Folder where to save the generated files
    
    # Computed file paths (set by setup_output_node)
    problem_statement_file: Optional[str]  # Path to problem_statement.md
    test_cases_folder: Optional[str]  # Path to test_cases/ directory
    
    # UI Controls
    auto_load_previous: bool  # Checkbox to auto-load previous problem statement
```

## Usage

### Basic Usage

```python
from pg_agent.pipeline_novel_prompt import create_novel_prompt_graph

# Create the graph
graph = create_novel_prompt_graph()

# Run the pipeline with topics
result = graph.invoke({
    "topics": "dynamic programming, arrays",
    "previous_problem": None,
    "user_prompt": "Make it about finding maximum subarray sum",
    "output_folder": "./problem_001/",
    "auto_load_previous": True
})

# Run the pipeline without topics (using previous problem and user prompt)
result = graph.invoke({
    "topics": None,  # Optional when previous problem exists
    "previous_problem": "Previous problem statement...",
    "user_prompt": "Create a variation focusing on negative numbers",
    "output_folder": "./problem_002/",
    "auto_load_previous": True
})
```

### Input Requirements

The pipeline requires **at least one** of the following inputs:
- ✅ **Topics**: General topic area for problem generation
- ✅ **Previous Problem**: Existing problem statement for context
- ✅ **User Prompt**: Specific requirements for the new problem

**Valid combinations:**
- `topics` only
- `topics` + `user_prompt`
- `previous_problem` + `user_prompt`
- `topics` + `previous_problem` + `user_prompt`
- `user_prompt` only (if previous problem exists via auto-load)

### Auto-Load Feature

The pipeline includes an auto-load feature that can automatically load the previous problem statement from an existing folder:

**When `auto_load_previous: True`:**
1. Checks if `{output_folder}/problem_statement.md` exists
2. If found, loads it as the `previous_problem` context
3. Uses this context to generate a new, related problem
4. Logs the auto-load action for transparency

**Example workflow:**
```python
# First run - creates problem_001/
result1 = graph.invoke({
    "topics": "arrays",
    "output_folder": "./problem_001/",
    "auto_load_previous": True
})

# Second run - auto-loads problem_001/problem_statement.md as context
result2 = graph.invoke({
    "topics": "arrays, variations",
    "output_folder": "./problem_002/",
    "auto_load_previous": True  # Will load from problem_001/
})
```

**Benefits:**
- ✅ **Seamless iteration**: Build on previous problems
- ✅ **Context preservation**: New problems relate to previous ones
- ✅ **Automatic detection**: No manual copy-paste needed
- ✅ **Optional feature**: Can be disabled if not wanted

### Output Structure

The pipeline copies the `sample_problem_structure` template and creates:

```
problem_001/
├── problem_statement.md      # Generated problem statement
├── test_cases/
│   ├── example_1.in         # Generated test case input
│   ├── example_1.out        # Generated test case output
│   ├── example_2.in
│   ├── example_2.out
│   └── ...                  # 4-6 test cases total
├── test_generator.cpp        # Template test generator
├── standard.cpp             # Template solution file
├── requirements.json        # Template requirements
├── solution.md             # Template solution file
└── README.md               # Template documentation
```

## Components

### Nodes

- `setup_output_node` - Copies template structure from `sample_problem_structure`
- `generate_problem_statement_node` - Generates problem statement using LLM
- `generate_test_cases_node` - Generates test cases using LLM
- `save_outputs_node` - Saves generated content to files

### Prompts

Located in `pg_agent/pipeline_novel_prompt/prompts/`:
- `GENERATE_PROBLEM_STATEMENT_PROMPT` - Generates problem statements
- `GENERATE_TEST_CASES_PROMPT` - Generates test cases

### Utilities

- `setup_output_structure()` - Copies template structure (preserves existing work)
- `save_problem_statement()` - Saves problem statement to file
- `save_test_cases()` - Saves test cases as example_*.in/out files
- `parse_test_cases_from_llm_response()` - Parses LLM response into test cases

## Features

- **Template-based structure**: Uses `sample_problem_structure` as template
- **Smart copying**: Only copies template files if missing, preserves existing work
- **Topic-based generation**: Creates problems based on specified topics
- **Context awareness**: Uses previous problems to ensure variety
- **User customization**: Incorporates user prompts for specific requirements
- **Comprehensive test cases**: Generates 4-6 test cases covering edge cases
- **Consistent output**: Follows standardized folder structure
- **Markdown formatting**: Problem statements are properly formatted
- **Pipeline-specific prompts**: All prompts organized within the pipeline

## Example Input

```python
{
    "topics": "graph algorithms, shortest path",
    "previous_problem": "Find the shortest path in a weighted graph...",
    "user_prompt": "Focus on Dijkstra's algorithm with negative weights",
    "output_folder": "./problems/graph_shortest_path/"
}
```

## Example Output

**problem_statement.md:**
```markdown
# Shortest Path with Negative Weights

Given a directed graph with weighted edges (including negative weights), find the shortest path from source to destination using a modified Dijkstra's algorithm.

## Input Format
- First line: n m (number of nodes and edges)
- Next m lines: u v w (edge from u to v with weight w)
- Last line: s t (source and destination nodes)

## Output Format
- Single line: shortest path distance, or "IMPOSSIBLE" if no path exists

## Constraints
- 1 ≤ n ≤ 10^5
- 1 ≤ m ≤ 2×10^5
- -10^9 ≤ w ≤ 10^9
```

**test_cases/example_1.in:**
```
3 3
1 2 5
2 3 -2
1 3 10
1 3
```

**test_cases/example_1.out:**
```
3
```

## Template Structure

The pipeline copies the complete `sample_problem_structure` template, which includes:
- All template files (README.md, test_generator.cpp, etc.)
- Existing test cases structure
- Proper folder organization
- Ready-to-use test generation tools

## Folder Structure

```
pipeline_novel_prompt/
├── __init__.py
├── types.py
├── utils.py
├── nodes.py
├── graph.py
├── README.md
└── prompts/
    ├── __init__.py
    └── novel_prompt.py
``` 