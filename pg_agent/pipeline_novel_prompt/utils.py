"""Utility functions for the novel prompt pipeline."""

import os
import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pg_agent.pipeline_novel_prompt.prompts.novel_prompt import (
    GENERATE_PROBLEM_STATEMENT_PROMPT,
    GENERATE_TEST_CASES_PROMPT,
)

load_dotenv()


def get_llm(temp=1):
    """Get configured LLM instance."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    return ChatOpenAI(model="gpt-4.1-2025-04-14", temperature=temp)


def setup_output_structure(output_folder: str) -> Tuple[str, str]:
    """Setup the output folder structure by copying from template."""
    output_path = Path(output_folder)

    # Get the template path (sample_problem_structure)
    template_path = Path(__file__).parent.parent.parent / "sample_problem_structure"

    if not template_path.exists():
        raise FileNotFoundError(f"Template directory not found: {template_path}")

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Check if we need to copy template files
    required_files = [
        "test_generator.cpp",
        "standard.cpp",
        "requirements.json",
        "README.md",
    ]
    missing_files = [f for f in required_files if not (output_path / f).exists()]

    if missing_files:
        # Only copy if we're missing template files
        logging.info(f"Missing template files: {missing_files}")
        shutil.copytree(template_path, output_path, dirs_exist_ok=True)
        logging.info(f"Template files copied to: {output_path}")
    else:
        logging.info(f"Template structure already exists at: {output_path}")

    # Define file paths based on template structure
    problem_statement_file = output_path / "problem_statement.md"
    test_cases_folder = output_path / "test_cases"

    return str(problem_statement_file), str(test_cases_folder)


def save_problem_statement(content: str, file_path: str):
    """Save the problem statement to a markdown file."""
    Path(file_path).write_text(content)
    logging.info(f"Problem statement saved to: {file_path}")


def save_test_cases(test_cases: List[Tuple[str, str]], folder_path: str):
    """Save test cases as example_*.in and example_*.out files."""
    folder = Path(folder_path)

    # Clear existing example files
    for example_file in folder.glob("example_*.in"):
        example_file.unlink()
    for example_file in folder.glob("example_*.out"):
        example_file.unlink()

    # Save new test cases as example_*.in/out
    for idx, (input_data, expected_output) in enumerate(test_cases, 1):
        # Save input file
        input_file = folder / f"example_{idx}.in"
        input_file.write_text(input_data)

        # Save output file
        output_file = folder / f"example_{idx}.out"
        output_file.write_text(expected_output)

        logging.info(f"Test case {idx} saved: {input_file.name}, {output_file.name}")


def parse_test_cases_from_llm_response(response: str) -> List[Tuple[str, str]]:
    """Parse test cases from LLM response."""
    test_cases = []
    lines = response.split("\n")

    current_input = None
    current_output = None

    logging.info(f"Parsing test cases from response with {len(lines)} lines")

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Check for input patterns
        if (
            line.startswith("Input:")
            or line.startswith("input:")
            or line.startswith("Test Case")
            and "Input" in line
        ):
            if current_input is not None and current_output is not None:
                test_cases.append((current_input, current_output))
                logging.info(
                    f"Added test case {len(test_cases)}: input='{current_input[:50]}...', output='{current_output[:50]}...'"
                )

            # Extract input after colon
            if ":" in line:
                current_input = line.split(":", 1)[1].strip()
            else:
                current_input = ""
            current_output = None

        # Check for output patterns
        elif (
            line.startswith("Expected Output:")
            or line.startswith("Output:")
            or line.startswith("output:")
            or line.startswith("Expected:")
            or line.startswith("expected:")
        ):
            if ":" in line:
                current_output = line.split(":", 1)[1].strip()
            else:
                current_output = ""

        # If we have input but no output yet, and this line doesn't start with a keyword, it might be the input content
        elif (
            current_input is not None
            and current_output is None
            and not any(
                line.startswith(keyword)
                for keyword in [
                    "Input:",
                    "Output:",
                    "Expected:",
                    "Test Case",
                    "Description:",
                ]
            )
        ):
            if current_input == "":
                current_input = line
            else:
                current_input += "\n" + line

        # If we have both input and output, and this line doesn't start with a keyword, it might be the output content
        elif (
            current_input is not None
            and current_output is not None
            and not any(
                line.startswith(keyword)
                for keyword in [
                    "Input:",
                    "Output:",
                    "Expected:",
                    "Test Case",
                    "Description:",
                ]
            )
        ):
            if current_output == "":
                current_output = line
            else:
                current_output += "\n" + line

    # Add the last test case
    if current_input is not None and current_output is not None:
        test_cases.append((current_input, current_output))
        logging.info(
            f"Added final test case {len(test_cases)}: input='{current_input[:50]}...', output='{current_output[:50]}...'"
        )

    # If no test cases found, try alternative parsing
    if not test_cases:
        logging.warning(
            "No test cases found with standard parsing, trying alternative format"
        )
        test_cases = parse_test_cases_alternative(response)

    logging.info(f"Parsed {len(test_cases)} test cases total")
    return test_cases


def parse_test_cases_alternative(response: str) -> List[Tuple[str, str]]:
    """Alternative parsing method for different LLM response formats."""
    test_cases = []

    # Look for patterns like "Test Case 1:", "Example 1:", etc.
    import re

    # Split by test case markers
    test_case_sections = re.split(
        r"(?:Test Case|Example|Case)\s*\d+:", response, flags=re.IGNORECASE
    )

    for section in test_case_sections[
        1:
    ]:  # Skip the first section (before first test case)
        lines = section.strip().split("\n")
        input_data = ""
        output_data = ""

        in_input = False
        in_output = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "input" in line.lower() and ":" in line:
                in_input = True
                in_output = False
                input_data = line.split(":", 1)[1].strip()
            elif "output" in line.lower() and ":" in line:
                in_input = False
                in_output = True
                output_data = line.split(":", 1)[1].strip()
            elif in_input:
                input_data += "\n" + line
            elif in_output:
                output_data += "\n" + line

        if input_data and output_data:
            test_cases.append((input_data, output_data))

    return test_cases


def detect_previous_problem(output_folder: str) -> Optional[str]:
    """Auto-detect if output folder exists and load previous problem statement."""
    problem_file = Path(output_folder) / "problem_statement.md"
    if problem_file.exists():
        try:
            content = problem_file.read_text()
            if content.strip():  # Check if file is not empty
                logging.info(f"Auto-loaded previous problem from: {problem_file}")
                return content
            else:
                logging.warning(
                    f"Problem statement file exists but is empty: {problem_file}"
                )
                return None
        except Exception as e:
            logging.error(f"Failed to read previous problem statement: {str(e)}")
            return None
    return None


# Prompt templates
problem_statement_prompt = ChatPromptTemplate.from_messages(
    [("system", GENERATE_PROBLEM_STATEMENT_PROMPT)]
)
test_cases_prompt = ChatPromptTemplate.from_messages(
    [("system", GENERATE_TEST_CASES_PROMPT)]
)
