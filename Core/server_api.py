# ============================================================
# server_api.py
# ============================================================
# Raw Groq REST client for argument extraction.
#
# This bypasses ALL SDKs to avoid proxy poisoning.
#
# RULES:
# - No orchestration logic
# - No retries
# - No DB access
# - No prompt reasoning
# ============================================================

import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-120b"
TIMEOUT = 30

# ============================================================
# ARGUMENT EXTRACTION
# ============================================================

def extract_arguments(
    prompt: str,
    function_name: str,
    schema: dict,
    tokenized_prompt: list | None = None
) -> dict:
    """
    Extract structured arguments for a command using Groq LLM.

    This function:
    - Sends a raw REST request
    - Expects VALID JSON only in response
    - Raises on any malformed or failed response
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    model = os.getenv("GROQ_ARGUMENT_MODEL", DEFAULT_MODEL)

    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an argument extraction engine.\n"
                    "Rules:\n"
                    "- Extract ONLY arguments explicitly stated.\n"
                    "- Do NOT invent values.\n"
                    "- If missing, omit.\n"
                    "- Output VALID JSON only."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Command: {function_name}\n"
                    f"User input: {prompt}\n"
                    f"Schema: {json.dumps(schema)}\n"
                    f"Tokens: {tokenized_prompt}"
                )
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        GROQ_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Groq API error {response.status_code}: {response.text}"
        )

    data = response.json()

    try:
        choices = data.get("choices")
        if not choices:
            raise KeyError("Missing choices in response")

        content = choices[0]["message"]["content"]
        return json.loads(content)

    except Exception as e:
        raise RuntimeError(
            f"Invalid Groq response format: {data}"
        ) from e
