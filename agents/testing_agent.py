import subprocess

def run_tests(repo_path: str) -> dict:
    """Executes test suites (e.g., pytest) in the repository."""
    try:
        result = subprocess.run(
            ["pytest", repo_path],
            capture_output=True,
            text=True
        )
        # pytest returncode 5 means "No tests were found", which we can treat as non-fatal if desired
        success = (result.returncode == 0 or result.returncode == 5)

        return {
            "success": success,
            "output": result.stdout,
            "errors": result.stderr if result.returncode != 0 else ""
        }
    except Exception as e:
        return {"success": False, "errors": str(e)}
