# ============================================================
# groq_client.py
# ============================================================
# Centralized Groq client factory for JaiShell.
#
# Responsibilities:
# - Load environment configuration
# - Create and expose a single Groq client instance
#
# RULES:
# - This is the ONLY place Groq may be instantiated
# - No prompt logic
# - No retries or business logic
# ============================================================

import os
from groq import Groq
from dotenv import load_dotenv

# ============================================================
# ENVIRONMENT LOADING
# ============================================================
load_dotenv()

# ============================================================
# LAZY SINGLETON CLIENT
# ============================================================
_client = None

def get_groq_client():
    """
    Return a singleton Groq client instance.

    This function MUST be the only place Groq is instantiated.
    """
    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    _client = Groq(api_key=api_key)
    return _client
