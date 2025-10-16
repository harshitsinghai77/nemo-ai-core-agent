import os
import logging
import traceback
import asyncio

import boto3
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel

# from run_workflow import run_nemo_agent_workflow

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_ecs_task():
    
    github_link = os.getenv("GITHUB_LINK")
    jira_story = os.getenv("JIRA_STORY")
    jira_story_id = os.getenv("JIRA_STORY_ID")
    is_data_analysis_task = os.getenv("IS_DATA_ANALYSIS_TASK")

    if not all([github_link, jira_story, jira_story_id, is_data_analysis_task]):
        logger.error("Missing required environment variables.")
        logger.info(f"GITHUB_LINK: {github_link}")
        logger.info(f"JIRA_STORY: {jira_story}")
        logger.info(f"JIRA_STORY_ID: {jira_story_id}")
        logger.info(f"IS_DATA_ANALYSIS_TASK: {is_data_analysis_task}")
        exit(1)
    
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

    try:
        is_data_analysis_task = str(is_data_analysis_task).lower() == "true"
        # output = asyncio.run(run_nemo_agent_workflow(github_link=github_link, jira_story=jira_story, jira_story_id=jira_story_id, is_data_analysis_task=is_data_analysis_task))
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
        rodeos, and museums at Rome Vienna and Austria. Use web search to find current information about venues, 
        events, and attractions."""

        result = travel_agent(query)
        print("Result:", result)

        logger.info(f"✅ Workflow result: {result}")
        # logger.info(f"✅ Workflow result: {output}")
        logger.info("✅ ECS Task completed successfully.")
        exit(0)

    except Exception as e:
        logger.error(f"❌ Error during ECS task: {str(e)}")
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    start_ecs_task()