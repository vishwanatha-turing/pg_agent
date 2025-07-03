from pg_agent.pipeline.edge_case_suggester import graph, compile_with_memory
from pathlib import Path
import json


def test_edge_case_suggester():
    problem = Path("pg_agent/examples/sum_of_array.md").read_text()
    compiled = compile_with_memory()
    result = compiled.invoke({"problem_spec": problem, "feedback": ""})
    edge_cases = result["edge_cases"]

    assert isinstance(edge_cases, list)
    assert len(edge_cases) <= 25
    assert len(edge_cases) == len(
        set(json.dumps(ec) for ec in edge_cases)
    )  # no duplicates

    # Also ensure pipeline runs end-to-end starting from empty state (random topics)
    compiled.update_state(
        {}, {"feedback": "", "accepted": True}, as_node="HumanFeedback"
    )
    full_run = compiled.get_state({"configurable": {"thread_id": "1"}}).values
