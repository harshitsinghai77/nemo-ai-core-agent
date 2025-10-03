import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

from utils import parse_github_url
from clone_repo import clone_github_repo, validate_cloned_repo
from workflow import nemo_workflow
from create_pr import pull_request_workflow


def lambda_handler(event, context):
    # Get the JIRA story description from the event body
    
    if "Records" not in event:
        return {
            "statusCode": 400,
            "body": "No records found in the event payload."
        }
    
    required_fields = ["github_link", "jira_story", "jira_story_id"]
    for record in event["Records"]:
        try:
            payload = json.loads(record["body"])
            print("payload", payload)

            required_fields = ["github_link", "jira_story", "jira_story_id"]
            if not all(field in payload for field in required_fields):
                missing = [field for field in required_fields if field not in payload]
                print(f"⚠️ Skipping message: missing fields: {missing} {str(record)}")
                continue  # Skip this message but continue processing others
            
            github_link, jira_story, jira_story_id = payload["github_link"], payload['jira_story'], payload['jira_story_id']

            # Extract clone URL and repo name
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

            return {
                "statusCode": 200,
                "body": "Workflow complete."
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "body": f"Error running workflow: {str(e)}"
            }
        
    return {
        "statusCode": 204,
        "body": "No valid messages processed."
    }

  
if __name__ == "__main__":
    dummy_event = {
        "detail": {
            "github_link": "https://github.com/harshitsinghai77/nemo-ai-demo-1",
            "jira_story": "Create a new route inside the agentRoutes.py which takes two numbers from the query parameter and return the sum of it in JSON format, with keys like num1, num2, total",
            "jira_story_id": "FIN-1024"
        }
    }
    response = lambda_handler(dummy_event, context=None)

    print("=== Lambda Response ===")
    print(response)