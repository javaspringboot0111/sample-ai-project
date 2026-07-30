import subprocess

def rollback_deployment(deployment_name: str, namespace: str = "default") -> dict:
    """Rolls back the deployment to the previous stable revision."""
    try:
        subprocess.run(
            ["kubectl", "rollout", "undo", f"deployment/{deployment_name}", "-n", namespace],
            check=True
        )
        return {"success": True, "message": f"Successfully rolled back {deployment_name}."}
    except Exception as e:
        return {"success": False, "error": str(e)}
