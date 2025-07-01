import os
import openai

# Optional: load from env or hardcode
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_llm(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a senior software engineer helping a junior developer debug code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[LLM call failed: {e}]"

def critique_fn(state):
    prompt = open("prompts/critique.txt").read().format(
        problem=state["problem"],
        solution_code=state["solution_code"],
        results=state["results"]["output"]
    )
    response = call_llm(prompt)
    state["critique"] = response
    return state
	