from aws_cdk import Stack
from constructs import Construct
from custom_constructs.codebuild_project import SystemTestsBuildProject
from custom_constructs.system_tests_bucket import SystemTestsBucket
from custom_constructs.system_tests_trigger.system_tests_trigger import SystemTestsTrigger
class SystemsTestStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Store the project ARNs for use in systems tests
        self.android_project_arn = android_project_arn
        self.ios_project_arn = ios_project_arn

         # Add S3 bucket for system tests
        self.system_tests_bucket = SystemTestsBucket(
            self, "SystemTestsBucket"
        )

        # Add CodeBuild project for test suite building
        self.codebuild_project = SystemTestsBuildProject(
            self, "SystemTestsBuildProject",
            android_project_arn=android_project_arn,
            ios_project_arn=ios_project_arn
        )

        # Add Lambda trigger for app file uploads
        self.system_tests_trigger = SystemTestsTrigger(
            self, "SystemTestsTrigger",
            bucket=self.system_tests_bucket.bucket,
            codebuild_project=self.codebuild_project.project
        )