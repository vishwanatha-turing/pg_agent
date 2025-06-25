from pg_agent.pipeline import test_pipeline as build_test_graph


def test_pipeline_compiles_and_runs():
    graph = build_test_graph()
    result = graph.invoke({})
    assert isinstance(result, dict)
    # After first run we should at least have topics in state
    assert "topics" in result
