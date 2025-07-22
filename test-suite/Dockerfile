# Use Node.js base (we know this works) and add boto3
FROM public.ecr.aws/docker/library/node:20-slim

# Install system dependencies including python
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    zip \
    unzip \
    jq \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install Python packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir boto3 requests

# Install pnpm globally (this will work since we have Node.js)
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Copy test-suite
COPY . /workspace/test-suite/

# Make scripts executable  
RUN chmod +x /workspace/test-suite/scripts/build-and-zip.sh

# Install Node.js dependencies
RUN cd /workspace/test-suite && rm -rf node_modules && pnpm install --frozen-lockfile

WORKDIR /workspace/test-suite