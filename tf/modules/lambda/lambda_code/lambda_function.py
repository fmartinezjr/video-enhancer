"""
Lambda function to submit AWS Batch jobs when videos are uploaded to S3.
Triggered by S3 ObjectCreated events.
"""

import json
import os
import urllib.parse
import boto3
from datetime import datetime

batch_client = boto3.client('batch')


def parse_s3_event(event):
    """Extract S3 bucket and key from event."""
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])
    return bucket, key


def generate_job_name(s3_key):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename = s3_key.split('/')[-1].rsplit('.', 1)[0]
    job_name = f"video-enhance-{filename}-{timestamp}"[:128]
    return ''.join(c if c.isalnum() or c in '-_' else '-' for c in job_name)


def create_s3_paths(bucket, key):
    input_uri = f"s3://{bucket}/{key}"
    output_key = key.replace('input/', 'output/', 1)
    output_uri = f"s3://{bucket}/{output_key}"
    return input_uri, output_uri


def submit_batch_job(job_name, job_queue, job_definition, input_uri, output_uri):
    """Submit job to AWS Batch."""
    response = batch_client.submit_job(
        jobName=job_name,
        jobQueue=job_queue,
        jobDefinition=job_definition,
        containerOverrides={
            'command': [
                input_uri,
                output_uri,
                '--noise', '25'
            ]
        }
    )
    return response['jobId']


def lambda_handler(event, context):
    """
    Process S3 event and submit Batch job for video processing.

    Args:
        event: S3 event notification
        context: Lambda context
    """
    job_queue = os.environ['JOB_QUEUE']
    job_definition = os.environ['JOB_DEFINITION']
    bucket_name = os.environ['BUCKET_NAME']

    bucket, key = parse_s3_event(event)
    print(f"Processing video upload: s3://{bucket}/{key}")

    job_name = generate_job_name(key)

    input_uri, output_uri = create_s3_paths(bucket_name, key)

    try:
        job_id = submit_batch_job(job_name, job_queue, job_definition, input_uri, output_uri)

        print(f"Submitted Batch job: {job_name} (ID: {job_id})")
        print(f"Input: {input_uri}")
        print(f"Output: {output_uri}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Batch job submitted successfully',
                'jobId': job_id,
                'jobName': job_name,
                'input': input_uri,
                'output': output_uri
            })
        }

    except Exception as e:
        print(f"Error submitting Batch job: {str(e)}")
        raise
