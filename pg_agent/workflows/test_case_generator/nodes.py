import os
import re
import json
from pathlib import Path
import questionary
import subprocess
import tempfile
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .schemas import TestCaseGeneratorState

def _open_in_editor(file_path: Path):
    """Opens a file in the default text editor."""
    editor = os.environ.get('EDITOR', 'notepad' if os.name == 'nt' else 'vim')
    print(f"Opening {file_path.name} with '{editor}' for your review...")
    # Use shell=True for Windows compatibility with paths that might have spaces
    subprocess.run(f'"{editor}" "{file_path}"', shell=True, check=True)

def _extract_cpp_code(response_content: str) -> str:
    """Parses the LLM's response to extract only the C++ code."""
    match = re.search(r'```(?:cpp)?\s*([\s\S]+?)\s*```', response_content)
    if match: return match.group(1).strip()
    return response_content.strip()

def get_llm_client():
    """Creates an OpenAI client, reading the key from the environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: raise ValueError("OPENAI_API_KEY not found in environment.")
    return ChatOpenAI(model="o4-mini", api_key=api_key, max_tokens=8192)

def load_context_node(state: TestCaseGeneratorState) -> dict:
    """Loads the problem statement and latest bruteforce solution."""
    print(f"--- Loading context from: {state['problem_dir_path']}/automation ---")
    problem_dir = Path(state['problem_dir_path'])
    automation_dir = problem_dir / "automation"
    settings_path = automation_dir / "automation_settings.json"

    if not settings_path.exists():
        raise FileNotFoundError("automation_settings.json not found. Please run 'create_brute_force' workflow first.")

    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    bf_version = settings.get("bruteforceSolutionVersion", -1)
    
    if bf_version == -1:
        raise FileNotFoundError("Bruteforce solution not found. Please run 'create_brute_force' workflow first.")

    problem_statement = (problem_dir / "problem_statement.md").read_text(encoding="utf-8")
    bruteforce_path = automation_dir / "bruteForceSol" / f"bruteforceSolution_v{bf_version}.cpp"
    bruteforce_code = bruteforce_path.read_text(encoding="utf-8")
    
    print("Loaded problem statement and latest bruteforce solution.")
    return {"problem_statement": problem_statement, "bruteforce_code": bruteforce_code}

def _create_generation_node(prompt_file_name: str, output_key: str, version_key: str):
    """A factory to create a node that generates, allows optional review, and saves a C++ script."""
    def generation_node(state: TestCaseGeneratorState) -> dict:
        print(f"--- Generating: {output_key} ---")
        
        prompt_path = Path(__file__).parent / "prompts" / prompt_file_name
        prompt = ChatPromptTemplate.from_template(prompt_path.read_text(encoding="utf-8"))
        chain = prompt | get_llm_client()
        
        response = chain.invoke({
            "problem_statement": state["problem_statement"],
            "bruteforce_code": state["bruteforce_code"]
        })
        
        code = _extract_cpp_code(response.content)
        
        print("\n" + "="*60)
        wants_to_review = questionary.confirm(
            f"The '{version_key.replace('Version', '')}' script has been generated. Would you like to review or edit it?",
            default=False,
            qmark="?"
        ).ask()
        
        if wants_to_review:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".cpp", encoding="utf-8") as tf:
                temp_code_path = Path(tf.name)
                tf.write(code)
            
            _open_in_editor(temp_code_path)
            
            code = temp_code_path.read_text(encoding="utf-8")
            os.unlink(temp_code_path)
            print("--- Script updated with your changes. ---")
        else:
            print("--- Skipping review. Proceeding with AI-generated script. ---")
        print("="*60)

        automation_dir = Path(state['problem_dir_path']) / "automation"
        settings_path = automation_dir / "automation_settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        
        new_version = settings.get(version_key, -1) + 1
        
        script_dir = automation_dir / "testcaseGenScript"
        script_dir.mkdir(parents=True, exist_ok=True)
        
        file_prefix = version_key.replace("Version", "")
        final_path = script_dir / f"{file_prefix}_v{new_version}.cpp"
        final_path.write_text(code, encoding="utf-8")
        
        settings[version_key] = new_version
        settings_path.write_text(json.dumps(settings, indent=4), encoding="utf-8")
        
        print(f"Saved new version {new_version} to: {final_path}")
        return {output_key: str(final_path)}

    return generation_node

# --- THIS IS THE CRUCIAL FIX ---
# The calls to the factory function now include all required arguments.
gen_small_tests_node = _create_generation_node(
    "gen_small_tests.txt", "small_test_gen_path", "smallTestcaseGeneratorVersion"
)
gen_stress_tests_node = _create_generation_node(
    "gen_stress_tests.txt", "stress_test_gen_path", "stressTestcaseGeneratorVersion"
)
gen_validator_node = _create_generation_node(
    "gen_validator.txt", "validator_path", "testcaseValidatorVersion"
)