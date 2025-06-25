# evaluation_runner.py
"""Node that executes the generated evaluation script against the C++ solution.

Inputs expected in the LangGraph *state*:
    • "evaluation_code"  – Python source code string with an `evaluate()` function.
    • "cpp_solution"     – Raw C++17 source code.
    • "test_cases"       – List[Tuple[str, str]] of (input, expected_output).

Outputs written back to the state:
    • "test_results"     – Dict returned by `evaluate()` (passed, total, failed_cases…).
"""

from __future__ import annotations

import sys
import types
import uuid
from typing import List, Tuple, Dict, Any

__all__ = [
    "run_evaluation",
    "evaluation_runner_node",
]


def _load_module_from_code(source: str):
    """Exec *source* in a fresh module and return it."""
    module_name = f"_gen_evaluator_{uuid.uuid4().hex}"
    mod = types.ModuleType(module_name)
    # Ensure the module can import itself if needed (rare but safe to add)
    sys.modules[module_name] = mod
    exec(source, mod.__dict__)
    return mod


def run_evaluation(
    evaluation_code: str, cpp_solution: str, test_cases: List[Tuple[str, str]]
) -> Dict[str, Any]:
    """Execute *evaluation_code*'s `evaluate()` on the given solution and tests."""

    module = _load_module_from_code(evaluation_code)
    evaluate = getattr(module, "evaluate", None)
    if not callable(evaluate):
        raise AttributeError(
            "Provided evaluation_code does not define an 'evaluate' function"
        )

    return evaluate(cpp_solution, test_cases)


# ---------------------------------------------------------------------------
# LangGraph node wrapper
# ---------------------------------------------------------------------------


def evaluation_runner_node(state):
    """LangGraph node: runs evaluator and stores results under `test_results`."""

    evaluation_code = state.get("evaluation_code")
    cpp_solution = state.get("cpp_solution")
    test_cases = state.get("test_cases")

    if evaluation_code is None:
        raise ValueError("evaluation_code missing from state")
    if cpp_solution is None:
        raise ValueError("cpp_solution missing from state")
    if test_cases is None:
        raise ValueError("test_cases missing from state")

    results = run_evaluation(evaluation_code, cpp_solution, test_cases)

    return {"test_results": [results]}


if __name__ == "__main__":
    # Simple smoke-test using a tiny handwritten evaluator and problem.
    dummy_eval = """
import subprocess, tempfile, os, json, textwrap

def evaluate(solution_source: str, test_cases):
    with tempfile.TemporaryDirectory() as tmp:
        src_path = os.path.join(tmp, 'main.cpp')
        with open(src_path, 'w') as f:
            f.write(solution_source)
        bin_path = os.path.join(tmp, 'a.out')
        compile_res = subprocess.run(['g++', '-std=c++17', src_path, '-o', bin_path])
        if compile_res.returncode != 0:
            return {'passed': 0, 'total': len(test_cases), 'compile_error': 'Compilation failed'}
        passed = 0
        failed_cases = []
        for idx, (inp, exp) in enumerate(test_cases):
            run = subprocess.run([bin_path], input=inp.encode(), capture_output=True)
            out = run.stdout.decode().strip()
            if out == exp.strip():
                passed += 1
            else:
                failed_cases.append({'id': idx, 'input': inp, 'expected': exp, 'actual': out})
        return {'passed': passed, 'total': len(test_cases), 'failed_cases': failed_cases}
"""

    dummy_solution = """
#include <bits/stdc++.h>
using namespace std;int main(){ios::sync_with_stdio(false);cin.tie(nullptr);int a,b; if(!(cin>>a>>b)) return 0; cout<<a+b<<"\n"; return 0;}"""

    dummy_tests = [("3 4\n", "7")]

    print(run_evaluation(dummy_eval, dummy_solution, dummy_tests))
