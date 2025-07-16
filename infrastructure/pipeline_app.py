#!/usr/bin/env python3
"""
This is the app file used by the pipeline during synthesis.
It only creates the application stage (not the pipeline itself).
"""
import aws_cdk as cdk
from stacks.stages.system_tests_stage import SystemTestsStage

app = cdk.App()

# Only create the application stage for pipeline deployment
deploy_stage = SystemTestsStage(
    app, "Deploy"
)

app.synth()