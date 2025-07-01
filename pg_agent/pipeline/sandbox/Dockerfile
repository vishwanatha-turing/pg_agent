# Use a standard GCC image which has all the build tools we need.
# This simplifies the setup significantly.
FROM gcc:11.2.0

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the runner script into the container and make it executable.
# This is the ONLY file we bake into the image.
COPY runner.sh .
RUN chmod +x runner.sh

# Set the entrypoint. When the container starts, it will run this script.
ENTRYPOINT ["./runner.sh"]