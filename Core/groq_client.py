# ============================================================
# groq_client.py
# ============================================================
# Centralized Groq REST client for JaiShell.
#
# Responsibilities:
# - Load environment configuration
# - Send RAW HTTP requests to Groq
# - Expose minimal, safe chat completion API
#
# RULES:
# - NO Groq Python SDK
# - NO retries
# - NO orchestration logic
# ============================================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")
TIMEOUT = 30


# ============================================================
# CHAT COMPLETION
# ============================================================

def chat_complete(
    *,
    messages: list,
    temperature: float = 0.2,
    top_p: float = 0.9,
    max_tokens: int = 800
) -> str:
    """
    Perform a chat completion via Groq (RAW REST).

    Args:
        messages (list): OpenAI-style message list
        temperature (float)
        top_p (float)
        max_tokens (int)

    Returns:
        str: Assistant response text
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        GROQ_ENDPOINT,
        json=payload,
        headers=headers,
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Groq API error {response.status_code}: {response.text}"
        )

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        raise RuntimeError(f"Invalid Groq response format: {data}")
