import os
from dotenv import load_dotenv
import traceback
import asyncio

load_dotenv()

from run_workflow import run_nemo_agent_workflow

def start_ecs_task():
    
    github_link = os.getenv("GITHUB_LINK")
    jira_story = os.getenv("JIRA_STORY")
    jira_story_id = os.getenv("JIRA_STORY_ID")
    is_data_analysis_task = os.getenv("IS_DATA_ANALYSIS_TASK") == "True"

    if not all([github_link, jira_story, jira_story_id]):
        print("Missing required environment variables.")
        exit(1)
    
    try:
        output = asyncio.run(run_nemo_agent_workflow(github_link=github_link, jira_story=jira_story, jira_story_id=jira_story_id, is_data_analysis_task=is_data_analysis_task))
        print(f"✅ Workflow result: {output}")
        print("✅ ECS Task completed successfully.")
        exit(0)

    except Exception as e:
        print(f"❌ Error during ECS task: {str(e)}")
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    start_ecs_task()