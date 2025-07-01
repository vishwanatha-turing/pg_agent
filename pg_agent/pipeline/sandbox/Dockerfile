# Stage 1: Builder
# We use a full-featured base image to compile our C++ code.
FROM gcc:11.2.0 as builder

# Install build tools
RUN apt-get update && apt-get install -y build-essential

WORKDIR /usr/src/app

# Copy all source files into the container
COPY . .

# Compile all C++ programs
# We use C++14 standard and enable optimizations.
RUN g++ -std=c++14 -O2 -o testcaseGenerator testcaseGenerator.cpp
RUN g++ -std=c++14 -O2 -o bruteforce bruteforce.cpp
RUN g++ -std=c++14 -O2 -o suspectedSolution suspectedSolution.cpp

# Stage 2: Runner
# We use a minimal base image for the final container to reduce size.
FROM debian:bullseye-slim

# Install only necessary runtime libraries
RUN apt-get update && apt-get install -y libstdc++6 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy the compiled binaries from the builder stage
COPY --from=builder /usr/src/app/testcaseGenerator .
COPY --from=builder /usr/src/app/bruteforce .
COPY --from=builder /usr/src/app/suspectedSolution .

# Copy the runner script
COPY runner.sh .
RUN chmod +x runner.sh

# Set the entrypoint for the container
ENTRYPOINT ["./runner.sh"]
