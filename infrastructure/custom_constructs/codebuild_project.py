from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create buildspec that prints the required information
        buildspec = codebuild.BuildSpec.from_object({
            "version": 0.2,
            "phases": {
                "pre_build": {
                    "commands": [
                        "echo 'Execution started'",
                        f"echo 'Android Device Farm Project ARN: {android_project_arn}'",
                        f"echo 'iOS Device Farm Project ARN: {ios_project_arn}'",
                        "echo 'Building test suite'"
                    ]
                },
                "build": {
                    "commands": [
                        "echo 'Test suite build completed'"
                    ]
                }
            }
        })

        # Create CodeBuild project
        self.project = codebuild.Project(
            self, "TestSuiteBuilder",
            project_name="test-suite-builder",
            build_spec=buildspec,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL
            )
        )