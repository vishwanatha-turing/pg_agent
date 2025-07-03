# Use a standard GCC image which has all the build tools we need.
FROM gcc:11.2.0

# Install sed, a tool for text manipulation, just in case it's not in the base image.
# Then clean up the apt cache to keep the image small.
RUN apt-get update && apt-get install -y sed && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the runner script into the container.
COPY runner.sh .

# --- FIX THE LINE ENDINGS ---
# This command finds and removes the invisible Windows '\r' characters from the script.
# This makes the script compatible with the Linux environment inside the container.
RUN sed -i 's/\r$//' runner.sh

# Make the script executable.
RUN chmod +x runner.sh

# Set the entrypoint. When the container starts, it will run this script.
ENTRYPOINT ["./runner.sh"]