import subprocess
import os

def clone_or_pull(repo_url: str, repo_dir: str = "./repo", branch: str = "main") -> dict:
    """Clones or pulls the latest code from a git repository."""
    try:
        if os.path.exists(repo_dir):
            subprocess.run(["git", "-C", repo_dir, "checkout", branch], check=True)
            subprocess.run(["git", "-C", repo_dir, "pull"], check=True)
        else:
            subprocess.run(["git", "clone", "-b", branch, repo_url, repo_dir], check=True)
        
        diff = subprocess.check_output(
            ["git", "-C", repo_dir, "diff", "HEAD~1", "HEAD"]
        ).decode("utf-8")
        
        return {"status": "success", "repo_path": repo_dir, "diff": diff}
    except Exception as e:
        return {"status": "error", "message": str(e)}
