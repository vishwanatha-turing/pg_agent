import os
import openai
from dotenv import load_dotenv
from prompts.critique import CRITIQUE_PROMPT 

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_llm(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer helping a junior developer debug code."
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
        prompt = CRITIQUE_PROMPT.format(
            problem=state["problem"],
            solution_code=state["solution_code"],
            results=state["results"]["output"]
        )

        state["critique"] = call_llm(prompt)

    except Exception as e:
        state["critique"] = f"[Critique generation failed: {e}]"

    return state
