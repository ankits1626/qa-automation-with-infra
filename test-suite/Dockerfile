# Use lightweight Ubuntu with Node.js
FROM node:20-slim

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

# Install AWS CLI v2 (more reliable than pip install)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# Install pnpm globally
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Copy the entire repository structure
COPY . /workspace/test-suite/

# Make scripts executable
RUN chmod +x /workspace/test-suite/scripts/build-and-zip.sh

# Install Node.js dependencies for test-suite using pnpm
RUN cd /workspace/test-suite && pnpm install

# Set the default working directory
WORKDIR /workspace/test-suite