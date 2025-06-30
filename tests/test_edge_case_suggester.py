from graphs.edge_case_suggester import graph
from pathlib import Path
import json

def test_edge_case_suggester():
    problem = Path("examples/sum_of_array.md").read_text()
    result = graph.invoke({"problem_spec": problem})
    edge_cases = result["edge_cases"]

    assert isinstance(edge_cases, list)
    assert len(edge_cases) <= 25
    assert len(edge_cases) == len(set(json.dumps(ec) for ec in edge_cases))  # no duplicates
