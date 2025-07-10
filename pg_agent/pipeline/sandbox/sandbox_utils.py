import docker
import os
import re
from pathlib import Path
import tempfile
import shutil
import subprocess

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
    """
    A robust function to run a command in a container using the Docker CLI via subprocess.
    This is more reliable for stdin handling on Windows.
    Returns (exit_code, stdout, stderr).
    """
    client = docker.from_env()
    _build_image_if_not_exists(client, image_tag)

    # Resolve the absolute path for the volume mount
    abs_work_dir = str(work_dir.resolve())
    
    # Construct the full Docker CLI command
    docker_command = [
        "docker", "run",
        "--rm",  # Automatically remove the container when it exits
        "-i",    # Keep STDIN open even if not attached (-i for interactive)
        "-w", "/usr/src/app", # Set the working directory
        "-v", f"{abs_work_dir}:/usr/src/app", # Mount the working directory
        "--memory=512m",
        "--cpu-shares=1024",
        image_tag,
        "/bin/bash", "-c", command # The command to execute inside the container
    ]
    
    # Run the command using subprocess
    process = subprocess.run(
        docker_command,
        input=input_data,
        capture_output=True,
        timeout=30 # Add a generous 30-second timeout to prevent infinite hangs
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

def run_validator_script(validator_path: str, input_file: Path) -> (bool, str):
    """Runs a validator script against a single input file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        work_dir = Path(temp_dir)
        shutil.copy(validator_path, work_dir / "validator.cpp")
        
        command = "g++ -std=c++14 -O2 -o validator validator.cpp && ./validator"
        
        input_data = input_file.read_bytes()
        status_code, stdout, stderr = _run_command_in_container("cpp-validator-sandbox", command, work_dir, input_data=input_data)
        
        # A validator is successful if it exits with 0. Stderr contains the reason for failure.
        return status_code == 0, stderr

def run_solution_on_test_case(solution_path: str, input_file: Path, time_limit: float) -> (bool, str):
    """Runs a solution against an input file with a timeout. Returns (timed_out, output)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        work_dir = Path(temp_dir)
        shutil.copy(solution_path, work_dir / "solution.cpp")
        
        # Using linux 'timeout' command inside the container
        command = f"g++ -std=c++14 -O2 -o solution solution.cpp && timeout {time_limit} ./solution"
        
        input_data = input_file.read_bytes()
        status_code, stdout, stderr = _run_command_in_container("cpp-validator-sandbox", command, work_dir, input_data=input_data)
        
        timed_out = status_code == 124
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
