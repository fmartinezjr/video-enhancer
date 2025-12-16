"""S3 utilities for downloading and uploading videos."""

import os
from urllib.parse import urlparse

try:
    import boto3
except ImportError:
    boto3 = None


def is_s3_uri(path: str) -> bool:
    """Check if path is an S3 URI."""
    return path.startswith("s3://")


def parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    """Parse S3 URI into bucket and key."""
    parsed = urlparse(s3_uri)
    return parsed.netloc, parsed.path.lstrip("/")


def download_from_s3(s3_uri: str, local_path: str) -> None:
    """Download file from S3 to local path."""
    if boto3 is None:
        raise ImportError("boto3 is required for S3 operations")

    bucket, key = parse_s3_uri(s3_uri)
    s3_client = boto3.client("s3")

    print(f"Downloading from S3: {s3_uri}")
    s3_client.download_file(bucket, key, local_path)
    print(f"Downloaded to: {local_path}")


def upload_to_s3(local_path: str, s3_uri: str) -> None:
    """Upload file from local path to S3."""
    if boto3 is None:
        raise ImportError("boto3 is required for S3 operations")

    bucket, key = parse_s3_uri(s3_uri)
    s3_client = boto3.client("s3")

    print(f"Uploading to S3: {s3_uri}")
    s3_client.upload_file(local_path, bucket, key)
    print("Uploaded successfully")


def send_notification(message: str, subject: str = "Video Processing Complete") -> None:
    """Send SNS notification if SNS_TOPIC_ARN is set."""
    sns_topic_arn = os.environ.get("SNS_TOPIC_ARN")
    if not sns_topic_arn:
        return

    if boto3 is None:
        print("Warning: boto3 not available, skipping notification")
        return

    sns_client = boto3.client("sns")
    try:
        sns_client.publish(TopicArn=sns_topic_arn, Subject=subject, Message=message)
        print(f"Notification sent: {subject}")
    except Exception as e:
        print(f"Failed to send notification: {e}")
