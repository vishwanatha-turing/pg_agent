import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_llm(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer helping a junior developer debug their code."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[LLM call failed: {e}]"


def critique_fn(state):
    try:
        # Format the full prompt inline (was previously in critique.txt)
        prompt = f"""
Here is the problem they were trying to solve:

<<<{state["problem"]}>>>

And here is the code they submitted:

{state["solution_code"]}

The following tests were run, and some of them failed. Here's the test output:

{state["results"]["output"]}

Please do the following:

1. Clearly explain why the code failed. Reference specific lines or logic mistakes if possible.
2. Provide a concise, concrete suggestion for how to fix the issue — no generalities.
3. Do NOT rewrite the entire code. Instead, focus on the mistake and how to fix it.

Respond in 2 short paragraphs maximum.
""".strip()

        # Call LLM and update state
        state["critique"] = call_llm(prompt)

    except Exception as e:
        state["critique"] = f"[Critique generation failed: {e}]"

    return state
