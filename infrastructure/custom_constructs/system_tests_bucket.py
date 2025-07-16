from aws_cdk import (
    aws_s3 as s3,
    RemovalPolicy,
)
from constructs import Construct

class SystemTestsBucket(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for system tests
        self.bucket = s3.Bucket(
            self, "SystemTestsBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )