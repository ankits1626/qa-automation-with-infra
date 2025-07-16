#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.device_farm_stack import DeviceFarmStack
from stacks.system_tests_stack import SystemsTestStack


app = cdk.App()
device_farm_env = cdk.Environment(region="us-west-2")

# Systems test stack can be deployed anywhere
systems_test_env = cdk.Environment(region="ap-south-1")  # Uses default region

device_farm_stack = DeviceFarmStack(
    app, 
    "DeviceFarmStack", 
    env=device_farm_env, 
    cross_region_references=True
)

systems_test_stack = SystemsTestStack(
    app, 
    "SystemsTestStack",
    android_project_arn=device_farm_stack.android_project_arn,
    ios_project_arn=device_farm_stack.ios_project_arn,
    env=systems_test_env,
    cross_region_references=True
)

app.synth()