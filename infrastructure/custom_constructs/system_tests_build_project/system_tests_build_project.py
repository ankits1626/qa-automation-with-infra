import os
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CodeBuild project with custom image
        self.project = codebuild.Project(
            self, "SystemTestsBuildProject",
            project_name="system-tests-build-project",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": "3.11"
                        },
                        "commands": [
                            # Install requests for Device Farm uploads
                            "pip install requests"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            # Show environment for debugging
                            "echo 'Environment variables:'",
                            "echo 'ANDROID_PROJECT_ARN='$ANDROID_PROJECT_ARN",
                            "echo 'IOS_PROJECT_ARN='$IOS_PROJECT_ARN", 
                            "echo 'S3_BUCKET='$S3_BUCKET",
                            "echo 'APP_FILE_PATH='$APP_FILE_PATH",
                            "echo 'APP_TYPE='$APP_TYPE",
                            "echo 'Current working directory:'$(pwd)",
                            "ls -la"
                        ]
                    },
                    "build": {
                        "commands": [
                            "python handler.py"
                        ]
                    }
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_asset(
                    self, "CustomBuildImage",
                    # Point to test-suite directory where Dockerfile is located
                    directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "test-suite")
                ),
                compute_type=codebuild.ComputeType.SMALL,
                privileged=True,  # Enable privileged mode for Docker operations
                environment_variables={
                    # Static environment variables (always the same)
                    "ANDROID_PROJECT_ARN": codebuild.BuildEnvironmentVariable(
                        value=android_project_arn
                    ),
                    "IOS_PROJECT_ARN": codebuild.BuildEnvironmentVariable(
                        value=ios_project_arn
                    ),
                    # Dynamic variables will be provided by the S3 Lambda trigger:
                    # - S3_BUCKET
                    # - APP_FILE_PATH  
                    # - APP_TYPE
                },
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