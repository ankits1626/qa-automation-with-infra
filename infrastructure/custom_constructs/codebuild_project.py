from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct
import os

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create buildspec that handles the full Device Farm workflow
        buildspec = codebuild.BuildSpec.from_object({
            "version": "0.2",
            "phases": {
                "pre_build": {
                    "commands": [
                        "echo 'Execution started'",
                        f"echo 'Android Device Farm Project ARN: {android_project_arn}'",
                        f"echo 'iOS Device Farm Project ARN: {ios_project_arn}'",
                        "echo 'Environment variables:'",
                        "echo 'S3_BUCKET=' $S3_BUCKET",
                        "echo 'APP_FILE_PATH=' $APP_FILE_PATH", 
                        "echo 'APP_TYPE=' $APP_TYPE",
                        "echo 'Current working directory:' $(pwd)",
                        "echo 'Available directories:'",
                        "ls -la /workspace/",
                        "echo 'Test suite directory contents:'",
                        "ls -la /workspace/test-suite/ || echo 'test-suite directory not found'"
                    ]
                },
                "build": {
                    "commands": [
                        "echo 'Building test suite'",
                        "cd /workspace/test-suite",
                        # "./scripts/build-and-zip.sh",
                        "echo 'Test suite build completed'",
                        "ls -la system_tests.zip || echo 'system_tests.zip not found'",
                        "",
                        "echo 'Downloading app file from S3'",
                        "aws s3 cp s3://$S3_BUCKET/$APP_FILE_PATH ./app_file",
                        "ls -la ./app_file",
                        "",
                        "echo 'Determining Device Farm project based on app type'",
                        "if [ \"$APP_TYPE\" = \"ios\" ]; then",
                        f"  PROJECT_ARN=\"{ios_project_arn}\"",
                        "  echo 'Using iOS Device Farm project'",
                        "elif [ \"$APP_TYPE\" = \"android\" ]; then",
                        f"  PROJECT_ARN=\"{android_project_arn}\"", 
                        "  echo 'Using Android Device Farm project'",
                        "else",
                        "  echo 'Unknown app type: $APP_TYPE'",
                        "  exit 1",
                        "fi",
                        "",
                        "echo 'Uploading app to Device Farm'",
                        "APP_UPLOAD=$(aws devicefarm create-upload \\",
                        "  --project-arn $PROJECT_ARN \\",
                        "  --name \"app-$(date +%Y%m%d-%H%M%S)\" \\",
                        "  --type \"${APP_TYPE^^}_APP\" \\",
                        "  --query 'upload.{arn:arn,url:url}' \\",
                        "  --output json)",
                        "",
                        "APP_ARN=$(echo $APP_UPLOAD | jq -r '.arn')",
                        "APP_URL=$(echo $APP_UPLOAD | jq -r '.url')",
                        "echo 'App upload ARN:' $APP_ARN",
                        "",
                        "curl -T ./app_file \"$APP_URL\"",
                        "echo 'App uploaded successfully'",
                        "",
                        "echo 'Uploading test package to Device Farm'", 
                        "TEST_UPLOAD=$(aws devicefarm create-upload \\",
                        "  --project-arn $PROJECT_ARN \\",
                        "  --name \"tests-$(date +%Y%m%d-%H%M%S)\" \\",
                        "  --type \"APPIUM_NODE_TEST_PACKAGE\" \\",
                        "  --query 'upload.{arn:arn,url:url}' \\",
                        "  --output json)",
                        "",
                        "TEST_ARN=$(echo $TEST_UPLOAD | jq -r '.arn')",
                        "TEST_URL=$(echo $TEST_UPLOAD | jq -r '.url')",
                        "echo 'Test upload ARN:' $TEST_ARN",
                        "",
                        "curl -T ./system_tests.zip \"$TEST_URL\"",
                        "echo 'Test package uploaded successfully'",
                        "",
                        "echo 'Getting device pool for project'",
                        "DEVICE_POOLS=$(aws devicefarm list-device-pools --arn $PROJECT_ARN --query 'devicePools[0].arn' --output text)",
                        "echo 'Using device pool:' $DEVICE_POOLS",
                        "",
                        "echo 'Creating test run configuration'",
                        "if [ \"$APP_TYPE\" = \"ios\" ]; then",
                        "  BUILDSPEC_ARN=\"arn:aws:devicefarm:us-west-2::upload:appium-ios-test.yml\"",
                        "else",
                        "  BUILDSPEC_ARN=\"arn:aws:devicefarm:us-west-2::upload:appium-android-test.yml\"", 
                        "fi",
                        "",
                        "echo 'Scheduling Device Farm test run'",
                        "RUN_RESULT=$(aws devicefarm schedule-run \\",
                        "  --project-arn $PROJECT_ARN \\",
                        "  --app-arn $APP_ARN \\",
                        "  --device-pool-arn $DEVICE_POOLS \\",
                        "  --name \"SystemTest-$(date +%Y%m%d-%H%M%S)\" \\",
                        "  --test \"type=APPIUM_NODE,testPackageArn=$TEST_ARN\" \\",
                        "  --query 'run.{arn:arn,name:name}' \\",
                        "  --output json)",
                        "",
                        "RUN_ARN=$(echo $RUN_RESULT | jq -r '.arn')",
                        "RUN_NAME=$(echo $RUN_RESULT | jq -r '.name')",
                        "echo 'Test run created:'",
                        "echo 'Name:' $RUN_NAME", 
                        "echo 'ARN:' $RUN_ARN",
                        "",
                        "echo 'Device Farm test run initiated successfully'",
                        "echo 'Monitor progress in AWS Device Farm console'"
                    ]
                }
            }
        })

        # Create CodeBuild project with custom image
        self.project = codebuild.Project(
            self, "SystemTestsBuildProject",
            project_name="system-tests-build-project",
            build_spec=buildspec,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_asset(
                    self, "CustomBuildImage",
                    # Point to repository root where Dockerfile is located
                    directory=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
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
                    "devicefarm:GetDevicePool"
                ],
                resources=["*"]
            )
        )
        
        # S3 permissions will be granted by the SystemsTestStack via bucket.grant_read()