# Prompt template for generating LLM-based critique of incorrect solutions

CRITIQUE_PROMPT = """You are a senior software engineer helping a junior developer debug their code.

Here is the problem they were trying to solve:

<<<{problem}>>>

And here is the code they submitted:

{solution_code}

The following tests were run, and some of them failed. Here's the test output:

{results}

Please do the following:

1. Clearly explain why the code failed. Reference specific lines or logic mistakes if possible.
2. Provide a concise, concrete suggestion for how to fix the issue — no generalities.
3. Do NOT rewrite the entire code. Instead, focus on the mistake and how to fix it.

Respond in 2 short paragraphs maximum."""

__all__ = ["CRITIQUE_PROMPT"]
