# Use the same base image as CodeBuild Standard 7.0
FROM public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:5.0

# Set working directory
WORKDIR /workspace

# Copy the entire repository structure (. means current directory which is repo root)
COPY . /workspace/

# Make scripts executable
RUN chmod +x /workspace/test-suite/scripts/build-and-zip.sh

# Set proper ownership (CodeBuild runs as codebuild user)
RUN chown -R codebuild:codebuild /workspace

# Switch to codebuild user
USER codebuild

# Set the default working directory
WORKDIR /workspace