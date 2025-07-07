from .graph_builder import build_graph

def main():
    state = {
        "problem": open("examples/sum_of_array.md").read(),
        "solution_code": open("examples/sum_of_array.py").read(),
        "tests": open("examples/test_sum_of_array.py").read()
    }

    graph = build_graph()
    out = graph.invoke(state)

    print("Verdict:", out["verdict"])
    if out["verdict"] == "FAIL":
        print("\nCritique:\n", out["critique"])

if __name__ == "__main__":
    main()

