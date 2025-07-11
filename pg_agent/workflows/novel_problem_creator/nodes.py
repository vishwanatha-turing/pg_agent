import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .schemas import NovelProblemState

def get_llm_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: raise ValueError("OPENAI_API_KEY not found in environment.")
    return ChatOpenAI(model="gpt-4o-mini", api_key=api_key, max_tokens=8192)

def _parse_test_cases(response: str) -> list[tuple[str, str]]:
    """Parses the LLM response using XML-like tags to find test cases."""
    test_cases = []
    # Use a non-greedy regex to find all <test_case> blocks
    for match in re.finditer(r'<test_case>(.*?)</test_case>', response, re.DOTALL):
        block = match.group(1)
        # Extract input and output from within the block
        input_match = re.search(r'<input>(.*?)</input>', block, re.DOTALL)
        output_match = re.search(r'<output>(.*?)</output>', block, re.DOTALL)
        if input_match and output_match:
            test_cases.append((input_match.group(1).strip(), output_match.group(1).strip()))
    return test_cases

# --- Node Definitions ---

def setup_node(state: NovelProblemState) -> dict:
    """Copies the repo_template and loads any context from a previous problem."""
    print(f"--- Setting up output directory: {state['output_dir']} ---")
    output_path = Path(state['output_dir'])
    
    # Use an absolute path for the template to be safe
    template_path = Path(__file__).parent.parent.parent.parent / "repo_template"
    if not template_path.exists():
        raise FileNotFoundError(f"Template directory not found at: {template_path}")

    # Copy template to output directory
    if output_path.exists():
        print(f"Directory '{output_path}' already exists. Overwriting is not supported.")
    else:
        shutil.copytree(template_path, output_path)
        print(f"Copied template to '{output_path}'.")

    previous_problem = None
    if state.get("context_dir"):
        context_path = Path(state["context_dir"]) / "problem_statement.md"
        if context_path.exists():
            previous_problem = context_path.read_text(encoding="utf-8")
            print(f"Loaded context from: {context_path}")
        else:
            print(f"Warning: Context directory provided, but no problem_statement.md found in {state['context_dir']}")

    return {"previous_problem": previous_problem}

def initial_generation_node(state: NovelProblemState) -> dict:
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
    
    # Save the current version for the user to review
    problem_path = Path(state['output_dir']) / "problem_statement.md"
    problem_path.write_text(state['problem_statement'], encoding="utf-8")
    print(f"The latest version of the problem has been saved to:\n{problem_path.resolve()}")

    # Create a temporary file for feedback
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt", encoding="utf-8") as tf:
        feedback_file_path = tf.name
        tf.write("# Please enter your feedback below. Save and close this file to continue.\n")
        tf.write("# To accept the current version and generate test cases, save and close this file without adding any other text.\n")
    
    # Determine the default editor
    editor = os.environ.get('EDITOR', 'notepad' if os.name == 'nt' else 'vim')
    print(f"Opening feedback file with '{editor}'...")
    
    try:
        # Open the editor and wait for the user to close it
        subprocess.run([editor, feedback_file_path], check=True)
    except Exception as e:
        print(f"\nError opening editor: {e}")
        print("Please manually open the feedback file, add your notes, save, and close it.")
        print(f"Feedback file path: {feedback_file_path}")
        input("Press Enter to continue after you have saved and closed the file...")

    # Read the feedback from the file
    feedback_content = Path(feedback_file_path).read_text(encoding="utf-8")
    
    # Clean the default instructional text
    lines = [line for line in feedback_content.splitlines() if not line.strip().startswith('#')]
    human_feedback = "\n".join(lines).strip()
    
    # Clean up the temporary file
    os.unlink(feedback_file_path)
    
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
    
    # Overwrite the old problem statement with the refined version
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
    
    # Clear any existing example files first
    for f in test_cases_dir.glob("example_*"):
        f.unlink()
        
    for i, (input_data, output_data) in enumerate(state["test_cases"], 1):
        (test_cases_dir / f"example_{i}.in").write_text(input_data, encoding="utf-8")
        (test_cases_dir / f"example_{i}.out").write_text(output_data, encoding="utf-8")
        
    print(f"Saved {len(state['test_cases'])} examples to {test_cases_dir}")
    return {}
