from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Tuple, Dict, Any
from pathlib import Path
import subprocess
import difflib
import os
import json
import asyncio

# === Constants ===
PROBLEM_PATH = Path("problem.md")
TEST_CASES_DIR = Path("test_cases")
QWEN_DIR = Path("qwen")
ATTEMPT_COUNT = 16
FINAL_RESULTS_FILE = Path("final_results.json")

# === Graph State ===
class GraphState(TypedDict):
    problem_text: str
    test_cases: List[Tuple[str, str, str, str]]  # (in_name, out_name, input, expected)
    all_results: List[Dict[str, Any]]

# === Load Problem ===
def load_problem_node(state: GraphState) -> GraphState:
    with open(PROBLEM_PATH, "r", encoding="utf-8") as f:
        problem_text = f.read()
    return {**state, "problem_text": problem_text, "all_results": []}

# === Load Test Cases ===
def load_test_cases_node(state: GraphState) -> GraphState:
    in_files = {f.stem: f for f in TEST_CASES_DIR.glob("*.in")}
    out_files = {f.stem: f for f in TEST_CASES_DIR.glob("*.out")}
    test_cases = []

    for key in sorted(set(in_files) & set(out_files)):
        with open(in_files[key], "r", encoding="utf-8") as f_in, open(out_files[key], "r", encoding="utf-8") as f_out:
            test_cases.append((in_files[key].name, out_files[key].name, f_in.read(), f_out.read()))

    print(f"[INFO] Loaded {len(test_cases)} test cases.")
    return {**state, "test_cases": test_cases}

# === Compile and Run Tests in Parallel ===
async def compile_and_test_one(idx: int, test_cases: List[Tuple[str, str, str, str]]) -> List[Dict[str, Any]]:
    cpp_file = QWEN_DIR / f"run_{idx}.cpp"
    exe_path = cpp_file.with_suffix(".exe")
    results = []

    if not cpp_file.exists():
        print(f"[WARNING] Missing file: {cpp_file}")
        return results

    compile_result = subprocess.run(["g++", "-O2", "-std=c++17", str(cpp_file), "-o", str(exe_path)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if compile_result.returncode != 0:
        print(f"[FAIL] Compilation failed for {cpp_file.name}:")
        print(compile_result.stderr.decode())
        return results

    print(f"[OK] Compiled: {cpp_file.name}")
    
    for in_name, out_name, input_data, expected_output in test_cases:
        result_entry = {
            "attempt": f"run_{idx}.cpp",
            "input_file": in_name,
            "output_file": out_name
        }
        try:
            proc = subprocess.run([str(exe_path)], input=input_data.encode(),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            actual_output = proc.stdout.decode()
            passed = actual_output.strip() == expected_output.strip()
            result_entry["passed"] = passed
            result_entry["diff"] = ""

            if passed:
                print(f"  ✔ {in_name} → {out_name}: PASS")
            else:
                print(f"  ✘ {in_name} → {out_name}: FAIL")
                diff = difflib.unified_diff(
                    expected_output.strip().splitlines(),
                    actual_output.strip().splitlines(),
                    fromfile='expected',
                    tofile='actual',
                    lineterm=''
                )
                result_entry["diff"] = "\n".join(diff)

        except subprocess.TimeoutExpired:
            print(f"  ⚠ {in_name}: TIMEOUT")
            result_entry["passed"] = False
            result_entry["error"] = "TIMEOUT"
        except Exception as e:
            print(f"  ⚠ {in_name}: ERROR - {e}")
            result_entry["passed"] = False
            result_entry["error"] = str(e)

        results.append(result_entry)

    exe_path.unlink(missing_ok=True)
    return results

# === Run All in Parallel ===
def run_all_attempts_node(state: GraphState) -> GraphState:
    async def run_all():
        tasks = [compile_and_test_one(i, state["test_cases"]) for i in range(1, ATTEMPT_COUNT + 1)]
        all_results_nested = await asyncio.gather(*tasks)
        return [item for sublist in all_results_nested for item in sublist]

    all_results = asyncio.run(run_all())
    return {**state, "all_results": all_results}

# === Save Results ===
def save_results_node(state: GraphState) -> GraphState:
    with open(FINAL_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(state["all_results"], f, indent=2)
    print(f"\n[INFO] Final results saved to {FINAL_RESULTS_FILE}")
    return state

# === Build LangGraph ===
def build_graph():
    builder = StateGraph(GraphState)
    builder.set_entry_point("LoadProblem")

    builder.add_node("LoadProblem", load_problem_node)
    builder.add_node("LoadTestCases", load_test_cases_node)
    builder.add_node("RunAllAttempts", run_all_attempts_node)
    builder.add_node("SaveResults", save_results_node)

    builder.add_edge("LoadProblem", "LoadTestCases")
    builder.add_edge("LoadTestCases", "RunAllAttempts")
    builder.add_edge("RunAllAttempts", "SaveResults")
    builder.add_edge("SaveResults", END)

    return builder.compile()

# === Entry Point ===
app = build_graph()

if __name__ == "__main__":
    app.invoke({})
