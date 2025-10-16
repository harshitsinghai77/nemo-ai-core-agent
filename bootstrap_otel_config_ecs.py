import os
import requests
import logging

logger = logging.getLogger(__name__)

def set_otel_exporter_otlp_log_headers_for_ecs(metric_namespace: str = 'nemo-ai-core-agent-ecs'):
    """Set OTEL_EXPORTER_OTLP_LOGS_HEADERS environment variable for ECS Fargate."""

    metadata_uri = os.getenv("ECS_CONTAINER_METADATA_URI_V4")
    if not metadata_uri:
        raise ValueError("ECS_CONTAINER_METADATA_URI_V4 environment variable not set.")
    
    resp = requests.get(f'{metadata_uri}/task')
    resp.raise_for_status()
    data = resp.json()
    log_group = data['Containers'][0]['LogOptions']['awslogs-group']
    log_stream = data['Containers'][0]['LogOptions']['awslogs-stream']
    # os.environ["OTEL_EXPORTER_OTLP_LOGS_HEADERS"] = f"x-aws-log-group={log_group},x-aws-log-stream={log_stream},x-aws-metric-namespace={metric_namespace}"
    # logger.info(f"OTEL_EXPORTER_OTLP_LOGS_HEADERS set to: {os.getenv('OTEL_EXPORTER_OTLP_LOGS_HEADERS')}")
    return f"x-aws-log-group={log_group},x-aws-log-stream={log_stream},x-aws-metric-namespace={metric_namespace}"

if __name__ == "__main__":
    print(set_otel_exporter_otlp_log_headers_for_ecs())