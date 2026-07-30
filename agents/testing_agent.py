import subprocess

def run_tests(repo_path: str) -> dict:
    """Executes test suites (e.g., pytest) in the repository."""
    try:
        result = subprocess.run(
            ["pytest", repo_path],
            capture_output=True,
            text=True
        )
        success = (result.returncode == 0)
        return {
            "success": success,
            "output": result.stdout,
            "errors": result.stderr
        }
    except Exception as e:
        return {"success": False, "errors": str(e)}
