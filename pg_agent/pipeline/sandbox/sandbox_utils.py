import docker
import tempfile
import os
import re
import tarfile
import io

# --- Helper function to copy files into a container ---
def copy_to_container(container, src, dst):
    """Copies files from a source on the host to a destination in the container."""
    # Create a tar archive in memory
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        tar.add(src, arcname=os.path.basename(dst))
    
    # Go to the beginning of the stream
    tar_stream.seek(0)
    container.put_archive(path=os.path.dirname(dst), data=tar_stream)


def run_docker_sandbox(solution_code: str, test_generator_code: str, bruteforce_solution_code: str) -> dict:
    """
    Builds a Docker image if needed, then runs the C++ test pipeline in a new container.
    """
    client = docker.from_env()
    image_tag = "cpp-validator-sandbox"
    
    # --- 1. Build the image only if it doesn't exist ---
    try:
        client.images.get(image_tag)
        print(f"Docker image '{image_tag}' already exists. Skipping build.")
    except docker.errors.ImageNotFound:
        print(f"Building Docker image '{image_tag}'...")
        sandbox_dir = os.path.dirname(__file__)
        try:
            client.images.build(path=sandbox_dir, tag=image_tag, rm=True)
        except docker.errors.BuildError as e:
            print("Docker build failed!")
            return {"passed": 0, "failed": 1, "details": f"Docker build error: {e}"}

    # --- 2. Create a temporary directory for the source files ---
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the C++ code to files
        solution_path = os.path.join(temp_dir, "suspectedSolution.cpp")
        test_gen_path = os.path.join(temp_dir, "testcaseGenerator.cpp")
        bruteforce_path = os.path.join(temp_dir, "bruteforce.cpp")

        with open(solution_path, "w") as f: f.write(solution_code)
        with open(test_gen_path, "w") as f: f.write(test_generator_code)
        with open(bruteforce_path, "w") as f: f.write(bruteforce_solution_code)

        # --- 3. Run the test in a new container ---
        container = None
        try:
            print("Creating and starting container...")
            # Create the container but don't start it yet
            container = client.containers.create(
                image=image_tag,
                mem_limit="256m",
                cpu_shares=1024,
            )
            
            # Copy source files into the container
            copy_to_container(container, solution_path, "/usr/src/app/suspectedSolution.cpp")
            copy_to_container(container, test_gen_path, "/usr/src/app/testcaseGenerator.cpp")
            copy_to_container(container, bruteforce_path, "/usr/src/app/bruteforce.cpp")

            # Start the container and wait for the runner.sh script to finish
            container.start()
            result = container.wait()
            output = container.logs().decode('utf-8')
            
            # Check the exit code from the container
            if result['StatusCode'] != 0:
                # This is our expected path for test failures
                print("Container exited with non-zero status (tests likely failed).")
            
        except Exception as e:
            print(f"An unexpected error occurred while running the container: {e}")
            return {"passed": 0, "failed": 1, "details": f"Container runtime error: {e}"}
        finally:
            # --- 4. Always clean up the container ---
            if container:
                print("Removing container...")
                container.remove()

    # --- 5. Parse the output from the container logs ---
    passed_match = re.search(r"PASSED: (\d+)", output)
    failed_match = re.search(r"FAILED: (\d+)", output)
    passed_count = int(passed_match.group(1)) if passed_match else 0
    failed_count = int(failed_match.group(1)) if failed_match else 0
    
    return {
        "passed": passed_count,
        "failed": failed_count,
        "details": output
    }