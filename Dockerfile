# Use the same base image as CodeBuild Standard 7.0
FROM public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:5.0

# Set working directory
WORKDIR /workspace

# Copy the entire repository structure (. means current directory which is repo root)
COPY . /workspace/

# Make scripts executable
RUN chmod +x /workspace/test-suite/scripts/build-and-zip.sh

# The CodeBuild base image already has the right user setup
# No need to manually chown or switch users - CodeBuild handles this

# Set the default working directory
WORKDIR /workspace