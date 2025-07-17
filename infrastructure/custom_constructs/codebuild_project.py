from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

class SystemTestsBuildProject(Construct):

    def __init__(self, scope: Construct, construct_id: str, android_project_arn: str, ios_project_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create buildspec that handles the complete test workflow
        buildspec = codebuild.BuildSpec.from_object({
            "version": 0.2,
            "phases": {
                "pre_build": {
                    "commands": [
                        "echo 'Execution started'",
                        f"echo 'Android Device Farm Project ARN: {android_project_arn}'",
                        f"echo 'iOS Device Farm Project ARN: {ios_project_arn}'",
                        "echo 'Building test suite'",
                        # Install AWS CLI (if not already available)
                        "pip install awscli",
                        # Navigate to test-suite directory where scripts folder is located
                        "cd ../test-suite",
                        "pwd",
                        "ls -la",
                        "echo 'Contents of test-suite directory:'",
                        "find . -name '*.sh' -type f",
                        "echo 'Checking scripts directory:'",
                        "ls -la scripts/ || echo 'scripts directory not found'"
                    ]
                },
                "build": {
                    "commands": [
                        # Build the test suite
                        "echo 'Running build-and-zip script...'",
                        "chmod +x ./scripts/build-and-zip.sh",
                        "./scripts/build-and-zip.sh",
                        "echo 'Test suite build completed'",
                        "ls -la *.zip",
                        
                        # Determine app type and upload to Device Farm
                        "echo 'Processing uploaded app file...'",
                        "if [ ! -z \"$APP_FILE_PATH\" ]; then",
                        "  echo \"App file detected: $APP_FILE_PATH\"",
                        "  if [ \"$APP_TYPE\" = \"ios\" ]; then",
                        "    echo 'Processing iOS app (.ipa)'",
                        "    # Upload IPA to Device Farm",
                        f"    IPA_UPLOAD_ARN=$(aws devicefarm create-upload --project-arn {ios_project_arn} --name app.ipa --type IOS_APP --query 'upload.arn' --output text)",
                        "    echo \"IPA Upload ARN: $IPA_UPLOAD_ARN\"",
                        "    IPA_UPLOAD_URL=$(aws devicefarm get-upload --arn $IPA_UPLOAD_ARN --query 'upload.url' --output text)",
                        "    curl -T $S3_BUCKET/$APP_FILE_PATH $IPA_UPLOAD_URL",
                        "    ",
                        "    # Upload test suite to Device Farm",
                        f"    TEST_UPLOAD_ARN=$(aws devicefarm create-upload --project-arn {ios_project_arn} --name system_tests.zip --type APPIUM_NODE_TEST_PACKAGE --query 'upload.arn' --output text)",
                        "    echo \"Test Upload ARN: $TEST_UPLOAD_ARN\"",
                        "    TEST_UPLOAD_URL=$(aws devicefarm get-upload --arn $TEST_UPLOAD_ARN --query 'upload.url' --output text)",
                        "    curl -T system_tests.zip $TEST_UPLOAD_URL",
                        "    ",
                        "    # Upload build spec for iOS",
                        f"    SPEC_UPLOAD_ARN=$(aws devicefarm create-upload --project-arn {ios_project_arn} --name appium-ios-test.yml --type APPIUM_NODE_TEST_SPEC --query 'upload.arn' --output text)",
                        "    echo \"Spec Upload ARN: $SPEC_UPLOAD_ARN\"",
                        "    SPEC_UPLOAD_URL=$(aws devicefarm get-upload --arn $SPEC_UPLOAD_ARN --query 'upload.url' --output text)",
                        "    curl -T appium-ios-test.yml $SPEC_UPLOAD_URL",
                        "    ",
                        "    # Schedule test run",
                        "    echo 'Scheduling iOS test run...'",
                        f"    aws devicefarm schedule-run --project-arn {ios_project_arn} --app-arn $IPA_UPLOAD_ARN --device-pool-arn {ios_project_arn}/devicepool/default --name 'iOS-SystemTests-$(date +%Y%m%d-%H%M%S)' --test type=APPIUM_NODE,testPackageArn=$TEST_UPLOAD_ARN,testSpecArn=$SPEC_UPLOAD_ARN",
                        "  elif [ \"$APP_TYPE\" = \"android\" ]; then",
                        "    echo 'Processing Android app (.apk)'",
                        "    # Upload APK to Device Farm",
                        f"    APK_UPLOAD_ARN=$(aws devicefarm create-upload --project-arn {android_project_arn} --name app.apk --type ANDROID_APP --query 'upload.arn' --output text)",
                        "    echo \"APK Upload ARN: $APK_UPLOAD_ARN\"",
                        "    APK_UPLOAD_URL=$(aws devicefarm get-upload --arn $APK_UPLOAD_ARN --query 'upload.url' --output text)",
                        "    curl -T $S3_BUCKET/$APP_FILE_PATH $APK_UPLOAD_URL",
                        "    ",
                        "    # Upload test suite to Device Farm",
                        f"    TEST_UPLOAD_ARN=$(aws devicefarm create-upload --project-arn {android_project_arn} --name system_tests.zip --type APPIUM_NODE_TEST_PACKAGE --query 'upload.arn' --output text)",
                        "    echo \"Test Upload ARN: $TEST_UPLOAD_ARN\"",
                        "    TEST_UPLOAD_URL=$(aws devicefarm get-upload --arn $TEST_UPLOAD_ARN --query 'upload.url' --output text)",
                        "    curl -T system_tests.zip $TEST_UPLOAD_URL",
                        "    ",
                        "    # Upload build spec for Android",
                        f"    SPEC_UPLOAD_ARN=$(aws devicefarm create-upload --project-arn {android_project_arn} --name appium-android-test.yml --type APPIUM_NODE_TEST_SPEC --query 'upload.arn' --output text)",
                        "    echo \"Spec Upload ARN: $SPEC_UPLOAD_ARN\"",
                        "    SPEC_UPLOAD_URL=$(aws devicefarm get-upload --arn $SPEC_UPLOAD_ARN --query 'upload.url' --output text)",
                        "    curl -T appium-android-test.yml $SPEC_UPLOAD_URL",
                        "    ",
                        "    # Schedule test run",
                        "    echo 'Scheduling Android test run...'",
                        f"    aws devicefarm schedule-run --project-arn {android_project_arn} --app-arn $APK_UPLOAD_ARN --device-pool-arn {android_project_arn}/devicepool/default --name 'Android-SystemTests-$(date +%Y%m%d-%H%M%S)' --test type=APPIUM_NODE,testPackageArn=$TEST_UPLOAD_ARN,testSpecArn=$SPEC_UPLOAD_ARN",
                        "  else",
                        "    echo 'Unknown app type or no app file provided'",
                        "  fi",
                        "else",
                        "  echo 'No app file specified, running test suite build only'",
                        "fi"
                    ]
                }
            },
            "artifacts": {
                "files": [
                    "system_tests.zip"
                ]
            }
        })

        # Create CodeBuild project
        self.project = codebuild.Project(
            self, "SystemTestsBuildProject",
            project_name="system-tests-build-project",
            build_spec=buildspec,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.MEDIUM  # Increased for build process
            )
        )

        # Add Device Farm permissions
        self.project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "devicefarm:CreateUpload",
                    "devicefarm:GetUpload",
                    "devicefarm:ScheduleRun",
                    "devicefarm:ListDevicePools",
                    "devicefarm:GetProject"
                ],
                resources=["*"]
            )
        )

        # Add S3 permissions to read uploaded app files
        self.project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:GetObjectVersion"
                ],
                resources=["*"]  # You might want to restrict this to specific bucket
            )
        )