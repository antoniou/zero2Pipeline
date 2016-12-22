
from __future__ import print_function
from boto3.session import Session
import boto3
import json
import os.path
import botocore
import tempfile
import zipfile
import traceback

code_pipeline = boto3.client('codepipeline')

def get_user_params(job_data):
    """Decodes the JSON user parameters and validates the required properties.

    Args:
        job_data: The job data structure containing the UserParameters string which should be a valid JSON structure

    Returns:
        The JSON parameters decoded as a dictionary.

    Raises:
        Exception: The JSON can't be decoded or a property is missing.

    """
    try:
        # Get the user parameters which contain the stack, artifact and file settings
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        decoded_parameters = json.loads(user_parameters)

    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        raise Exception('UserParameters could not be decoded as JSON')

    if 'stack' not in decoded_parameters:
        # Validate that the stack is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the stack name')

    if 'artifact' not in decoded_parameters:
        # Validate that the artifact name is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the artifact name')

    if 'file' not in decoded_parameters:
        # Validate that the template file is provided, otherwise fail the job
        # with a helpful message.
        raise Exception('Your UserParameters JSON must include the template file name')

    return decoded_parameters

def find_artifact(artifacts, name):
    """Finds the artifact 'name' among the 'artifacts'

    Args:
        artifacts: The list of artifacts available to the function
        name: The artifact we wish to use
    Returns:
        The artifact dictionary found
    Raises:
        Exception: If no matching artifact is found

    """
    for artifact in artifacts:
        if artifact['name'] == name:
            return artifact

    raise Exception('Input artifact named "{0}" not found in event'.format(name))

def get_configuration_file(s3, artifact, file_in_zip):
    """Gets the template artifact

    Downloads the artifact from the S3 artifact store to a temporary file
    then extracts the zip and returns the file containing the CloudFormation
    template.

    Args:
        artifact: The artifact to download
        file_in_zip: The path to the file within the zip containing the template

    Returns:
        The CloudFormation template as a string

    Raises:
        Exception: Any exception thrown while downloading the artifact or unzipping it

    """

    tmp_file = tempfile.NamedTemporaryFile()
    bucket = artifact['location']['s3Location']['bucketName']
    key = artifact['location']['s3Location']['objectKey']

    with tempfile.NamedTemporaryFile() as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, 'r') as zip:
            data = zip.read(file_in_zip)
            return { file_in_zip: data }

def extend_configuration_file(config_file, artifact_location):
    config = json.loads(config_file)
    config['Properties']['S3ConfigBucketName'] = artifact_location['location']['s3Location']['bucketName']
    config['Properties']['S3ConfigBucketObject'] = artifact_location['location']['s3Location']['objectKey']

    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    json.dump(config, tmp_file)
    tmp_file.close()

    return tmp_file


def put_job_failure(job, message):
    """Notify CodePipeline of a failed job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_failure_result()

    """
    print('Putting job failure')
    print(message)
    # code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})

def put_job_success(job, message):
    """Notify CodePipeline of a successful job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_success_result()

    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)

def setup_s3_client(job_data):
    """Creates an S3 client

    Uses the credentials passed in the event by CodePipeline. These
    credentials can be used to access the artifact bucket.

    Args:
        job_data: The job data structure

    Returns:
        An S3 client with the appropriate credentials

    """
    key_id = job_data['artifactCredentials']['accessKeyId']
    key_secret = job_data['artifactCredentials']['secretAccessKey']
    session_token = job_data['artifactCredentials']['sessionToken']

    session = Session(aws_access_key_id=key_id,
        aws_secret_access_key=key_secret,
        aws_session_token=session_token)
    return session.client('s3', config=botocore.client.Config(signature_version='s3v4'))

def generate_output_artifact(output_files):
    tmp_file = tempfile.NamedTemporaryFile()
    zf = zipfile.ZipFile(tmp_file.name, mode='w')
    try:
        for f, data in output_files.iteritems():
            zf.write(data.name, arcname=f)
    finally:
        zf.close()

    return tmp_file


def upload_artifact(s3, file, artifact_location):
    bucket = artifact_location['location']['s3Location']['bucketName']
    key = artifact_location['location']['s3Location']['objectKey']
    with open(file.name, 'rb') as data:
        s3.upload_fileobj(data, bucket, "{0}.zip".format(key))

def lambda_handler(event, context):
    """The Lambda function handler

    Args:
        event: The event passed by Lambda
        context: The context passed by Lambda

    """

    try:
        # Extract the Job ID
        job_id = event['CodePipeline.job']['id']

        # Extract the Job Data
        job_data = event['CodePipeline.job']['data']

        # Extract the params
        # params = get_user_params(job_data)

        # Get the list of artifacts passed to the function
        artifacts = job_data['inputArtifacts']

        # Get the artifact details
        artifact_data = find_artifact(artifacts, 'MyInfra')

        # Get S3 client to access artifact with
        s3 = setup_s3_client(job_data)

        path = 'templates/parameters-int.json'

        # Get the JSON template file out of the artifact
        config_file_map = get_configuration_file(s3, artifact_data, path)

        config_file_map[path] = extend_configuration_file(config_file_map[path], find_artifact(artifacts, 'MyApp'))

        output_artifact = generate_output_artifact(config_file_map)

        outputArtifactDetails = find_artifact(job_data['outputArtifacts'], 'BuildParamsArtifact')
        upload_artifact(s3, output_artifact, outputArtifactDetails)

        put_job_success(job_id, 'Configuration file created successfully')

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        print('Function failed due to exception.')
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(e))

    print('Function complete.')
    return "Complete."

if __name__ == '__main__':
    lambda_handler(json.load(open("test/fixtures/event.json")), None)
