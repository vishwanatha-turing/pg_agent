def verdict_fn(state):
    state["verdict"] = "PASS" if state["results"]["failed"] == 0 else "FAIL"
    return state
