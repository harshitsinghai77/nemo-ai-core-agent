import os
import json
from urllib.parse import urlparse

import requests
import boto3
import logging

logger = logging.getLogger(__name__)

secrets_manager_client = boto3.client('secretsmanager', region_name='us-east-1')

def parse_github_url(github_url: str):
    """
    Given a GitHub web URL (e.g. https://github.com/user/repo), return:
    - the .git clone URL
    - the project name (repo name)

    Returns:
        (clone_url, project_name)
    """
    # Ensure no trailing slash
    github_url = github_url.rstrip("/")

    # Extract project name from path
    parsed = urlparse(github_url)
    path_parts = parsed.path.strip("/").split("/")
    
    if len(path_parts) != 2:
        raise ValueError("Invalid GitHub URL format. Expected: https://github.com/user/repo")

    project_name = path_parts[-1]
    clone_url = f"{github_url}.git" if not github_url.endswith(".git") else github_url

    return clone_url, project_name

def get_github_personal_access_token(secret_arn: str) -> str:
    """Fetch a secret from AWS Secrets Manager using its ARN."""
    try:
        response = secrets_manager_client.get_secret_value(SecretId=secret_arn)
        secret_str = response.get('SecretString')

        if not secret_str:
            raise ValueError("SecretString not found in secret.")

        secret_dict = json.loads(secret_str)

        token = secret_dict.get('token')
        if not token:
            raise ValueError("'token' key not found in secret.")

        return token
    except Exception as e:
        print(f"[ERROR] Could not retrieve GitHub PAT: {e}")
        raise

def set_otel_exporter_otlp_log_headers(log_group_name: str, log_stream_name: str, metric_namespace: str = 'nemo-ai-core-agent-lambda'):
    """Set OTEL_EXPORTER_OTLP_LOGS_HEADERS environment variable."""
    otel_log_headers = (
        f"x-aws-log-group={log_group_name},"
        f"x-aws-log-stream={log_stream_name},"
        f"x-aws-metric-namespace={metric_namespace}"
    )
    os.environ["OTEL_EXPORTER_OTLP_LOGS_HEADERS"] = otel_log_headers

def set_otel_exporter_otlp_log_headers_for_ecs(metric_namespace: str = 'nemo-ai-core-agent-ecs'):
    """Set OTEL_EXPORTER_OTLP_LOGS_HEADERS environment variable for ECS Fargate."""

    metadata_uri = os.getenv("ECS_CONTAINER_METADATA_URI_V4")
    if not metadata_uri:
        raise ValueError("ECS_CONTAINER_METADATA_URI_V4 environment variable not set.")
    
    resp = requests.get(f'{metadata_uri}/task')
    resp.raise_for_status()
    data = resp.json()
    print("==>> resp: ", resp)
    logger.info(f"==>> data: {str(data)}")
    task_arn = data['TaskARN']
    task_id = task_arn.split('/')[-1]

    container = data['Containers'][0]
    container_name = container['Name']
    log_options = container['LogOptions']
    log_group = log_options.get('awslogs-group', '/ecs/nemo-ai-container')
    # stream_prefix = log_options['awslogs-stream-prefix']
    log_stream_name = f"nemo-ai-ecs/{container_name}/{task_id}"
    logger.info(f"Log Stream Name: {log_stream_name}")
    logger.info(f"Log Group Name: {log_group}")
    
    os.environ["OTEL_EXPORTER_OTLP_LOGS_HEADERS"] = f"x-aws-log-group={log_group},x-aws-log-stream={log_stream_name},x-aws-metric-namespace={metric_namespace}"
