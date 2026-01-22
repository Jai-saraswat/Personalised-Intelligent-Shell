# ============================================================
# server_api.py
# ============================================================
# Raw Groq REST client for argument extraction.
# This bypasses ALL SDKs to avoid proxy poisoning.
# ============================================================

import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

TIMEOUT = 30


def extract_arguments(
    prompt: str,
    function_name: str,
    schema: dict,
    tokenized_prompt: list | None = None
) -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    payload = {
        "model": "openai/gpt-oss-120b",
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
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        GROQ_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=TIMEOUT
    )

    if r.status_code != 200:
        raise RuntimeError(f"Groq API error {r.status_code}: {r.text}")

    data = r.json()

    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        raise RuntimeError(f"Invalid Groq response: {data}") from e
