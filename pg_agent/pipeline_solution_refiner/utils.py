"""Utility functions for compilation, execution, and code processing."""

import subprocess
import tempfile
from pathlib import Path
import logging
import os
import textwrap
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pg_agent.prompts.solution_refiner import (
    GENERATE_SOLUTION_PROMPT,
    FIX_SOLUTION_PROMPT,
)

load_dotenv()


def get_llm(temp=1):
    """Get configured LLM instance."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    return ChatOpenAI(model="gpt-4.1-2025-04-14", temperature=temp)


def get_o3_llm(temp=1):
    """Get configured LLM instance."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    return ChatOpenAI(
        model="o3-2025-04-16", temperature=temp, reasoning={"effort": "low"}
    )


def get_o4_mini_llm(temp=1):
    """Get configured LLM instance."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    return ChatOpenAI(model="o4-mini", temperature=temp)


def strip_code_fences(text: str) -> str:
    """Strip ``` or ```cpp fences from code blocks."""
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text.strip()


def compile_and_run(src: str, tests: list[tuple[str, str]]):
    """
    Local compilation and execution (single, canonical method).
    """
    logger = logging.getLogger("compile_run")
    logger.setLevel(logging.INFO)

    with tempfile.TemporaryDirectory() as tmp:
        cpp_path = Path(tmp) / "main.cpp"
        bin_path = Path(tmp) / "a.out"

        # Write source code
        cpp_path.write_text(src)

        # Compile
        compile_res = subprocess.run(
            [
                "g++",
                "-std=c++17",
                "-O2",
                "-Wall",
                "-Wextra",
                str(cpp_path),
                "-o",
                str(bin_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second compilation timeout
        )

        if compile_res.returncode != 0:
            logger.error("Compilation failed:\n%s", compile_res.stderr)
            return {
                "compile_error": compile_res.stderr,
                "failing_tests": [],
                "passing_tests": [],
            }

        # Run tests
        failed = []
        passed = []
        logger.info("Running %d test cases", len(tests))

        for idx, (inp, exp) in enumerate(tests):
            try:
                run = subprocess.run(
                    [str(bin_path)],
                    input=inp,
                    capture_output=True,
                    text=True,
                    timeout=5,  # 5 second runtime timeout per test
                    cwd=tmp,  # Run in temp directory
                )

                out = run.stdout.strip()
                err = run.stderr.strip()

                logger.info(
                    "Test %d: input='%s', expected='%s', actual='%s', stderr='%s'",
                    idx,
                    inp,
                    exp.strip(),
                    out,
                    err,
                )

                if out != exp.strip():
                    failed.append(
                        {
                            "input": inp,
                            "expected": exp,
                            "actual": out,
                            "stderr": err if err else None,
                            "return_code": run.returncode,
                        }
                    )
                else:
                    passed.append(
                        {
                            "input": inp,
                            "expected": exp,
                            "actual": out,
                            "stderr": err if err else None,
                            "return_code": run.returncode,
                        }
                    )

            except subprocess.TimeoutExpired:
                logger.error("Test %d timed out", idx)
                failed.append(
                    {
                        "input": inp,
                        "expected": exp,
                        "actual": "TIMEOUT",
                        "stderr": "Test execution timed out after 5 seconds",
                        "return_code": -1,
                    }
                )

            except Exception as e:
                logger.error("Test %d failed with exception: %s", idx, str(e))
                failed.append(
                    {
                        "input": inp,
                        "expected": exp,
                        "actual": "ERROR",
                        "stderr": f"Runtime error: {str(e)}",
                        "return_code": -1,
                    }
                )

        logger.info(
            "Passed %d, Failed %d out of %d test cases",
            len(passed),
            len(failed),
            len(tests),
        )

        return {
            "failing_tests": failed,
            "passing_tests": passed,
            "compile_error": None,
        }


# Prompt templates
solution_prompt = ChatPromptTemplate.from_messages(
    [("system", GENERATE_SOLUTION_PROMPT)]
)
fix_prompt = ChatPromptTemplate.from_messages([("system", FIX_SOLUTION_PROMPT)])


def extract_content_from_o3_response(msg):
    """Extract content from O3's structured response format."""
    if isinstance(msg.content, list) and msg.content:
        # O3 returns list of reasoning steps
        # Get the text from the last step (usually contains the final answer)
        last_step = msg.content[-1]
        if isinstance(last_step, dict) and "text" in last_step:
            return last_step["text"]
        else:
            return str(last_step)
    else:
        # Fallback for other formats
        return str(msg.content)
