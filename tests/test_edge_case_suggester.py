from pg_agent.pipeline.edge_case_suggester import graph
from pathlib import Path
import json


def test_edge_case_suggester():
    problem = Path("pg_agent/examples/sum_of_array.md").read_text()
    result = graph.compile().invoke({"problem_spec": problem})
    edge_cases = result["edge_cases"]

    assert isinstance(edge_cases, list)
    assert len(edge_cases) <= 25
    assert len(edge_cases) == len(
        set(json.dumps(ec) for ec in edge_cases)
    )  # no duplicates

    # Also ensure pipeline runs end-to-end starting from empty state (random topics)
    full_run = graph.compile().invoke({})
    assert "edge_cases" in full_run
    assert isinstance(full_run["edge_cases"], list)
