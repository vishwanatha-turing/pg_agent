import docker
import os
import re
from pathlib import Path

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

def _run_container(image_tag: str, command: list, work_dir: Path) -> (int, str):
    """A simplified and robust function to run a command in a container."""
    client = docker.from_env()
    container = None
    try:
        volumes = {str(work_dir.resolve()): {'bind': '/usr/src/app', 'mode': 'rw'}}
        
        container = client.containers.run(
            image=image_tag,
            command=command,
            volumes=volumes,
            working_dir='/usr/src/app',
            mem_limit="512m",
            cpu_shares=1024,
            detach=True,
        )
        result = container.wait()
        output = container.logs().decode('utf-8')
        return result['StatusCode'], output
    finally:
        if container:
            try:
                container.remove(force=True)
            except docker.errors.NotFound:
                pass

def generate_test_case_batches(test_generator_code: str, num_batches: int, output_dir: Path) -> Path:
    """Writes generator code and a corrected runner script to the output dir, then runs it."""
    image_tag = "cpp-validator-sandbox"
    client = docker.from_env()
    _build_image_if_not_exists(client, image_tag)
    
    (output_dir / "testcaseGenerator.cpp").write_text(test_generator_code)
    
    # --- THIS IS THE CRUCIAL FIX ---
    # Read the runner script, fix line endings in memory, then write it.
    sandbox_dir = Path(__file__).parent
    runner_sh_content = (sandbox_dir / "runner.sh").read_text()
    corrected_runner_content = runner_sh_content.replace('\r\n', '\n')
    runner_sh_path_in_temp = output_dir / "runner.sh"
    runner_sh_path_in_temp.write_text(corrected_runner_content, newline='\n')
    # --- END OF FIX ---
    
    os.chmod(runner_sh_path_in_temp, 0o755)

    for i in range(1, num_batches + 1):
        print(f"Generating test case batch #{i}...")
        command = ["/bin/bash", "runner.sh", "generate", str(i)]
        
        status_code, output = _run_container(image_tag, command, work_dir=output_dir)
        if status_code != 0:
            raise Exception(f"Failed to generate test case batch #{i}:\n{output}")
    
    return output_dir

def run_solution_against_tests(solution_code: str, bruteforce_code: str, test_cases_dir: Path) -> dict:
    """Writes solution code and a corrected runner script to the test dir, then runs it."""
    image_tag = "cpp-validator-sandbox"
    client = docker.from_env()
    _build_image_if_not_exists(client, image_tag)
    
    (test_cases_dir / "suspectedSolution.cpp").write_text(solution_code)
    (test_cases_dir / "bruteforce.cpp").write_text(bruteforce_code)
    
    # --- THIS IS THE CRUCIAL FIX ---
    # Read the runner script, fix line endings in memory, then write it.
    sandbox_dir = Path(__file__).parent
    runner_sh_content = (sandbox_dir / "runner.sh").read_text()
    corrected_runner_content = runner_sh_content.replace('\r\n', '\n')
    runner_sh_path_in_temp = test_cases_dir / "runner.sh"
    runner_sh_path_in_temp.write_text(corrected_runner_content, newline='\n')
    # --- END OF FIX ---
    
    os.chmod(runner_sh_path_in_temp, 0o755)

    command = ["/bin/bash", "runner.sh", "execute"]
    status_code, output = _run_container(image_tag, command, work_dir=test_cases_dir)

    if status_code != 0:
        return {"passed": 0, "failed": 1, "details": output}

    passed_match = re.search(r"PASSED: (\d+)", output)
    failed_match = re.search(r"FAILED: (\d+)", output)
    
    return {
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else 0,
        "details": output
    }