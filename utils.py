from urllib.parse import urlparse

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
