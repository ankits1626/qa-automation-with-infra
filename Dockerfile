# Use the same base image as CodeBuild Standard 7.0
FROM public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:5.0

# Set working directory
WORKDIR /workspace

# Copy the entire repository structure
COPY . /workspace/

# Install Node.js dependencies for test-suite (if needed upfront)
# We'll do this in buildspec for flexibility, but you can uncomment if you want it baked in
# RUN cd test-suite && npm install

# Make scripts executable
RUN chmod +x test-suite/scripts/build-and-zip.sh

# Install any additional system dependencies if needed
# RUN yum update -y && yum install -y <additional-packages>

# Set proper ownership (CodeBuild runs as codebuild user)
RUN chown -R codebuild:codebuild /workspace

# Switch to codebuild user
USER codebuild

# Set the default working directory
WORKDIR /workspace