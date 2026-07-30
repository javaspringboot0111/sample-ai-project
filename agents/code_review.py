import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

client = genai.Client()

SYSTEM_PROMPT = """
You are an expert DevOps and Security Code Reviewer.
Analyze git diffs for hardcoded secrets, security vulnerabilities, and syntax errors.

Format response:
STATUS: [PASSED or FAILED]
REASON: <Concise summary or bulleted issues>
"""

def analyze_changes(diff_text: str, model: str = "gemini-3.6-flash", max_retries: int = 3) -> dict:
    """Analyzes git diff with automatic retry on rate limits (429)."""
    if not diff_text.strip():
        return {"passed": True, "reason": "No code changes detected to review."}

    # Truncate diff if it's excessively massive to save input tokens
    MAX_CHARACTERS = 30000
    if len(diff_text) > MAX_CHARACTERS:
        diff_text = diff_text[:MAX_CHARACTERS] + "\n\n[Diff truncated to avoid token quota limits]"

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=f"Review this git diff:\n\n{diff_text}",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                ),
            )

            content = response.text.strip()
            is_passed = "STATUS: PASSED" in content or content.startswith("PASSED")

            return {
                "passed": is_passed,
                "reason": content
            }

        except APIError as e:
            if e.code == 429 and attempt < max_retries:
                wait_time = 45  # Wait 45 seconds as requested by the API error
                print(f"[Rate Limit Hit] Waiting {wait_time}s before retry (Attempt {attempt}/{max_retries})...")
                time.sleep(wait_time)
            else:
                return {
                    "passed": False,
                    "reason": f"Gemini Code Review Failed: {str(e)}"
                }
        except Exception as e:
            return {
                "passed": False,
                "reason": f"Unexpected Error: {str(e)}"
            }
