# PG-Agent Workflows

This directory contains a system of modular, independent workflows for the Programming Agent. Unlike a single, monolithic agent, these workflows are designed to be run as separate, focused tasks. This allows for a more controlled and step-by-step approach to creating and validating competitive programming problems.

## Core Concepts

### 1. The `repo_template` Directory

Located at the project root, this directory provides the basic scaffolding for a new problem. A user starts by copying this template to a new folder (e.g., `my_new_problem/`). They are expected to:

* Edit `problem_statement.md` with the full problem description, constraints, and examples.
* Create `example_1.in`, `example_1.out`, `example_2.in`, etc., inside the `my_new_problem/test_cases/` directory. These files must correspond exactly to the examples given in the problem statement.

### 2. The `automation` Directory

For each problem, an `automation` folder will be created *inside* that *problem's* directory (e.g., `my_new_problem/automation/`). This folder acts as the central, version-controlled "brain" for that specific problem. As the workflows run, they will populate this directory with versioned artifacts (solutions, test case generators, etc.), ensuring a clean, auditable history.

## How to Run a Workflow

All workflows are executed from the project root directory using the master `run.py` script. You must provide the workflow name and the path to the relevant problem directory.

**General Command Format:**

`python -m pg_agent.workflows.run --workflow <WORKFLOW_NAME> --<ARGUMENTS>`

## Available Workflows

### Workflow: `create_novel_problem` (New)

* **Purpose:** To act as a creative partner in generating a brand new problem from scratch. It creates a new problem directory, then enters an interactive loop allowing you to generate and refine a problem statement until you are satisfied. Finally, it generates a set of initial example test cases. This is the recommended starting point for any new problem.
* **Prerequisites:** None.
* **Command:**
    ```
    # Basic usage: creates a new problem in 'my_new_problem' based on topics
    python -m pg_agent.workflows.run --workflow create_novel_problem --output_dir ./my_new_problem --topics "dynamic programming, arrays"

    # Advanced usage: creates a new problem based on an existing one and a specific idea
    python -m pg_agent.workflows.run --workflow create_novel_problem --output_dir ./another_problem --context_dir ./my_new_problem --user_prompt "Make a variation that includes negative numbers."
    ```
* **Output:**
    * A new directory (e.g., `./my_new_problem/`) based on the `repo_template`.
    * A finalized `problem_statement.md` inside the new directory.
    * A set of `example_*.in` and `example_*.out` files inside the `test_cases` sub-directory.

### Workflow: `create_brute_force`

* **Purpose:** To read an existing problem statement and its examples, and then use an LLM to generate, test, and refine a correct bruteforce C++ solution until it passes all provided examples.
* **Prerequisites:** A problem directory that already contains a `problem_statement.md` and one or more `example_*.in`/`.out` files. (Typically run after `create_novel_problem`).
* **Command:**
    ```
    python -m pg_agent.workflows.run --workflow create_brute_force --problem_dir ./my_new_problem
    ```
* **Output:**
    * Saves the final, correct solution to `automation/bruteForceSol/bf_v0.cpp` inside your problem directory.
    * Creates/updates `automation/automation_settings.json` with the new version number.

### Workflow: `generate_test_cases`

* **Purpose:** To generate three crucial C++ scripts: one for creating many small/tricky test cases, one for creating large stress-test cases, and a validator to check input format correctness.
* **Prerequisites:** You must have already run the `create_brute_force` workflow successfully.
* **Command:**
    ```
    python -m pg_agent.workflows.run --workflow generate_test_cases --problem_dir ./my_new_problem
    ```
* **Output:**
    * Saves the three generated scripts to the `automation/testcaseGenScript/` directory with version numbers.
    * Updates `automation/automation_settings.json` with the new version numbers.

### Workflow: `validate_and_run_tests`

* **Purpose:** To execute the C++ generator scripts, validate all generated inputs, and then run the bruteforce solution on the valid small test cases to generate the final `.out` files.
* **Prerequisites:** You must have already run the `generate_test_cases` workflow successfully.
* **Command:**
    ```
    python -m pg_agent.workflows.run --workflow validate_and_run_tests --problem_dir ./my_new_problem
    ```
* **Output:**
    * Populates the `automation/testcases/` directory with all the generated and validated `.in` and `.out` files.
    * Creates `automation/testcases/invalid_testcases.json` to log any tests that failed validation or timed out.