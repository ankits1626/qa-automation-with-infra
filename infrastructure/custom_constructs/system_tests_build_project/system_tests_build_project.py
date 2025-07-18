from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct
import os
import yaml

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Reference external buildspec file
        # buildspec_path = os.path.join(os.path.dirname(__file__), "buildspec.yml")
        
        # buildspec = codebuild.BuildSpec.from_source_filename(buildspec_path)

        # Read buildspec from file
        buildspec_path = os.path.join(os.path.dirname(__file__), "buildspec.yml")
        with open(buildspec_path, "r") as file:
            buildspec_content = yaml.safe_load(file)

        # Create CodeBuild project with custom image
        self.project = codebuild.Project(
            self, "SystemTestsBuildProject",
            project_name="system-tests-build-project",
            build_spec=codebuild.BuildSpec.from_object(buildspec_content),
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