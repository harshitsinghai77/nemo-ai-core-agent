import os
import shutil
import subprocess
from constants import GITHUB_PERSONAL_ACCESS_TOKEN

def run_cmd(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {result}")
    return result.stdout.strip()

def clone_github_repo(repo_url: str, project_name: str, base_branch: str = "main") -> str:
    """
    Clone the given GitHub repo into /tmp/{project_name}, checkout base branch, and pull latest code.

    Returns:
        The local path to the cloned repository.
    """
    local_path = f"/tmp/{project_name}"

    # Clean old repo if exists
    if os.path.exists(local_path):
        print(f"Cleaning old repo at {local_path}...")
        shutil.rmtree(local_path)

    # Clone fresh
    remote_url_with_token = f"https://{GITHUB_PERSONAL_ACCESS_TOKEN}@{repo_url.split('https://')[1]}"
    run_cmd(["git", "clone", remote_url_with_token, local_path])
    run_cmd(["git", "checkout", base_branch], cwd=local_path)
    run_cmd(["git", "pull", "origin", base_branch], cwd=local_path)

    return local_path

def validate_cloned_repo(project_name: str):
    local_path = f"/tmp/{project_name}"

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Cloning failed. Directory {local_path} does not exist.")

    has_files = any(os.scandir(local_path))
    if not has_files:
        raise RuntimeError(f"Repo exists at {local_path}, but it is empty.")

    print(f"✅ Repo at {local_path} exists and contains files.")
    return True

if __name__ == "__main__":
    clone_github_repo(repo_url='https://github.com/Deloitte-US-Consulting/nemo-ai-example-app-3', project_name='nemo-ai-example-app-3')