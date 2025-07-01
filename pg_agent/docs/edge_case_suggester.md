# Edge Case Suggester

This LangGraph mini-pipeline helps developers automatically generate tricky edge-case inputs for coding problems.

## Usage

```bash
python -m pg_agent.pipeline.edge_case_suggester pg_agent/examples/sum_of_array.md
```

The command prints a JSON array (max 25 items) containing diverse test inputs tailored to the provided problem statement. 