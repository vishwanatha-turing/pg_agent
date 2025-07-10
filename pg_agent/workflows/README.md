# PG-Agent Workflows

This directory contains a system of modular, independent workflows for the Programming Agent. Unlike a single, monolithic agent, these workflows are designed to be run as separate, focused tasks. This allows for a more controlled and step-by-step approach to creating and validating competitive programming problems.

## Core Concepts

### 1. The `repo_template` Directory
Located at the project root, this directory provides the basic scaffolding for a new problem. A user starts by copying this template to a new folder (e.g., `my_new_problem/`). They are expected to:
-   Edit `problem_statement.md` with the full problem description, constraints, and examples.
-   Create `example_1.in`, `example_1.out`, `example_2.in`, etc., inside the `my_new_problem/test_cases/` directory. These files must correspond exactly to the examples given in the problem statement.

### 2. The `automation` Directory
For each problem, an `automation` folder will be created *inside* that *problem's directory* (e.g., `my_new_problem/automation/`). This folder acts as the central, version-controlled "brain" for that specific problem. As the workflows run, they will populate this directory with versioned artifacts (solutions, test case generators, etc.), ensuring a clean, auditable history.

## How to Run a Workflow

All workflows are executed from the project root directory using the master `run.py` script. You must provide the workflow name and the path to the problem directory you are working on.

**General Command Format:**
```bash
python -m pg_agent.workflows.run --workflow <WORKFLOW_NAME> --problem_dir <PATH_TO_PROBLEM_DIR>
````

-----

## Available Workflows

### Workflow: `create_brute_force`

  - **Purpose:** To read a problem statement and its examples, and then use an LLM to generate, test, and refine a correct bruteforce C++ solution until it passes all provided examples.
  - **Prerequisites:** You must have a problem directory set up with:
    1.  A complete `problem_statement.md`.
    2.  One or more `example_*.in` and `example_*.out` files in the `test_cases` sub-directory.
  - **Command:**
    ```bash
    python -m pg_agent.workflows.run --workflow create_brute_force --problem_dir ./repo_template
    ```
  - **Output:**
      - Creates an `automation` folder inside your problem directory.
      - Saves the final, correct solution to `automation/bruteForceSol/bf_v0.cpp`.
      - Creates/updates `automation/automation_settings.json` with the new version number.

### Workflow: `generate_test_cases`

  - **Purpose:** To generate three crucial C++ scripts: one for creating many small/tricky test cases, one for creating large stress-test cases, and a validator to check input format correctness.
  - **Prerequisites:** You must have already run the `create_brute_force` workflow successfully, as this workflow needs the problem statement and the verified bruteforce solution for context.
  - **Command:**
    ```bash
    python -m pg_agent.workflows.run --workflow generate_test_cases --problem_dir ./repo_template
    ```
  - **Output:**
      - Saves the three generated scripts to the `automation/testcaseGenScript/` directory with version numbers (e.g., `small_test_gen_path_v0.cpp`, `stress_test_gen_path_v0.cpp`, `validator_path_v0.cpp`).
      - Updates `automation/automation_settings.json` with the new version numbers for each script.

### Workflow: `validate_and_run_tests`

  - **Purpose:** To execute the C++ generator scripts, validate all generated inputs, and then run the bruteforce solution on the valid small test cases to generate the final `.out` files.
  - **Prerequisites:** You must have already run the `generate_test_cases` workflow successfully, as this workflow needs the C++ generator and validator scripts from the `automation` directory.
  - **Command:**
    ```bash
    python -m pg_agent.workflows.run --workflow validate_and_run_tests --problem_dir ./repo_template
    ```
  - **Output:**
      - Populates the `test_cases` directory inside your problem directory with all the generated and validated `.in` and `.out` files.
      - Prints a summary of how many tests were generated, validated, and how many (if any) were discarded due to the bruteforce solution timing out.
