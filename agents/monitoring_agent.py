import urllib.request
import time

def check_health(endpoint_url: str, retries: int = 5, delay: int = 5) -> dict:
    """Polls an endpoint to verify the service is running correctly."""
    for attempt in range(retries):
        try:
            response = urllib.request.urlopen(endpoint_url, timeout=5)
            if response.status == 200:
                return {"healthy": True, "status_code": 200}
        except Exception:
            time.sleep(delay)
            
    return {"healthy": False, "message": "Health checks failed after multiple retries."}
