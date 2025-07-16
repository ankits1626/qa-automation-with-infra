from aws_cdk import (
    Stage,
    Environment,
)

from constructs import Construct
from stacks.device_farm_stack import DeviceFarmStack
from stacks.system_tests_stack import SystemsTestStack

class SystemTestsStage(Stage):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Device Farm stack in us-west-2 (Device Farm region)
        device_farm_env = Environment(region="us-west-2")

        # Systems test stack can be deployed anywhere
        systems_test_env = Environment(region="ap-south-1")  # Uses default region

        device_farm_stack = DeviceFarmStack(
            self, 
            "DeviceFarmStack", 
            env=device_farm_env, 
            cross_region_references=True
        )

        systems_test_stack = SystemsTestStack(
            self, 
            "SystemsTestStack",
            android_project_arn=device_farm_stack.android_project_arn,
            ios_project_arn=device_farm_stack.ios_project_arn,
            env=systems_test_env,
            cross_region_references=True
        )