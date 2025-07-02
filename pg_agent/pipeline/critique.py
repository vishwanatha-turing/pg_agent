import os
import openai
from dotenv import load_dotenv  # Load from .env file if needed

# Load environment variables from .env (if present)
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_llm(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or use "gpt-3.5-turbo" for lower cost
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
        # Load and format the prompt template
        with open("prompts/critique.txt", "r", encoding="utf-8") as f:
            template = f.read()

        prompt = template.format(
            problem=state["problem"],
            solution_code=state["solution_code"],
            results=state["results"]["output"]
        )

        # Call LLM and store response
        response = call_llm(prompt)
        state["critique"] = response

    except Exception as e:
        state["critique"] = f"[Critique generation failed: {e}]"

    return state
