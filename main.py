from dotenv import load_dotenv
load_dotenv()
import os
otel_vars = [
    "OTEL_PYTHON_DISTRO",
    "OTEL_PYTHON_CONFIGURATOR",
    "OTEL_EXPORTER_OTLP_PROTOCOL",
    "OTEL_EXPORTER_OTLP_LOGS_HEADERS",
    "OTEL_RESOURCE_ATTRIBUTES",
    "AGENT_OBSERVABILITY_ENABLED",
    "OTEL_TRACES_EXPORTER"
]

print("OpenTelemetry Configuration:")
for var in otel_vars:
    value = os.getenv(var)
    if value:
        print(f"{var}={value}")

from utils import set_otel_exporter_otlp_log_headers

import os
import json
import asyncio

from strands import Agent, tool
from strands.models import BedrockModel
import boto3

# from run_workflow import run_nemo_agent_workflow

def lambda_handler(event, context):

    if context.log_group_name and context.log_stream_name:
        set_otel_exporter_otlp_log_headers(log_group_name=context.log_group_name, log_stream_name=context.log_stream_name)

    # Get the JIRA story description from the event body
    if "Records" not in event:
        return {
            "statusCode": 200,
            "body": "No records found in the event payload."
        }
    
    required_fields = ["github_link", "jira_story", "jira_story_id", "is_data_analysis_task"]
    for record in event["Records"]:
        try:
            payload = json.loads(record["body"])
            print("payload", payload)

            if not all(field in payload for field in required_fields):
                missing = [field for field in required_fields if field not in payload]
                print(f"⚠️ Skipping message: missing fields: {missing} {str(record)}")
                continue  # Skip this message but continue processing others
            
            # output = asyncio.run(run_nemo_agent_workflow(
            #     github_link=payload["github_link"],
            #     jira_story=payload["jira_story"],
            #     jira_story_id=payload["jira_story_id"],
            #     is_data_analysis_task=payload['is_data_analysis_task']
            # ))

            session = boto3.Session()
            bedrock_nova_pro_model = BedrockModel(
                model_id='us.amazon.nova-pro-v1:0',
                boto_session=session,
            )

            travel_agent = Agent(
                model=bedrock_nova_pro_model,
                system_prompt="""You are an experienced travel agent specializing in personalized travel recommendations 
                with access to real-time web information. You should provide comprehensive recommendations with current 
                information, brief descriptions, and practical travel details.""",
            )

            # Execute the travel research task
            query = """Research and recommend suitable travel destinations for someone looking for cowboy vibes, 
            rodeos, and museums in New York city. Use web search to find current information about venues, 
            events, and attractions."""

            result = travel_agent(query)
            print("Result:", result)

            print(f"✅ Lambda workflow complete: {result}")
            # print(f"✅ Lambda workflow complete: {output}")

            return {"statusCode": 200, "body": "Workflow complete."}

        except Exception as e:
            print(f"❌ Error processing record: {str(e)}")
        
    return {
        "statusCode": 200,
        "body": "Lambda executed. All messages processed."
    }

if __name__ == "__main__":
    payload = {
        'Records': [
            {
                'body': json.dumps({
                    "github_link": "https://github.com/harshitsinghai77/nemo-ai-demo-1",
                    "jira_story": "Create a new route inside the agentRoutes.py which takes two numbers from the query parameter and return the sum of it in JSON format, with keys like num1, num2, total",
                    "jira_story_id": "FIN-1024",
                    "is_data_analysis_task": False
                })
            }
        ]}
    response = lambda_handler(payload, context=None)
    print("=== Lambda Response ===")
    print(response)