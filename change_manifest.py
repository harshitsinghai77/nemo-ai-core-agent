import subprocess
import re
import os
import json
from typing import List, Dict, Any, Optional

def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> str:
    """Run a shell command inside the given cwd and return stdout."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()

def parse_diff(diff_text: str, change_type: str, project_name: str) -> List[Dict[str, Any]]:
    changes: List[Dict[str, Any]] = []
    current_file: Optional[str] = None

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("@@") and current_file:
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start_line = int(match.group(1))
                length = int(match.group(2) or 1)
                end_line = start_line + length - 1
                changes.append({
                    "file_path": f"/tmp/{project_name}/{current_file}",
                    "change_type": change_type,
                    "mode": "lines",
                    "start_line": start_line,
                    "end_line": end_line
                })
    return changes


def get_untracked_files(cwd: str, project_name: str) -> List[Dict[str, Any]]:
    out = run_cmd(["git", "ls-files", "--others", "--exclude-standard"], cwd=cwd)
    files = out.splitlines() if out else []
    entries: List[Dict[str, Any]] = []

    for f in files:
        abs_path = os.path.join(cwd, f)
        if os.path.isfile(abs_path):
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as fh:
                    num_lines = sum(1 for _ in fh)
            except Exception:
                num_lines = 0

            entries.append({
                "file_path": f"/tmp/{project_name}/{f}",
                "change_type": "untracked_file",
                "mode": "full",
                "start_line": 1,
                "end_line": num_lines
            })
    return entries



def get_manifest(project_name: str, py_only: bool = True) -> Dict[str, Any]:
    repo_path = os.path.join("/tmp", project_name)
    manifest: Dict[str, Any] = {"changes": []}

    # Gather diffs and untracked files
    manifest["changes"].extend(
        parse_diff(run_cmd(["git", "diff", "--unified=0"], cwd=repo_path), "modified_file", project_name)
    )
    manifest["changes"].extend(
        parse_diff(run_cmd(["git", "diff", "--cached", "--unified=0"], cwd=repo_path), "staged_new_file", project_name)
    )
    manifest["changes"].extend(
        get_untracked_files(cwd=repo_path, project_name=project_name)
    )

    # Optionally filter only Python files
    if py_only:
        manifest["changes"] = [
            c for c in manifest["changes"] if c["file_path"].endswith(".py")
        ]

    return manifest
