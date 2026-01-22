import os
from groq import Groq
from dotenv import load_dotenv

# HARD ISOLATION
load_dotenv()

def get_groq_client():
    """
    Returns a clean Groq client instance.
    This function MUST be the only place Groq is instantiated.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    return Groq(api_key=api_key)
