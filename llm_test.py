import os
from openai import OpenAI
from openai import OpenAIError, BadRequestError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def debug_model(model_name: str):
    try:
        # quick ping
        response = client.responses.create(
            model=model_name,
            reasoning={"effort": "medium"},
            input=[{"role": "user", "content": "Latest ufc updates"}],
            tools=[{"type": "web_search_preview"}],
        )
        print(f"{model_name}: success")
        print(f"Response: {response.output_text}")
    except BadRequestError as e:
        print(f"{model_name}: {e}")
    except OpenAIError as e:
        print(f"{model_name}: {e}")


# list the models your key can see
# models = client.models.list()
# print([model.id for model in models.data])

# test the model that’s giving trouble
debug_model("o3-2025-04-16")  # will raise “model does not exist”
# debug_model("gpt-4.1-2025-04-14")  # or any model you know works
