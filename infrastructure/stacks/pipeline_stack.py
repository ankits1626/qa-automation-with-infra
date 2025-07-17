from aws_cdk import (
    Stack,
    pipelines,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct
from stacks.stages.system_tests_stage import SystemTestsStage
from aws_cdk.aws_codepipeline import PipelineType
class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, github_repo: str, codestar_connection_arn: str, github_branch: str = "main", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the pipeline
        self.pipeline = pipelines.CodePipeline(
            self, "SystemTestsPipeline",
            pipeline_name="system-tests-pipeline",
            pipeline_type=PipelineType.V2,
           cross_account_keys=True,
            docker_enabled_for_self_mutation=True,
            docker_enabled_for_synth=True,
            self_mutation=True,
            synth=pipelines.CodeBuildStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    repo_string=github_repo,
                    branch=github_branch,
                    connection_arn=codestar_connection_arn
                ),
                role_policy_statements=[
                    iam.PolicyStatement(
                        actions=["sts:AssumeRole"],
                        resources=["*"],
                        conditions={
                            "StringEquals": {
                                "iam:ResourceTag/aws-cdk:bootstrap-role": "lookup"
                            }
                        },
                    ),
                ],
                commands=[
                    'cd "infrastructure"',
                    "curl -LsSf https://astral.sh/uv/install.sh | sh",
                    "export PATH=$HOME/.local/bin:$PATH",
                    "uv sync",
                    "npm install -g aws-cdk",
                    "uv run cdk synth"
                ],
                primary_output_directory="infrastructure/cdk.out",
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.STANDARD_7_0
                ),
                partial_build_spec=codebuild.BuildSpec.from_object(
                    {
                        "version": "0.2",
                        "phases": {
                            "install": {
                                "runtime-versions": {
                                    "nodejs": "20.x",
                                    "python": "3.12",
                                },
                            },
                        },
                    }
                ),
            )
        )

        # Add deployment stage
        deploy_stage = SystemTestsStage(
            self, "Deploy"
        )
        
        self.pipeline.add_stage(deploy_stage)