# Prompt template for evaluation code generation

EVALUATION_PROMPT = """You are an expert programming competition judge system developer. Your task is to write Python 3 code that can automatically evaluate C++17 contestant submissions for the problem described below.

Requirements for the generated script:
1. Provide a function `evaluate(solution_source: str, test_cases: list[tuple[str, str]]) -> dict` that accepts:
   • `solution_source`: C++17 source code as a single string.
   • `test_cases`: A list of `(input_string, expected_output_string)` tuples.

2. Inside `evaluate` the script must:
   • Write `solution_source` to a file named `solution.cpp` in a temporary directory.
   • Compile it with `g++ -std=c++17 -O2 solution.cpp -o solution.out`.
   • For each test case:
       a. Run the executable, feeding the `input_string` via STDIN.
       b. Capture STDOUT, strip trailing whitespace and new-lines.
       c. Trim whitespace from `expected_output_string` as well.
       d. Compare the two strings for an exact match.
       e. Record pass/fail along with the actual output and optional runtime.
   • Impose a 2-second timeout per test using `subprocess.run(..., timeout=2)`.
   • Handle compilation errors, runtime errors, or timeouts gracefully by marking all tests as failed and returning an informative error message.

3. After testing all cases, return a summary dictionary with keys:
   • `passed`: int  – number of tests passed.
   • `total`:  int  – total number of tests.
   • `failed_cases`: list[dict] – details for each failed test including `input`, `expected`, `actual`.
   • `compile_error` (optional str) – full compiler stderr if compilation fails.

4. Also include a `__main__` guard so the script can be run directly as:
   `python judge.py solution.cpp tests.json` (but keep this minimal; the core is the `evaluate` function).

Important guidelines:
- Use only the Python standard library (`subprocess`, `tempfile`, `os`, `json`, `textwrap`, `time`).
- Write clean, well-commented, and robust code that works on POSIX systems.
- Do NOT output the original problem statement or any explanation text – ONLY the Python code.

Problem Statement:
{problem_statement}

Do NOT wrap the code in markdown fences. Output ONLY the raw Python code, nothing else."""

__all__ = ["EVALUATION_PROMPT"]
