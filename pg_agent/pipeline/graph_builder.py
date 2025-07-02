from langgraph.graph import StateGraph
from .run_tests import run_tests_fn
from .critique import critique_fn
from .verdict import verdict_fn
from pipeline.run_tests import run_tests_fn
from pipeline.critique import critique_fn
from pipeline.verdict import verdict_fn
# This file builds the state graph for the pipeline, connecting the run_tests, critique, and verdict functions.
def build_graph():
    from typing import TypedDict

    class State(TypedDict):
        problem: str
        solution_code: str
        tests: str
        results: dict | None
        critique: str | None
        verdict: str | None

    g = StateGraph(State)

    g.add_node("RunTests", run_tests_fn)
    g.add_node("Critique", critique_fn)
    g.add_node("Verdict", verdict_fn)

    def condition_branch(state):
        return "Critique" if state["results"]["failed"] > 0 else "Verdict"

    g.add_conditional_edges(
        "RunTests",
        condition_branch,
        {
            "Critique": "Critique",
            "Verdict": "Verdict"
        }
    )

    g.add_edge("Critique", "Verdict")
    g.set_entry_point("RunTests")
    g.set_finish_point("Verdict")

    return g.compile()

