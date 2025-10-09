import os
import subprocess
from github import Github, Auth

from constants import GIHUB_SECRET_ARN
from utils import get_github_personal_access_token

def run_cmd(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {result}")
    return result.stdout.strip()

def get_repo_path(project_name: str) -> str:
    return f"/tmp/{project_name}"

def clean_tmp_directory(project_name: str):
    repo_path = get_repo_path(project_name)
    if not os.path.exists(repo_path):
        print(f"⚠️ Repo path does not exist: {repo_path}")
        return

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".bak"):
                full_path = os.path.join(root, file)
                os.remove(full_path)
                print(f"🧹 Deleted backup file: {full_path}")

def get_pr_body(story_id: str, project_name: str) -> str:
    pr_md_file = os.path.join(get_repo_path(project_name), f"{story_id}.md")
    if os.path.exists(pr_md_file):
        with open(pr_md_file, "r", encoding="utf-8") as f:
            pr_body = f.read().strip()
        os.remove(pr_md_file)
        print(f"🧹 Deleted PR markdown file: {pr_md_file}")
        return pr_body
    return f"This PR was generated automatically for `{story_id}`."

def commit_and_push(repo_url: str, project_name: str, story_id: str):
    repo_path = get_repo_path(project_name)
    new_branch = f"feature/{story_id}"

    run_cmd(["git", "config", "user.email", "nemo-ai@example.com"], cwd=repo_path)
    run_cmd(["git", "config", "user.name", "nemo-ai"], cwd=repo_path)

    run_cmd(["git", "checkout", "-b", new_branch], cwd=repo_path)
    run_cmd(["git", "add", "."], cwd=repo_path)
    run_cmd(["git", "commit", "-m", f"{story_id}: automated changes"], cwd=repo_path)

    # Push with token
    secret_arn = GIHUB_SECRET_ARN.format(aws_account_id=os.getenv('AWS_ACCOUNT_ID'))
    personal_access_token = get_github_personal_access_token(secret_arn=secret_arn)

    remote_url_with_token = f"https://{personal_access_token}@{repo_url.split('https://')[1]}"
    run_cmd(["git", "remote", "set-url", "origin", remote_url_with_token], cwd=repo_path)
    run_cmd(["git", "push", "-u", "origin", new_branch], cwd=repo_path)

    return new_branch

def create_pr(repo_url: str, pr_body: str, story_id: str, base_branch="main"):

    secret_arn = GIHUB_SECRET_ARN.format(aws_account_id=os.getenv('AWS_ACCOUNT_ID'))
    personal_access_token = get_github_personal_access_token(secret_arn=secret_arn)

    auth = Auth.Token(personal_access_token)
    g = Github(auth=auth)

    repo_name = repo_url.split("github.com/")[-1].replace(".git", "")
    repo = g.get_repo(repo_name)
    new_branch = f"feature/{story_id}"
    pr_title = f"[{story_id}] - Nemo AI"

    pr = repo.create_pull(
        title=pr_title,
        body=pr_body,
        head=new_branch,
        base=base_branch,
    )
    print(f"✅ PR created: {pr.html_url}")
    return pr.html_url

def pull_request_workflow(project_name: str, repo_url: str, story_id: str):

    # Clean backup files first
    clean_tmp_directory(project_name)

    # get pr_body and delete the file before committing the changes
    pr_body = get_pr_body(story_id, project_name)

    # Commit and Push new branch
    commit_and_push(repo_url=repo_url, project_name=project_name, story_id=story_id)

    # Create PR
    pr_url = create_pr(repo_url=repo_url, pr_body=pr_body, story_id=story_id)

    return {
        "statusCode": 200,
        "body": f"✅ Pull request created: {pr_url}"
    }