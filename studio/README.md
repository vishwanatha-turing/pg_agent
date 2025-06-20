# Competitive Programming Problem Generator

A LangGraph-based pipeline for generating, solving, and validating competitive programming problems.

## Overview

This pipeline uses a combination of GPT-4 and Claude to:
1. Select algorithmic topics
2. Generate problem statements
3. Create comprehensive test cases
4. Generate optimized C++ solutions
5. Validate solutions against test cases

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your API keys:
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Components

- `topic_selector.py`: Randomly selects algorithmic topics
- `problem_statement_generator.py`: Generates problem statements using GPT-4
- `test_case_generator.py`: Creates comprehensive test cases
- `solution_generator.py`: Generates optimized C++ solutions using Claude
- `pipeline_graph.py`: Orchestrates the entire workflow

## Usage

Run the pipeline using LangGraph Studio:
```bash
langgraph studio
```

This will start the LangGraph Studio interface where you can:
- Visualize the pipeline graph
- Execute the pipeline
- Monitor state transitions
- Debug individual nodes

## Pipeline Flow

1. Topic Selection → Problem Generation → [Test Case Generation, Solution Generation] → Validation

The pipeline includes parallel execution paths and proper state management through the `PipelineState` class.

## Development

To run tests or experiment with individual components:

```python
from pipeline_graph import test_pipeline

# Run the test pipeline
graph = test_pipeline()
result = graph.invoke({})
```

## Notes

- The solution generator uses Claude Opus for high-quality C++ code generation
- Test cases are generated in a two-step process (scenarios → test cases)
- The pipeline includes error handling and retry mechanisms 