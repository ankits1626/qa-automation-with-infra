from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct
import os

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create buildspec that works from repo root
        buildspec = codebuild.BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "pre_build": {
                    "commands": [
                        "echo 'Execution started'",
                        "pwd && ls -la",  # Debug: show repo structure
                        f"echo 'Android Device Farm Project ARN: {android_project_arn}'",
                        f"echo 'iOS Device Farm Project ARN: {ios_project_arn}'",
                    ]
                },
                "build": {
                    "commands": [
                        # Build test suite
                        "cd test-suite",
                        "./scripts/build-and-zip.sh",
                        "ls -la system_tests.zip",
                        
                        # Device Farm operations
                        "echo 'Test suite build completed'",
                        "echo 'App file path: $APP_FILE_PATH'",
                        "echo 'App type: $APP_TYPE'",
                        
                        # TODO: Add actual Device Farm upload commands
                        "echo 'Ready for Device Farm upload...'",
                    ]
                }
            }
        })

        # Create CodeBuild project with custom Docker image
        self.project = codebuild.Project(
            self, "SystemTestsBuildProject",
            project_name="system-tests-build-project",
            build_spec=buildspec,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_asset(
                    self, "TestSuiteImage",
                    directory=os.path.join(os.path.dirname(__file__), "docker-image")
                ),
                compute_type=codebuild.ComputeType.SMALL
            )
        )
        
        # Add Device Farm permissions
        self.project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "devicefarm:CreateUpload",
                    "devicefarm:GetUpload", 
                    "devicefarm:ScheduleRun",
                    "devicefarm:GetRun",
                    "devicefarm:ListProjects",
                    "devicefarm:ListDevicePools",
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                resources=["*"]
            )
        )