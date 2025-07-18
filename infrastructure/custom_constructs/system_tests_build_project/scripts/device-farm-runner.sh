#!/bin/bash
set -e

# Accept project ARNs as parameters
ANDROID_PROJECT_ARN="$1"
IOS_PROJECT_ARN="$2"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check required environment variables
check_env_vars() {
    log "Checking required environment variables..."
    
    if [ -z "$S3_BUCKET" ]; then
        log "ERROR: S3_BUCKET environment variable is not set"
        exit 1
    fi
    
    if [ -z "$APP_FILE_PATH" ]; then
        log "ERROR: APP_FILE_PATH environment variable is not set"
        exit 1
    fi
    
    if [ -z "$APP_TYPE" ]; then
        log "ERROR: APP_TYPE environment variable is not set"
        exit 1
    fi
    
    log "Environment variables validation passed"
}

# Function to display environment info
show_environment_info() {
    log "Environment variables:"
    log "S3_BUCKET=$S3_BUCKET"
    log "APP_FILE_PATH=$APP_FILE_PATH"
    log "APP_TYPE=$APP_TYPE"
    log "ANDROID_PROJECT_ARN=$ANDROID_PROJECT_ARN"
    log "IOS_PROJECT_ARN=$IOS_PROJECT_ARN"
    log "Current working directory: $(pwd)"
    
    log "Available directories:"
    ls -la /workspace/
    
    log "Test suite directory contents:"
    ls -la /workspace/test-suite/ || log "test-suite directory not found"
}

# Function to build test suite
build_test_suite() {
    log "Building test suite..."
    cd /workspace/test-suite
    ./scripts/build-and-zip.sh
    log "Test suite build completed"
    
    if [ ! -f "system_tests.zip" ]; then
        log "ERROR: system_tests.zip not found after build"
        exit 1
    fi
    
    log "Test suite zip file created successfully"
    ls -la system_tests.zip
}

# Function to download app from S3
download_app_file() {
    log "Downloading app file from S3..."
    aws s3 cp "s3://$S3_BUCKET/$APP_FILE_PATH" ./app_file
    
    if [ ! -f "./app_file" ]; then
        log "ERROR: Failed to download app file from S3"
        exit 1
    fi
    
    log "App file downloaded successfully"
    ls -la ./app_file
}

# Function to determine Device Farm project ARN
determine_project_arn() {
    log "Determining Device Farm project based on app type: $APP_TYPE"
    
    case "$APP_TYPE" in
        "ios")
            PROJECT_ARN="$IOS_PROJECT_ARN"
            log "Using iOS Device Farm project"
            ;;
        "android")
            PROJECT_ARN="$ANDROID_PROJECT_ARN"
            log "Using Android Device Farm project"
            ;;
        *)
            log "ERROR: Unknown app type: $APP_TYPE"
            exit 1
            ;;
    esac
    
    log "Selected project ARN: $PROJECT_ARN"
}

# Function to upload app to Device Farm
upload_app_to_device_farm() {
    log "Uploading app to Device Farm..."
    
    local app_upload_result
    app_upload_result=$(aws devicefarm create-upload \
        --project-arn "$PROJECT_ARN" \
        --name "app-$(date +%Y%m%d-%H%M%S)" \
        --type "${APP_TYPE^^}_APP" \
        --query 'upload.{arn:arn,url:url}' \
        --output json)
    
    APP_ARN=$(echo "$app_upload_result" | jq -r '.arn')
    APP_URL=$(echo "$app_upload_result" | jq -r '.url')
    
    log "App upload ARN: $APP_ARN"
    
    curl -T ./app_file "$APP_URL"
    log "App uploaded successfully"
}

# Function to upload test package to Device Farm
upload_test_package() {
    log "Uploading test package to Device Farm..."
    
    local test_upload_result
    test_upload_result=$(aws devicefarm create-upload \
        --project-arn "$PROJECT_ARN" \
        --name "tests-$(date +%Y%m%d-%H%M%S)" \
        --type "APPIUM_NODE_TEST_PACKAGE" \
        --query 'upload.{arn:arn,url:url}' \
        --output json)
    
    TEST_ARN=$(echo "$test_upload_result" | jq -r '.arn')
    TEST_URL=$(echo "$test_upload_result" | jq -r '.url')
    
    log "Test upload ARN: $TEST_ARN"
    
    curl -T ./system_tests.zip "$TEST_URL"
    log "Test package uploaded successfully"
}

# Function to get device pool
get_device_pool() {
    log "Getting device pool for project..."
    
    DEVICE_POOLS=$(aws devicefarm list-device-pools \
        --arn "$PROJECT_ARN" \
        --query 'devicePools[0].arn' \
        --output text)
    
    log "Using device pool: $DEVICE_POOLS"
}

# Function to schedule test run
schedule_test_run() {
    log "Scheduling Device Farm test run..."
    
    local run_result
    run_result=$(aws devicefarm schedule-run \
        --project-arn "$PROJECT_ARN" \
        --app-arn "$APP_ARN" \
        --device-pool-arn "$DEVICE_POOLS" \
        --name "SystemTest-$(date +%Y%m%d-%H%M%S)" \
        --test "type=APPIUM_NODE,testPackageArn=$TEST_ARN" \
        --query 'run.{arn:arn,name:name}' \
        --output json)
    
    RUN_ARN=$(echo "$run_result" | jq -r '.arn')
    RUN_NAME=$(echo "$run_result" | jq -r '.name')
    
    log "Test run created:"
    log "Name: $RUN_NAME"
    log "ARN: $RUN_ARN"
    log "Device Farm test run initiated successfully"
    log "Monitor progress in AWS Device Farm console"
}

# Main execution
main() {
    log "Starting Device Farm workflow..."
    
    check_env_vars
    show_environment_info
    build_test_suite
    download_app_file
    determine_project_arn
    upload_app_to_device_farm
    upload_test_package
    get_device_pool
    schedule_test_run
    
    log "Device Farm workflow completed successfully"
}

# Execute main function
main "$@"