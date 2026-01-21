# Core/command_contract.py
from datetime import datetime


def command_result(
        status: str,
        message: str,
        data: dict = None,
        error: dict = None,
        effects: list = None,
        timestamp: str = None
) -> dict:
    """
    Standardized return schema for all Shell functions.

    Args:
        status (str): 'success' or 'error'
        message (str): Human readable description
        data (dict): Result payload (optional)
        error (dict): Error details (optional)
        effects (list): System changes made (optional)
        timestamp (str): ISO format time (optional, defaults to now)
    """
    return {
        "status": status,
        "message": message,
        "data": data,
        "error": error,
        "effects": effects or [],
        "timestamp": timestamp or datetime.now().isoformat()
    }