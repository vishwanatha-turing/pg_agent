import docker
import os
import re
from pathlib import Path
import tempfile
import shutil
import subprocess
from typing import List, Dict, Tuple

def _build_image_if_not_exists(client: docker.DockerClient, image_tag: str):
    """Checks if the image exists locally and builds it if it doesn't."""
    try:
        client.images.get(image_tag)
    except docker.errors.ImageNotFound:
        print(f"Docker image '{image_tag}' not found. Building...")
        sandbox_dir = Path(__file__).parent
        try:
            client.images.build(path=str(sandbox_dir), tag=image_tag, rm=True)
            print("Build successful.")
        except docker.errors.BuildError as e:
            print(f"FATAL: Docker build failed: {e}")
            raise

def _run_command_in_container(image_tag: str, command: str, work_dir: Path, input_data: bytes = None) -> (int, str, str):
    """A robust function to run a command in a container using the Docker CLI via subprocess."""
    client = docker.from_env()
    _build_image_if_not_exists(client, image_tag)
    abs_work_dir = str(work_dir.resolve())
    docker_command = [
        "docker", "run", "--rm", "-i", "-w", "/usr/src/app",
        "-v", f"{abs_work_dir}:/usr/src/app",
        "--memory=512m", "--cpu-shares=1024",
        image_tag, "/bin/bash", "-c", command
    ]
    process = subprocess.run(
        docker_command, input=input_data,
        capture_output=True, timeout=120
    )
    stdout = process.stdout.decode('utf-8', errors='ignore')
    stderr = process.stderr.decode('utf-8', errors='ignore')
    return process.returncode, stdout, stderr

def run_generator_script(script_path: str, output_dir: Path):
    """Compiles and runs a generator script inside the mounted output_dir."""
    work_dir = output_dir
    work_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(script_path, work_dir / "generator.cpp")
    command = "g++ -std=c++14 -O2 -o generator generator.cpp && ./generator"
    status_code, stdout, stderr = _run_command_in_container("cpp-validator-sandbox", command, work_dir)
    if status_code != 0:
        raise Exception(f"Generator script failed:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")

def run_validation_suite(validator_path: str, all_input_files: List[Path]) -> Tuple[List[Path], List[Dict[str, str]]]:
    """Validates a whole directory of .in files in a single container run."""
    with tempfile.TemporaryDirectory() as temp_dir:
        work_dir = Path(temp_dir)
        shutil.copy(validator_path, work_dir / "validator.cpp")
        for in_file in all_input_files:
            shutil.copy(in_file, work_dir / in_file.name)
        
        runner_sh_content = (Path(__file__).parent / "runner.sh").read_text().replace('\r\n', '\n')
        (work_dir / "runner.sh").write_text(runner_sh_content, newline='\n')
        os.chmod(work_dir / "runner.sh", 0o755)

        command = "/bin/bash runner.sh validate_suite"
        status_code, stdout, stderr = _run_command_in_container("cpp-validator-sandbox", command, work_dir)
        
        if status_code != 0:
            raise Exception(f"Validation suite execution failed:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
            
        valid_files, invalid_files = [], []
        original_paths = {p.name: p for p in all_input_files}
        for line in stdout.splitlines():
            if line.startswith("VALID:"):
                filename = line.split(":", 1)[1].strip()
                if filename in original_paths:
                    valid_files.append(original_paths[filename])
            elif line.startswith("INVALID:"):
                parts = line.split(" REASON: ", 1)
                filename = parts[0].split(":", 1)[1].strip()
                reason = parts[1].strip() if len(parts) > 1 else "Unknown validation error"
                invalid_files.append({"file": filename, "reason": reason})
                
        return valid_files, invalid_files

def run_test_suite(solution_path: str, test_cases_dir: Path, time_limit: float):
    """
    Runs a single solution against a directory of test cases efficiently.
    Compiles once, then runs all tests in a single container.
    """
    image_tag = "cpp-validator-sandbox"
    work_dir = test_cases_dir
    
    shutil.copy(solution_path, work_dir / "solution.cpp")
    runner_sh_content = (Path(__file__).parent / "runner.sh").read_text().replace('\r\n', '\n')
    (work_dir / "runner.sh").write_text(runner_sh_content, newline='\n')
    os.chmod(work_dir / "runner.sh", 0o755)

    command = f"/bin/bash runner.sh execute_suite {time_limit} solution.cpp solution_executable"
    status_code, stdout, stderr = _run_command_in_container(image_tag, command, work_dir=work_dir)
    
    if status_code != 0:
        raise Exception(f"Test suite execution failed:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
    
    print(stdout) # Print the output for debugging

def run_solution_on_test_case(solution_path: str, input_file: Path, time_limit: float) -> (bool, str):
    """Runs a solution against an input file with a timeout. Returns (timed_out, output)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        work_dir = Path(temp_dir)
        shutil.copy(solution_path, work_dir / "solution.cpp")
        command = f"g++ -std=c++14 -O2 -o solution solution.cpp && timeout {time_limit} ./solution"
        input_data = input_file.read_bytes()
        status_code, stdout, stderr = _run_command_in_container("cpp-validator-sandbox", command, work_dir, input_data=input_data)
        timed_out = status_code == 124
        if status_code not in [0, 124]:
            print(f"Solution run failed with stderr:\n{stderr}")
        return timed_out, stdout

def run_single_test(solution_code: str, input_data: str) -> (bool, str):
    """Runs a single piece of code (as a string) against a single input string."""
    with tempfile.TemporaryDirectory() as temp_dir:
        work_dir = Path(temp_dir)
        (work_dir / "solution.cpp").write_text(solution_code)
        command = "g++ -std=c++14 -O2 -o solution solution.cpp && ./solution"
        status_code, stdout, stderr = _run_command_in_container("cpp-validator-sandbox", command, work_dir, input_data=input_data.encode('utf-8'))
        if status_code != 0:
            print(f"run_single_test failed with stderr:\n{stderr}")
        return status_code == 0, stdout
