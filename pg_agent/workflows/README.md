# PG-Agent Workflows

This directory contains a system of modular, independent workflows for the Programming Agent. Unlike a single, monolithic agent, these workflows are designed to be run as separate, focused tasks, providing a powerful and flexible system for creating and validating competitive programming problems.

## Core Concepts

### 1. The `repo_template` Directory
Located at the project root, this directory provides the basic scaffolding for a new problem. A user starts by copying this template to a new folder (e.g., `my_new_problem/`). They are expected to:
-   Edit `problem_statement.md` with the full problem description, constraints, and examples.
-   Create `example_1.in`, `example_1.out`, etc., inside the `my_new_problem/test_cases/` directory.

### 2. The `automation` Directory
For each problem, an `automation` folder is created *inside that problem's directory* (e.g., `my_new_problem/automation/`). This folder acts as the central, version-controlled "brain" for that specific problem, storing all generated artifacts like solutions and test case scripts.

## How to Run a Workflow

The entire system is now managed through a single, interactive master menu. To start, run this command from the project root:

**`python -m pg_agent.workflows.run`**

This will launch a menu in your terminal, guiding you through selecting a workflow and providing the necessary inputs.

---

## Available Workflows

### [1] Create a New Novel Problem from Scratch

-   **Purpose:** To act as a creative partner in generating a brand new problem. This is the recommended starting point for any new problem.
-   **Interactive Features:**
    -   **Strategy Selection:** You will be prompted to choose a generation strategy:
        -   **Random Topic:** The agent picks 1-2 topics from a comprehensive list of 150+ topics in `topics.json` to generate a problem.
        -   **Specific Topics:** You provide a comma-separated list of topics.
        -   **Your Own Idea:** The agent opens a text editor for you to write a detailed, multi-line prompt, idea, or even paste content from multiple sources to guide the generation.
    -   **Iterative Refinement:** After the first draft of the problem statement is generated, the agent will repeatedly open a text editor for you to provide feedback. You can refine the problem as many times as you wish until you are satisfied.
-   **Output:**
    -   A new problem directory based on the `repo_template`.
    -   A finalized `problem_statement.md` inside the new directory.
    -   A set of `example_*.in` and `example_*.out` files inside the `test_cases` sub-directory.

### [2] Create a Bruteforce Solution for an Existing Problem

-   **Purpose:** To read an existing problem statement and its examples, and then use an LLM to generate, test, and refine a correct bruteforce C++ solution.
-   **Prerequisites:** A problem directory that already contains a `problem_statement.md` and one or more `example_*.in`/`.out` files.
-   **Interactive Features:**
    -   **Optional Review:** After the bruteforce code is generated, the workflow will ask if you want to review and edit it (`y/N`). If you say yes, it will open the C++ code in your text editor for you to make changes before it is tested.
-   **Output:**
    -   Saves the final, correct solution to `automation/bruteForceSol/bf_v0.cpp`.
    -   Creates/updates `automation/automation_settings.json` with the new version number.

### [3] Generate Test Case Scripts for an Existing Problem

-   **Purpose:** To generate three crucial C++ scripts using highly detailed prompts: one for creating many small/tricky test cases, one for creating large stress-test cases, and a validator to check input format correctness.
-   **Prerequisites:** You must have already run the `create_brute_force` workflow successfully.
-   **Interactive Features:**
    -   **Optional Review:** For each of the three scripts generated (small tests, stress tests, validator), the workflow will ask if you want to review and edit it (`y/N`) before saving the final version.
-   **Output:**
    -   Saves the three generated scripts to the `automation/testcaseGenScript/` directory with version numbers.
    -   Updates `automation/automation_settings.json` with the new version numbers.

### [4] Validate and Run Test Cases for an Existing Problem

-   **Purpose:** To execute the C++ generator scripts, validate all generated inputs, and then run the bruteforce solution on the valid small test cases to generate the final `.out` files.
-   **Prerequisites:** You must have already run the `generate_test_cases` workflow successfully.
-   **Interactive Features:** None. This workflow is fully automated.
-   **Output:**
    -   Populates the `automation/testcases/` directory with all the generated and validated `.in` and `.out` files.
    -   Creates `automation/testcases/invalid_testcases.json` to log any tests that failed validation or timed out against the bruteforce solution.