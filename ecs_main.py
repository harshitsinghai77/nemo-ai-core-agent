import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from utils import parse_github_url
from clone_repo import clone_github_repo, validate_cloned_repo
from workflow import nemo_workflow
from create_pr import pull_request_workflow


def start_ecs_task():
    
    github_link = os.getenv("GITHUB_LINK")
    jira_story = os.getenv("JIRA_STORY")
    jira_story_id = os.getenv("JIRA_STORY_ID")

    if not all([github_link, jira_story, jira_story_id]):
        print("Missing required environment variables.")
        exit(1)
    
    try:
        
        clone_url, project_name = parse_github_url(github_link)

        # Clone and validate repo
        clone_github_repo(repo_url=clone_url, project_name=project_name)
        validate_cloned_repo(project_name=project_name)

        # Run agentic AI workflow
        result = asyncio.run(nemo_workflow(
            project_name=project_name,
            jira_story=jira_story,
            jira_story_id=jira_story_id
        ))
        print(f"==>> result: {result}")

        # Create a PR
        pr_status = pull_request_workflow(
            project_name=project_name,
            repo_url=clone_url,
            story_id=jira_story_id
        )
        print(f"==>> pr_status: {pr_status}")

        print("Workflow completed successfully.")
        print("ECS Task completed successfully.")
        exit(0)

    except Exception as e:
        print(f"Error during ECS batch job: {str(e)}")
        exit(1)

if __name__ == "__main__":
    start_ecs_task()