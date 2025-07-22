# Alternative: Use AWS Lambda Python base image (has boto3 pre-installed)
FROM public.ecr.aws/lambda/python:3.11

# Install Node.js and other system dependencies
RUN yum update -y && yum install -y \
    nodejs npm \
    git \
    zip \
    unzip \
    jq \
    && yum clean all

# Install pnpm
RUN npm install -g pnpm

# Install additional Python packages (boto3 already included)
RUN pip install --no-cache-dir requests

# Set working directory
WORKDIR /workspace

# Copy test-suite
COPY . /workspace/test-suite/

# Make scripts executable  
RUN chmod +x /workspace/test-suite/scripts/build-and-zip.sh

# Install Node.js dependencies
RUN cd /workspace/test-suite && rm -rf node_modules && pnpm install --frozen-lockfile

WORKDIR /workspace/test-suite