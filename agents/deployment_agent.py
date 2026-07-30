import subprocess
from agents import kubernetes

def deploy_app(deployment_name: str, container_name: str, image_tag: str, namespace: str = "default") -> dict:
    """Manages the rollout and checks deployment status."""
    result = kubernetes.update_deployment_image(deployment_name, container_name, image_tag, namespace)
    if not result["success"]:
        return result

    # Check rollout status
    try:
        subprocess.run(
            ["kubectl", "rollout", "status", f"deployment/{deployment_name}", "-n", namespace, "--timeout=60s"],
            check=True
        )
        return {"success": True, "message": "Rollout completed successfully."}
    except subprocess.CalledProcessError:
        return {"success": False, "message": "Rollout timed out or failed."}
