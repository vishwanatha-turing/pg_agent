import docker
import tempfile
import os
import re
import tarfile
import io
from pathlib import Path

def _copy_to_container(container, src, dst):
    """Helper to copy files into a container."""
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        tar.add(src, arcname=os.path.basename(dst))
    tar_stream.seek(0)
    container.put_archive(path=os.path.dirname(dst), data=tar_stream)

def _run_container(image_tag: str, command: list, files_to_copy: dict, directories_to_copy: dict = None) -> (int, str):
    """A generic function to create, run, and clean up a container."""
    client = docker.from_env()
    container = None
    try:
        container = client.containers.create(
            image=image_tag,
            command=command,
            mem_limit="512m",
            cpu_shares=1024,
        )
        # Copy necessary files and directories
        for src, dst in files_to_copy.items():
            _copy_to_container(container, src, dst)
        if directories_to_copy:
            for src_dir, dst_dir in directories_to_copy.items():
                # Create a tar of the directory to copy it
                tar_stream = io.BytesIO()
                with tarfile.open(fileobj=tar_stream, mode='w:gz') as tar:
                    tar.add(src_dir, arcname='.')
                tar_stream.seek(0)
                container.put_archive(path=dst_dir, data=tar_stream)

        container.start()
        result = container.wait()
        output = container.logs().decode('utf-8')
        return result['StatusCode'], output
    finally:
        if container:
            container.remove(force=True)

def generate_test_case_batches(test_generator_code: str, num_batches: int) -> Path:
    """
    Runs the test case generator in Docker to create multiple batches of test files.
    Returns the path to the temporary directory containing all generated test batches.
    """
    client = docker.from_env()
    image_tag = "cpp-validator-sandbox"
    
    # Build image if it doesn't exist
    try:
        client.images.get(image_tag)
    except docker.errors.ImageNotFound:
        print(f"Building Docker image '{image_tag}'...")
        sandbox_dir = Path(__file__).parent
        client.images.build(path=str(sandbox_dir), tag=image_tag, rm=True)

    # Use a single temp directory to hold all generated test case folders
    # This directory will be deleted automatically when the 'with' block exits
    # We need to manage its lifecycle outside this function.
    test_cases_root_dir = Path(tempfile.mkdtemp())
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as gen_f:
        gen_f.write(test_generator_code)
        generator_src_path = gen_f.name

    for i in range(1, num_batches + 1):
        print(f"Generating test case batch #{i}...")
        command = ["./runner.sh", "generate", str(i)]
        files_to_copy = {generator_src_path: "/usr/src/app/testcaseGenerator.cpp"}
        
        status_code, output = _run_container(image_tag, command, files_to_copy)
        if status_code != 0:
            raise Exception(f"Failed to generate test case batch #{i}: {output}")

    os.remove(generator_src_path)
    return test_cases_root_dir

def run_solution_against_tests(solution_code: str, bruteforce_code: str, test_cases_dir: Path) -> dict:
    """
    Runs the solution and bruteforce code against all pre-generated test cases.
    """
    image_tag = "cpp-validator-sandbox"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        solution_path = Path(temp_dir) / "suspectedSolution.cpp"
        solution_path.write_text(solution_code)
        
        bruteforce_path = Path(temp_dir) / "bruteforce.cpp"
        bruteforce_path.write_text(bruteforce_code)

        command = ["./runner.sh", "execute"]
        files_to_copy = {
            str(solution_path): "/usr/src/app/suspectedSolution.cpp",
            str(bruteforce_path): "/usr/src/app/bruteforce.cpp",
        }
        # Copy the entire directory of generated test cases
        dirs_to_copy = {str(test_cases_dir): "/usr/src/app/testcases"}

        status_code, output = _run_container(image_tag, command, files_to_copy, dirs_to_copy)

    passed_match = re.search(r"PASSED: (\d+)", output)
    failed_match = re.search(r"FAILED: (\d+)", output)
    
    return {
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else 0,
        "details": output
    }