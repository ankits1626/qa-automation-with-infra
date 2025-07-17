from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct
import os

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create buildspec that prints the required information and runs test suite
        buildspec = codebuild.BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "pre_build": {
                    "commands": [
                        "echo 'Execution started'",
                        f"echo 'Android Device Farm Project ARN: {android_project_arn}'",
                        f"echo 'iOS Device Farm Project ARN: {ios_project_arn}'",
                        "echo 'Current working directory:' $(pwd)",
                        "echo 'Available directories:'",
                        "ls -la /workspace/",
                        "echo 'Test suite directory contents:'",
                        "ls -la /workspace/test-suite/ || echo 'test-suite directory not found'"
                    ]
                },
                "build": {
                    "commands": [
                        "echo 'Building test suite'",
                        "cd /workspace/test-suite",
                        "./scripts/build-and-zip.sh",
                        "echo 'Test suite build completed'",
                        "ls -la system_tests.zip || echo 'system_tests.zip not found'"
                    ]
                }
            }
        })

        # Create CodeBuild project with custom image
        self.project = codebuild.Project(
            self, "SystemTestsBuildProject",
            project_name="system-tests-build-project",
            build_spec=buildspec,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_asset(
                    self, "CustomBuildImage",
                    # Dockerfile is now in infrastructure directory
                    directory=os.path.join(os.path.dirname(__file__), "demo_image")
                ),
                compute_type=codebuild.ComputeType.SMALL,
                privileged=True  # Enable privileged mode for Docker operations
            )
        )

        # Add IAM permissions for Device Farm operations
        self.project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "devicefarm:ListProjects",
                    "devicefarm:CreateUpload", 
                    "devicefarm:GetUpload",
                    "devicefarm:ScheduleRun",
                    "devicefarm:GetRun",
                    "devicefarm:ListRuns",
                    "devicefarm:ListDevicePools"
                ],
                resources=["*"]
            )
        )