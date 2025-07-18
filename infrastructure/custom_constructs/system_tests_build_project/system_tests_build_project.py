from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct
import os

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create buildspec that references the external script
        buildspec = codebuild.BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "pre_build": {
                    "commands": [
                        "echo 'Execution started'",
                        f"echo 'Android Device Farm Project ARN: {android_project_arn}'",
                        f"echo 'iOS Device Farm Project ARN: {ios_project_arn}'",
                        "echo 'Current working directory:' $(pwd)",
                        "ls -la .",
                        "echo 'Available scripts:'",
                        "find . -name '*.sh' -type f"
                    ]
                },
                "build": {
                    "commands": [
                        "chmod +x ./custom_constructs/system_tests_build_project/scripts/device-farm-runner.sh",
                        f"./custom_constructs/system_tests_build_project/scripts/device-farm-runner.sh {android_project_arn} {ios_project_arn}"
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
                    # Point to test-suite directory where Dockerfile is located
                    directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "test-suite")
                ),
                compute_type=codebuild.ComputeType.SMALL,
                privileged=True  # Enable privileged mode for Docker operations
            )
        )

        # Add comprehensive IAM permissions for Device Farm and S3 operations
        self.project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    # Device Farm permissions
                    "devicefarm:ListProjects",
                    "devicefarm:CreateUpload", 
                    "devicefarm:GetUpload",
                    "devicefarm:ScheduleRun",
                    "devicefarm:GetRun",
                    "devicefarm:ListRuns",
                    "devicefarm:ListDevicePools",
                    "devicefarm:GetDevicePool",
                    # S3 permissions for downloading app files
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                resources=["*"]
            )
        )