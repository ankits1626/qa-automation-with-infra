import json
import os
import logging
import boto3
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main entry point for Device Farm test execution"""
    try:
        logger.info("Starting Device Farm test execution")
        
        runner = DeviceFarmTestRunner()
        result = runner.execute()
        
        logger.info("Test execution completed successfully")
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

class DeviceFarmTestRunner:
    def __init__(self):
        """Initialize the test runner with AWS clients and configuration"""
        self.config = self._load_config()
        self.s3_client = boto3.client('s3', region_name='us-west-2')
        self.devicefarm_client = boto3.client('devicefarm', region_name='us-west-2')
        
    def _load_config(self) -> Dict[str, str]:
        """Load configuration from environment variables"""
        required_vars = [
            'ANDROID_PROJECT_ARN',
            'IOS_PROJECT_ARN', 
            'S3_BUCKET',
            'APP_FILE_PATH',
            'APP_TYPE'
        ]
        
        config = {}
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                config[var] = value
        
        if missing_vars:
            raise ValueError(f"Required environment variables not set: {', '.join(missing_vars)}")
            
        logger.info(f"Configuration loaded for app type: {config['APP_TYPE']}")
        return config
    
    def execute(self) -> Dict[str, Any]:
        """Execute the complete test workflow"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        
        logger.info("Starting test execution workflow")
        
        # 1. Build test suite
        logger.info("Step 1: Building test suite")
        test_package_path = self._build_test_suite()
        
        # 2. Download app from S3
        logger.info("Step 2: Downloading app from S3")
        app_file_path = self._download_app()
        
        # 3. Determine Device Farm project based on app type
        project_arn = self._get_project_arn()
        
        # 4. Upload app to Device Farm
        logger.info("Step 3: Uploading app to Device Farm")
        app_upload_arn = self._upload_to_device_farm(app_file_path, 'app', project_arn, timestamp)
        
        # 5. Upload test package to Device Farm
        logger.info("Step 4: Uploading test package to Device Farm")
        test_upload_arn = self._upload_to_device_farm(test_package_path, 'test', project_arn, timestamp)
        
        # 6. Schedule test run
        logger.info("Step 5: Scheduling test run")
        run_result = self._schedule_test_run(project_arn, app_upload_arn, test_upload_arn, timestamp)
        
        logger.info("Test execution workflow completed successfully")
        return run_result
    
    def _build_test_suite(self) -> str:
        """Build test suite using existing build script"""
        logger.info("Building test suite using build-and-zip.sh")
        
        # Try multiple possible locations for test suite
        possible_dirs = [
            "/workspace/test-suite",  # Docker image location
            "/tmp/codebuild-workspace/test-suite",  # Alternative CodeBuild location
            "."  # Current directory
        ]
        
        test_suite_dir = None
        for dir_path in possible_dirs:
            if os.path.exists(dir_path) and os.path.exists(os.path.join(dir_path, "scripts", "build-and-zip.sh")):
                test_suite_dir = dir_path
                logger.info(f"Found test suite directory at: {test_suite_dir}")
                break
        
        if not test_suite_dir:
            raise FileNotFoundError(f"Test suite directory not found. Tried: {possible_dirs}")
        
        # Run the build script
        build_script = os.path.join(test_suite_dir, "scripts", "build-and-zip.sh")
        if not os.path.exists(build_script):
            raise FileNotFoundError(f"Build script not found: {build_script}")
        
        result = subprocess.run(
            ["bash", build_script],
            cwd=test_suite_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Build script failed with return code {result.returncode}")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            raise RuntimeError(f"Test suite build failed: {result.stderr}")
        
        # Check if the zip file was created
        zip_path = os.path.join(test_suite_dir, "system_tests.zip")
        if not os.path.exists(zip_path):
            raise FileNotFoundError("system_tests.zip not found after build")
        
        logger.info("Test suite built successfully")
        return zip_path
    
    def _download_app(self) -> str:
        """Download app file from S3"""
        logger.info(f"Downloading app from s3://{self.config['S3_BUCKET']}/{self.config['APP_FILE_PATH']}")
        
        # Preserve the original filename and extension
        import os.path
        filename = os.path.basename(self.config['APP_FILE_PATH'])
        local_app_path = f"/tmp/{filename}"
        
        try:
            self.s3_client.download_file(
                self.config['S3_BUCKET'],
                self.config['APP_FILE_PATH'],
                local_app_path
            )
            
            # Basic validation without file size check
            file_size = os.path.getsize(local_app_path)
            logger.info(f"App downloaded successfully to {local_app_path}")
            logger.info(f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
            
            # Basic file validation
            if file_size == 0:
                raise ValueError("Downloaded file is empty")
            
            logger.info(f"Downloaded file: {filename}")
            return local_app_path
            
        except Exception as e:
            logger.error(f"Failed to download app from S3: {str(e)}")
            raise
    
    def _get_project_arn(self) -> str:
        """Determine Device Farm project based on app type"""
        app_type = self.config['APP_TYPE'].lower()
        
        if app_type == 'ios':
            project_arn = self.config['IOS_PROJECT_ARN']
            logger.info("Using iOS Device Farm project")
        elif app_type == 'android':
            project_arn = self.config['ANDROID_PROJECT_ARN']
            logger.info("Using Android Device Farm project")
        else:
            raise ValueError(f"Unknown app type: {app_type}. Must be 'ios' or 'android'")
        
        return project_arn
    
    def _upload_to_device_farm(self, file_path: str, upload_type: str, project_arn: str, timestamp: str) -> str:
        """Upload file to Device Farm"""
        logger.info(f"Uploading {upload_type} file: {file_path}")
        
        # Determine upload type and name
        if upload_type == 'app':
            df_upload_type = f"{self.config['APP_TYPE'].upper()}_APP"
            # Use the original filename from S3
            upload_name = os.path.basename(self.config['APP_FILE_PATH'])
        elif upload_type == 'test':
            df_upload_type = "APPIUM_NODE_TEST_PACKAGE"
            upload_name = f"tests-{timestamp}.zip"
        else:
            raise ValueError(f"Unknown upload type: {upload_type}")
        
        try:
            # Create upload
            response = self.devicefarm_client.create_upload(
                projectArn=project_arn,
                name=upload_name,
                type=df_upload_type
            )
            
            upload_arn = response['upload']['arn']
            upload_url = response['upload']['url']
            
            logger.info(f"Created {upload_type} upload with ARN: {upload_arn}")
            
            # Upload file using pre-signed URL with proper headers
            import requests
            
            # Extract filename for Content-Disposition header
            filename = os.path.basename(file_path)
            
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
            
            with open(file_path, 'rb') as f:
                response = requests.put(upload_url, data=f, headers=headers)
                response.raise_for_status()
            
            logger.info(f"{upload_type.capitalize()} uploaded successfully")
            
            # Wait for upload to be processed
            self._wait_for_upload_processing(upload_arn)
            
            return upload_arn
            
        except Exception as e:
            logger.error(f"Failed to upload {upload_type} to Device Farm: {str(e)}")
            raise
    
    def _wait_for_upload_processing(self, upload_arn: str, max_wait_time: int = 300):
        """Wait for upload to be processed by Device Farm"""
        logger.info("Waiting for upload to be processed...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                response = self.devicefarm_client.get_upload(arn=upload_arn)
                upload_info = response['upload']
                status = upload_info['status']
                
                logger.info(f"Upload status: {status}")
                
                # Log additional details for debugging
                if 'message' in upload_info:
                    logger.info(f"Upload message: {upload_info['message']}")
                if 'metadata' in upload_info:
                    logger.info(f"Upload metadata: {upload_info['metadata']}")
                
                if status == 'SUCCEEDED':
                    logger.info("Upload processed successfully")
                    return
                elif status == 'FAILED':
                    error_msg = f"Upload processing failed. Status: {status}"
                    if 'message' in upload_info:
                        error_msg += f". Message: {upload_info['message']}"
                    raise RuntimeError(error_msg)
                
                time.sleep(10)  # Wait 10 seconds before checking again
                
            except Exception as e:
                logger.error(f"Error checking upload status: {str(e)}")
                raise
        
        raise TimeoutError(f"Upload processing timed out after {max_wait_time} seconds")
    
    def _upload_existing_test_spec(self, project_arn: str, timestamp: str) -> str:
        """Upload existing test spec file from test suite to Device Farm"""
        logger.info("Uploading existing test spec to Device Farm")
        
        # Test spec file is at the same level as handler.py
        test_spec_filename = "appium-ios-test.yml"
        test_spec_path = os.path.join(os.path.dirname(__file__), test_spec_filename)
        
        # Fallback to current directory if __file__ approach doesn't work
        if not os.path.exists(test_spec_path):
            test_spec_path = test_spec_filename
        
        if not os.path.exists(test_spec_path):
            raise FileNotFoundError(f"Test spec file '{test_spec_filename}' not found at: {test_spec_path}")
        
        logger.info(f"Found test spec file at: {test_spec_path}")
        
        try:
            # Create upload for test spec
            response = self.devicefarm_client.create_upload(
                projectArn=project_arn,
                name=f"appium-ios-test-spec-{timestamp}.yml",
                type="APPIUM_NODE_TEST_SPEC"
            )
            
            upload_arn = response['upload']['arn']
            upload_url = response['upload']['url']
            
            logger.info(f"Created test spec upload with ARN: {upload_arn}")
            
            # Upload test spec file
            import requests
            filename = os.path.basename(test_spec_path)
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
            
            with open(test_spec_path, 'rb') as f:
                response = requests.put(upload_url, data=f, headers=headers)
                response.raise_for_status()
            
            logger.info("Existing test spec uploaded successfully")
            
            # Wait for upload to be processed
            self._wait_for_upload_processing(upload_arn)
            
            return upload_arn
            
        except Exception as e:
            logger.error(f"Failed to upload existing test spec to Device Farm: {str(e)}")
            raise
    
    def _schedule_test_run(self, project_arn: str, app_arn: str, test_arn: str, timestamp: str) -> Dict[str, Any]:
        """Schedule the Device Farm test run"""
        logger.info("Scheduling Device Farm test run")
        
        try:
            # Get the default device pool
            device_pools_response = self.devicefarm_client.list_device_pools(arn=project_arn)
            device_pools = device_pools_response.get('devicePools', [])
            
            if not device_pools:
                raise RuntimeError("No device pools found for the project")
            
            device_pool_arn = device_pools[0]['arn']
            logger.info(f"Using device pool: {device_pool_arn}")
            
            # Upload the existing test spec file
            test_spec_arn = self._upload_existing_test_spec(project_arn, timestamp)
            
            # Schedule the run using custom environment mode
            run_name = f"SystemTest-{timestamp}"
            response = self.devicefarm_client.schedule_run(
                projectArn=project_arn,
                appArn=app_arn,
                devicePoolArn=device_pool_arn,
                name=run_name,
                test={
                    'type': 'APPIUM_NODE',
                    'testPackageArn': test_arn,
                    'testSpecArn': test_spec_arn  # Required for custom environment mode
                }
            )
            
            run_arn = response['run']['arn']
            run_name = response['run']['name']
            
            result = {
                'run_arn': run_arn,
                'run_name': run_name,
                'project_arn': project_arn,
                'device_pool_arn': device_pool_arn,
                'test_spec_arn': test_spec_arn,
                'timestamp': timestamp
            }
            
            logger.info(f"Test run scheduled successfully:")
            logger.info(f"  Name: {run_name}")
            logger.info(f"  ARN: {run_arn}")
            logger.info("Monitor progress in AWS Device Farm console")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to schedule test run: {str(e)}")
            raise

# Allow running as script
if __name__ == "__main__":
    result = lambda_handler({}, None)
    print(json.dumps(result, indent=2))