import subprocess

def update_deployment_image(deployment_name: str, container_name: str, new_image: str, namespace: str = "default") -> dict:
    """Updates a deployment with a new Docker image using kubectl."""
    try:
        cmd = [
            "kubectl", "set", "image",
            f"deployment/{deployment_name}",
            f"{container_name}={new_image}",
            "-n", namespace
        ]
        subprocess.run(cmd, check=True)
        return {"success": True, "message": f"Updated {deployment_name} to {new_image}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
