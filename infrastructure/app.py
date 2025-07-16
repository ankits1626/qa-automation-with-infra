#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.pipeline_stack import PipelineStack
from stacks.stages.system_tests_stage import SystemTestsStage

app = cdk.App()

pipeline_stack = PipelineStack(
    app,
    "PipelineStack",
    github_repo="ankits1626/qa-automation-with-infra",  # Replace with your GitHub repo
    codestar_connection_arn="arn:aws:codeconnections:ap-south-1:637423487119:connection/0c9cafc8-09e5-4bdd-ac24-6c259df0a22c",  # Replace with your CodeStar connection ARN
    github_branch="main",
    env=cdk.Environment(
        account="637423487119",
        region="ap-south-1"  # Explicit region for the pipeline
    )  # Pipeline can be deployed in any region
)


app.synth()