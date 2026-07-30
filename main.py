import os
import sys
import logging
from typing import Dict, Any

# Ensure environmental variables are accessible
from dotenv import load_dotenv
load_dotenv()

# Import all 8 agents from the agents package
from agents import (
    git,
    code_review,
    testing_agent,
    docker,
    deployment_agent,
    kubernetes,
    monitoring_agent,
    rollback_agent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DevOpsPipeline")

# Configuration Constants
REPO_URL = os.getenv("REPO_URL", "https://github.com/your-org/sample-app.git/")
BRANCH = os.getenv("BRANCH_NAME", "main")
IMAGE_NAME = os.getenv("DOCKER_IMAGE", "your-registry/sample-app")
DEPLOYMENT_NAME = os.getenv("K8S_DEPLOYMENT", "sample-app-deployment")
CONTAINER_NAME = os.getenv("K8S_CONTAINER", "sample-app")
NAMESPACE = os.getenv("K8S_NAMESPACE", "default")
HEALTH_CHECK_URL = os.getenv("APP_HEALTH_URL", "http://localhost:8080/health")


def run_pipeline():
    logger.info("==========================================")
    logger.info("  STARTING AI-DRIVEN DEVOPS PIPELINE      ")
    logger.info("==========================================")

    # --------------------------------------------------
    # Phase 1: Git Operations
    # --------------------------------------------------
    logger.info("[PHASE 1] Fetching repository and retrieving diff...")
    git_res: Dict[str, Any] = git.clone_or_pull(repo_url=REPO_URL, branch=BRANCH)
    if git_res.get("status") != "success":
        logger.error(f"Pipeline Aborted at Git Phase: {git_res.get('message')}")
        sys.exit(1)

    repo_path = git_res["repo_path"]
    diff_text = git_res.get("diff", "")
    logger.info(f"Successfully checked out repository at: {repo_path}")

    # --------------------------------------------------
    # Phase 2: AI Code Review (Gemini / LLM)
    # --------------------------------------------------
    logger.info("[PHASE 2] Running AI Code Review on latest diff...")
    review_res: Dict[str, Any] = code_review.analyze_changes(diff_text=diff_text)
    
    if not review_res.get("passed", False):
        logger.error("Pipeline Aborted: AI Code Review failed!")
        logger.error(f"Review Details:\n{review_res.get('reason')}")
        sys.exit(1)
    
    logger.info("AI Code Review passed successfully.")

    # --------------------------------------------------
    # Phase 3: Automated Testing
    # --------------------------------------------------
    logger.info("[PHASE 3] Running automated unit/integration tests...")
    test_res: Dict[str, Any] = testing_agent.run_tests(repo_path=repo_path)
    if not test_res.get("success", False):
        logger.error("Pipeline Aborted: Test suite execution failed!")
        logger.error(f"Test Errors:\n{test_res.get('errors')}")
        sys.exit(1)

    logger.info("All tests passed.")

    # --------------------------------------------------
    # Phase 4: Containerization (Docker Build & Push)
    # --------------------------------------------------
    # Use git short hash or timestamp as image tag
    commit_tag = "latest"
    logger.info(f"[PHASE 4] Building and pushing Docker image: {IMAGE_NAME}:{commit_tag}...")
    docker_res: Dict[str, Any] = docker.build_and_push(
        image_name=IMAGE_NAME,
        tag=commit_tag,
        build_context=repo_path
    )
    if not docker_res.get("success", False):
        logger.error(f"Pipeline Aborted: Docker build/push failed. Error: {docker_res.get('error')}")
        sys.exit(1)

    full_image_tag = docker_res["image"]
    logger.info(f"Successfully pushed image: {full_image_tag}")

    # --------------------------------------------------
    # Phase 5: Kubernetes Deployment Strategy
    # --------------------------------------------------
    logger.info(f"[PHASE 5] Triggering Kubernetes rollout for {DEPLOYMENT_NAME}...")
    
    # Note: deployment_agent calls kubernetes.py under the hood
    deploy_res: Dict[str, Any] = deployment_agent.deploy_app(
        deployment_name=DEPLOYMENT_NAME,
        container_name=CONTAINER_NAME,
        image_tag=full_image_tag,
        namespace=NAMESPACE
    )
    if not deploy_res.get("success", False):
        logger.error(f"Deployment rollout failed! {deploy_res.get('message')}")
        logger.warning("Initiating immediate safety rollback...")
        rollback_agent.rollback_deployment(deployment_name=DEPLOYMENT_NAME, namespace=NAMESPACE)
        sys.exit(1)

    logger.info("Kubernetes rollout successful.")

    # --------------------------------------------------
    # Phase 6: Post-Deployment Monitoring & Health Check
    # --------------------------------------------------
    logger.info(f"[PHASE 6] Running post-deployment health checks on {HEALTH_CHECK_URL}...")
    health_res: Dict[str, Any] = monitoring_agent.check_health(
        endpoint_url=HEALTH_CHECK_URL,
        retries=5,
        delay=5
    )

    if not health_res.get("healthy", False):
        logger.error("Health check failed! App is unreachable or returning errors post-deployment.")
        logger.warning(f"Initiating automatic rollback for {DEPLOYMENT_NAME}...")
        
        # --------------------------------------------------
        # Phase 7: Rollback Execution (Safety Triggered)
        # --------------------------------------------------
        rollback_res: Dict[str, Any] = rollback_agent.rollback_deployment(
            deployment_name=DEPLOYMENT_NAME,
            namespace=NAMESPACE
        )
        if rollback_res.get("success", False):
            logger.info("Rollback completed successfully. Previous stable version restored.")
        else:
            logger.critical(f"Rollback failed! Intervention required. Error: {rollback_res.get('error')}")
        
        sys.exit(1)

    logger.info("==========================================")
    logger.info("  PIPELINE EXECUTED SUCCESSFULLY!         ")
    logger.info("==========================================")


if __name__ == "__main__":
    run_pipeline()
