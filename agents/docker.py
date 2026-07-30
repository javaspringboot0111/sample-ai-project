import subprocess

def build_and_push(image_name: str, tag: str, build_context: str = "./repo") -> dict:
    """Builds a Docker image and pushes it to a container registry."""
    full_image_name = f"{image_name}:{tag}"
    try:
        # Build image
        subprocess.run(["docker", "build", "-t", full_image_name, build_context], check=True)
        # Push image
        subprocess.run(["docker", "push", full_image_name], check=True)
        
        return {"success": True, "image": full_image_name}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e)}
