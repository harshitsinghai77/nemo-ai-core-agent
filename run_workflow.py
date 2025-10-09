import logging

from utils import parse_github_url
from clone_repo import clone_github_repo, validate_cloned_repo
from workflow import nemo_workflow
from data_analyst_workflow import data_analyst_workflow
from create_pr import GitHubPRManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_nemo_agent_workflow(github_link: str, jira_story: str, jira_story_id: str, is_data_analysis_task: bool) -> dict:
    """
    Runs the full AI agentic workflow: clone → run agent → create PR.
    Returns a dictionary with result and PR status.
    Raises Exception if any step fails.
    """
    # Extract repo details
    clone_url, project_name = parse_github_url(github_link)

    # Clone and validate
    clone_github_repo(repo_url=clone_url, project_name=project_name)
    validate_cloned_repo(project_name=project_name)

    # Run AI workflow
    if is_data_analysis_task:
        logger.info("Running data analyst workflow.")
        result = await data_analyst_workflow(
            project_name=project_name,
            jira_story=jira_story,
            jira_story_id=jira_story_id
        )
    else:
        logger.info("Running nemo workflow.")
        result = await nemo_workflow(
            project_name=project_name,
            jira_story=jira_story,
            jira_story_id=jira_story_id
        )

    # Create PR
    github_manager = GitHubPRManager(
        project_name=project_name,
        repo_url=clone_url,
        story_id=jira_story_id
    )
    pr_status = github_manager.run_pull_request_workflow()
    return {
        "result": result,
        "pr_status": pr_status
    }
