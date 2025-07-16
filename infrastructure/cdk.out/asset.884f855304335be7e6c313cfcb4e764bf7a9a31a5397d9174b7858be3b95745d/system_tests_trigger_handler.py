import json
import boto3
import os
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    """
    Lambda handler that triggers CodeBuild when .ipa or .apk files are uploaded to S3
    """
    
    codebuild = boto3.client('codebuild')
    
    try:
        # Parse S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            
            print(f"File uploaded: {key} to bucket: {bucket}")
            
            # Check if file is .ipa or .apk
            if key.lower().endswith(('.ipa', '.apk')):
                print(f"Detected mobile app file: {key}")
                
                # Get CodeBuild project name from environment variable
                project_name = os.environ['CODEBUILD_PROJECT_NAME']
                
                # Trigger CodeBuild
                response = codebuild.start_build(
                    projectName=project_name,
                    environmentVariablesOverride=[
                        {
                            'name': 'S3_BUCKET',
                            'value': bucket
                        },
                        {
                            'name': 'APP_FILE_PATH',
                            'value': key
                        },
                        {
                            'name': 'APP_TYPE',
                            'value': 'ios' if key.lower().endswith('.ipa') else 'android'
                        }
                    ]
                )
                
                print(f"Started CodeBuild project: {project_name}")
                print(f"Build ID: {response['build']['id']}")
                
            else:
                print(f"Ignoring non-app file: {key}")
                
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed S3 event')
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing event: {str(e)}')
        }