import subprocess
import tempfile
import os

def run_tests_fn(state):
    with tempfile.TemporaryDirectory() as tmpdir:
        sol_path = os.path.join(tmpdir, "solution.py")
        test_path = os.path.join(tmpdir, "test_solution.py")

        with open(sol_path, "w") as f:
            f.write(state["solution_code"])
        with open(test_path, "w") as f:
            f.write(state["tests"])

        result = subprocess.run(
            ["python", "-m", "pytest", "-q", test_path, "--tb=short", "--disable-warnings", "--maxfail=10"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=tmpdir,
        )

        output = result.stdout + result.stderr
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")

        state["results"] = {
            "passed": passed,
            "failed": failed,
            "output": output
        }
        return state
