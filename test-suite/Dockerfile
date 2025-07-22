# Use Node.js from Amazon ECR Public (no rate limits)
FROM public.ecr.aws/docker/library/node:20-slim

# Update package list and install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    build-essential \
    zip \
    unzip \
    jq \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages needed for Device Farm integration
RUN pip3 install --no-cache-dir requests boto3

# Install pnpm globally
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Copy test-suite to /workspace/test-suite (since Docker context is test-suite/)
# This will include handler.py if it's in the test-suite directory
COPY . /workspace/test-suite/

# Make scripts executable
RUN chmod +x /workspace/test-suite/scripts/build-and-zip.sh

# Install Node.js dependencies for test-suite using pnpm (force clean install)
RUN cd /workspace/test-suite && rm -rf node_modules && pnpm install --frozen-lockfile

# Set the default working directory to test-suite
WORKDIR /workspace/test-suite