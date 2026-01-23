# ============================================================
# ChatCore.py
# ============================================================
# Conversational mode handler for JaiShell.
#
# Responsibilities:
# - Handle free-form chat interactions
# - Provide explanations, help, and guidance
# - Integrate future custom chat models and tools
#
# This module does NOT:
# - Execute shell commands
# - Write or read the database
# - Manage sessions
# - Control logging or output
#
# All chat responses MUST conform to command_contract.
# ============================================================

from Core.command_contract import command_result


# ============================================================
# CHAT ENGINE (PLACEHOLDER)
# ============================================================
def chat_engine(prompt: str, context: dict) -> dict:
    """
    Handle chat-mode interactions.

    Args:
        prompt (str): User input
        context (dict): Global session context (read-only)

    Returns:
        dict: command_result-compliant response
    """

    # Defensive checks (never trust caller blindly)
    if not prompt or not isinstance(prompt, str):
        return command_result(
            status="error",
            message="Invalid chat input."
        )

    user_name = context.get("user_name", "User")

    # --------------------------------------------------------
    # PLACEHOLDER RESPONSE LOGIC
    # --------------------------------------------------------
    # This is intentionally simple.
    # Real chat intelligence will be plugged in later.
    # --------------------------------------------------------

    response = (
        f"Hi {user_name}! 👋\n\n"
        "Chat mode is active.\n\n"
        "You can use this mode for:\n"
        "- Asking questions\n"
        "- Getting explanations\n"
        "- Code help\n"
        "- General assistance\n\n"
        "Command execution is disabled in chat mode."
    )

    return command_result(
        status="success",
        message=response,
        confidence=1.0
    )
