from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_codebuild as codebuild,
    Duration,
)
from constructs import Construct
import os

class SystemTestsTrigger(Construct):

    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket, codebuild_project: codebuild.Project, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda function
        self.lambda_function = _lambda.Function(
            self, "SystemTestsTriggerFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="system_tests_trigger_handler.lambda_handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "handlers")
            ),
            timeout=Duration.minutes(5),
            environment={
                'CODEBUILD_PROJECT_NAME': codebuild_project.project_name
            }
        )

        # Grant Lambda permission to start CodeBuild builds
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codebuild:StartBuild"],
                resources=[codebuild_project.project_arn]
            )
        )

        # Grant Lambda permission to read from S3 bucket
        bucket.grant_read(self.lambda_function)

        # Add S3 event notification for .ipa and .apk files
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(self.lambda_function),
            s3.NotificationKeyFilter(suffix=".ipa")
        )
        
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(self.lambda_function),
            s3.NotificationKeyFilter(suffix=".apk")
        )