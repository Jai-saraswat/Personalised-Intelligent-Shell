# ============================================================
# command_contract.py
# ============================================================
# Standard return contract for all JaiShell commands.
#
# This file defines the ONLY allowed shape for command results.
# CoreShell depends on this structure to:
#   - Render output
#   - Log executions
#   - Handle actions (exit, clear screen)
#
# Commands must NEVER return arbitrary dicts.
# ============================================================

from datetime import datetime

# ============================================================
# RESULT FACTORY
# ============================================================
def command_result(
    status: str,
    message: str,
    data: dict = None
) -> dict:
    """
    Create a standardized command result.

    Args:
        status (str): 'success' or 'error'
        message (str): Human-readable output
        data (dict): Optional payload, may include:
            - action: 'exit', 'clear_screen', etc.
            - content: list or value for display

    Returns:
        dict: Standardized result object
    """
    if status not in ("success", "error"):
        raise ValueError("status must be 'success' or 'error'")

    return {
        "status": status,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }
