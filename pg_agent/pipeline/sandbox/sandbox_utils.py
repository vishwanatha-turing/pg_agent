import docker
import tempfile
import os
import re

def run_docker_sandbox(solution_code: str, test_generator_code: str, bruteforce_solution_code: str) -> dict:
    """
    Builds a Docker image, runs the C++ test pipeline, and returns the results.
    """
    client = docker.from_env()
    image_tag = "cpp-validator-sandbox"
    
    # --- 1. Define paths ---
    sandbox_dir = os.path.dirname(__file__)
    dockerfile_path = os.path.join(sandbox_dir)

    # --- 2. Create a temporary directory for the build context ---
    with tempfile.TemporaryDirectory() as build_context:
        # Write the C++ code to files within the build context
        with open(os.path.join(build_context, "suspectedSolution.cpp"), "w") as f:
            f.write(solution_code)
        with open(os.path.join(build_context, "testcaseGenerator.cpp"), "w") as f:
            f.write(test_generator_code)
        with open(os.path.join(build_context, "bruteforce.cpp"), "w") as f:
            f.write(bruteforce_solution_code)
        
        # Copy Dockerfile and runner.sh into the context
        os.system(f"cp {os.path.join(sandbox_dir, 'Dockerfile')} {build_context}")
        os.system(f"cp {os.path.join(sandbox_dir, 'runner.sh')} {build_context}")

        # --- 3. Build the Docker image ---
        print(f"Building Docker image '{image_tag}'...")
        try:
            client.images.build(path=build_context, tag=image_tag, rm=True)
        except docker.errors.BuildError as e:
            print("Docker build failed!")
            return {"passed": 0, "failed": 1, "details": f"Docker build error: {e}"}

        # --- 4. Run the container ---
        print("Running container...")
        try:
            container = client.containers.run(
                image=image_tag,
                detach=False,  # Run in foreground and wait for completion
                remove=True,   # Automatically remove container on exit
                mem_limit="256m", # Memory limit
                cpu_shares=1024,  # CPU shares (relative weight)
            )
            # The output is returned as bytes
            output = container.decode('utf-8')
            exit_code = 0 # If it completes, it means success
        except docker.errors.ContainerError as e:
            # This is expected for test failures, as runner.sh exits with 1
            output = e.container.logs().decode('utf-8')
            exit_code = e.exit_status
        except Exception as e:
            print(f"An unexpected error occurred while running the container: {e}")
            return {"passed": 0, "failed": 1, "details": f"Container runtime error: {e}"}

    # --- 5. Parse the output from the container ---
    passed_match = re.search(r"PASSED: (\d+)", output)
    failed_match = re.search(r"FAILED: (\d+)", output)
    passed_count = int(passed_match.group(1)) if passed_match else 0
    failed_count = int(failed_match.group(1)) if failed_match else 0
    
    return {
        "passed": passed_count,
        "failed": failed_count,
        "details": output
    }
