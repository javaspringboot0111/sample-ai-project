import os
from google import genai
from google.genai import types

# Initialize client (automatically picks up GEMINI_API_KEY env variable)
client = genai.Client()

SYSTEM_PROMPT = """
You are an expert DevOps and Security Code Reviewer.
Your task is to analyze git diffs for:
1. Hardcoded secrets, API keys, or credentials.
2. Critical security vulnerabilities (SQL injection, unsafe inputs, XSS, etc.).
3. Syntax errors, memory leaks, or broken logic.

Format your response exactly as follows:
STATUS: [PASSED or FAILED]
REASON: <Provide a concise summary if PASSED, or a bulleted list of issues if FAILED.>
"""

def analyze_changes(diff_text: str, model: str = "gemini-3.6-flash") -> dict:
    """Analyzes a git diff using Google Gemini API."""
    if not diff_text.strip():
        return {"passed": True, "reason": "No code changes detected to review."}

    try:
        response = client.models.generate_content(
            model=model,
            contents=f"Review this git diff:\n\n{diff_text}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,  # Low temperature for deterministic evaluation
            ),
        )

        content = response.text.strip()
        
        # Check if the output starts with or contains STATUS: PASSED
        is_passed = "STATUS: PASSED" in content or content.startswith("PASSED")

        return {
            "passed": is_passed,
            "reason": content
        }

    except Exception as e:
        return {
            "passed": False,
            "reason": f"Gemini Code Review Failed due to API Error: {str(e)}"
        }
