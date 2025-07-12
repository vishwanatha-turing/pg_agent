import os
import re
import shutil
import subprocess
import tempfile
import json
import random
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import questionary

from .schemas import NovelProblemState

def get_llm_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: raise ValueError("OPENAI_API_KEY not found in environment.")
    return ChatOpenAI(model="o4-mini", api_key=api_key, max_tokens=8192)

def _parse_test_cases(response: str) -> list[tuple[str, str]]:
    """Parses the LLM response using XML-like tags to find test cases."""
    test_cases = []
    for match in re.finditer(r'<test_case>(.*?)</test_case>', response, re.DOTALL):
        block = match.group(1)
        input_match = re.search(r'<input>(.*?)</input>', block, re.DOTALL)
        output_match = re.search(r'<output>(.*?)</output>', block, re.DOTALL)
        if input_match and output_match:
            test_cases.append((input_match.group(1).strip(), output_match.group(1).strip()))
    return test_cases

def _get_user_feedback_from_editor() -> str:
    """Opens a temporary file in the default text editor and returns the user's input."""
    editor = os.environ.get('EDITOR', 'notepad' if os.name == 'nt' else 'vim')
    initial_content = "# Please enter your feedback below. Save and close this file to continue.\n" \
                      "# To accept the current version and generate test cases, save and close this file without adding any other text.\n"
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt", encoding="utf-8") as tf:
        feedback_file_path = tf.name
        tf.write(initial_content)
    
    print(f"Opening feedback file with '{editor}'...")
    try:
        subprocess.run([editor, feedback_file_path], check=True)
    except Exception as e:
        print(f"\nError opening editor: {e}. Please manually open and edit the file.")
        print(f"Feedback file path: {feedback_file_path}")
        input("Press Enter to continue after you have saved and closed the file...")

    feedback_content = Path(feedback_file_path).read_text(encoding="utf-8")
    os.unlink(feedback_file_path)
    
    lines = [line for line in feedback_content.splitlines() if not line.strip().startswith('#')]
    return "\n".join(lines).strip()

# --- Node Definitions ---

def interactive_setup_node(state: NovelProblemState) -> dict:
    """Interactively asks the user for the generation strategy and gathers inputs."""
    print("--- Welcome to the Novel Problem Creator ---")
    
    output_path = Path(state['output_dir'])
    template_path = Path(__file__).parent.parent.parent.parent / "repo_template"
    if not template_path.exists():
        raise FileNotFoundError(f"Template directory not found at: {template_path}")
    if output_path.exists():
        print(f"Warning: Output directory '{output_path}' already exists. Files may be overwritten.")
    else:
        shutil.copytree(template_path, output_path)
        print(f"Created new problem directory at '{output_path}'.")

    strategy = questionary.select(
        "How would you like to generate the new problem?",
        choices=[
            "Random Topic (from a curated list of topics)",
            "Specific Topics (you provide the topics)",
            "Your Own Idea (describe your concept in a text editor)",
        ],
        qmark="?",
        pointer="»"
    ).ask()

    if not strategy:
        raise KeyboardInterrupt

    topics, user_prompt, previous_problem = None, None, None

    if "Random Topic" in strategy:
        topics_path = Path(__file__).parent.parent.parent.parent / "topics.json"
        all_topics = json.loads(topics_path.read_text(encoding="utf-8"))
        all_topic_choices = []
        for top_level_value in all_topics.values():
            if isinstance(top_level_value, dict):
                for category_list in top_level_value.values():
                    all_topic_choices.extend(category_list)
            elif isinstance(top_level_value, list):
                all_topic_choices.extend(top_level_value)
        selected_topics = random.sample(all_topic_choices, k=random.randint(1, 2))
        topics = ", ".join(selected_topics)
        print(f"I've selected the following topics: '{topics}'")
        proceed = questionary.confirm("Shall I proceed with these topics?", default=True).ask()
        if not proceed:
            raise KeyboardInterrupt

    elif "Specific Topics" in strategy:
        topics = questionary.text("Please enter the topics, separated by commas:").ask()

    elif "Your Own Idea" in strategy:
        user_prompt = _get_user_feedback_from_editor()
        if not user_prompt:
            print("No idea provided. Aborting.")
            raise KeyboardInterrupt

    return {
        "strategy": strategy,
        "topics": topics,
        "user_prompt": user_prompt,
        "previous_problem": previous_problem,
    }

def generation_node(state: NovelProblemState) -> dict:
    """Generates the first draft of the problem statement."""
    print("--- Generating initial problem statement ---")
    prompt_path = Path(__file__).parent / "prompts/generate_problem.txt"
    prompt = ChatPromptTemplate.from_template(prompt_path.read_text(encoding="utf-8"))
    chain = prompt | get_llm_client()
    
    response = chain.invoke({
        "topics": state.get("topics") or "None",
        "previous_problem": state.get("previous_problem") or "None",
        "user_prompt": state.get("user_prompt") or "None",
    })
    
    return {"problem_statement": response.content}

def interactive_feedback_node(state: NovelProblemState) -> dict:
    """Saves the current problem and opens a text editor for user feedback."""
    print("\n" + "="*60)
    print("--- Pausing for Your Feedback ---")
    
    problem_path = Path(state['output_dir']) / "problem_statement.md"
    problem_path.write_text(state['problem_statement'], encoding="utf-8")
    print(f"The latest version of the problem has been saved to:\n{problem_path.resolve()}")

    human_feedback = _get_user_feedback_from_editor()
    
    if human_feedback:
        print("--- Feedback received. Preparing to refine problem statement. ---")
    else:
        print("--- No feedback provided. Problem statement accepted. ---")
    print("="*60 + "\n")

    return {"human_feedback": human_feedback}

def refinement_node(state: NovelProblemState) -> dict:
    """Refines the problem statement based on human feedback."""
    print("--- Refining problem statement based on your feedback ---")
    prompt_path = Path(__file__).parent / "prompts/refine_problem.txt"
    prompt = ChatPromptTemplate.from_template(prompt_path.read_text(encoding="utf-8"))
    chain = prompt | get_llm_client()
    
    response = chain.invoke({
        "problem_statement": state["problem_statement"],
        "human_feedback": state["human_feedback"],
    })
    
    return {"problem_statement": response.content}

def generate_examples_node(state: NovelProblemState) -> dict:
    """Generates example test cases for the final problem statement."""
    print("--- Generating example test cases ---")
    prompt_path = Path(__file__).parent / "prompts/generate_examples.txt"
    prompt = ChatPromptTemplate.from_template(prompt_path.read_text(encoding="utf-8"))
    chain = prompt | get_llm_client()
    
    response = chain.invoke({"problem_statement": state["problem_statement"]})
    
    test_cases = _parse_test_cases(response.content)
    print(f"Generated {len(test_cases)} example test cases.")
    return {"test_cases": test_cases}

def final_save_node(state: NovelProblemState) -> dict:
    """Saves the final generated examples to the output directory."""
    print("--- Saving final example test cases ---")
    test_cases_dir = Path(state['output_dir']) / "test_cases"
    test_cases_dir.mkdir(exist_ok=True)
    
    for f in test_cases_dir.glob("example_*"):
        f.unlink()
        
    for i, (input_data, output_data) in enumerate(state["test_cases"], 1):
        (test_cases_dir / f"example_{i}.in").write_text(input_data, encoding="utf-8")
        (test_cases_dir / f"example_{i}.out").write_text(output_data, encoding="utf-8")
        
    print(f"Saved {len(state['test_cases'])} examples to {test_cases_dir}")
    return {}