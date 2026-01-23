# ============================================================
# ContextManager.py
# ============================================================
# In-memory context lifecycle manager for JaiShell.
#
# Responsibilities:
# - Create and maintain session context
# - Track turn progression
# - Hold lightweight cross-mode memory
# - Serialize context snapshots for persistence
#
# This module does NOT:
# - Read or write the database
# - Execute commands
# - Call AI or Chat engines
# ============================================================

from datetime import datetime
from typing import Dict, Any


# ============================================================
# CONTEXT CREATION
# ============================================================
def create_context(
    session_id: int,
    user_name: str,
    initial_mode: str = "rule"
) -> Dict[str, Any]:
    """
    Create a fresh session context.

    Args:
        session_id (int): Unique session identifier
        user_name (str): Display name of the user
        initial_mode (str): Starting mode ('rule' | 'ai' | 'chat')

    Returns:
        dict: Initialized context object
    """
    return {
        "session_id": session_id,
        "user_name": user_name,
        "mode": initial_mode,
        "start_time": datetime.now().isoformat(),
        "turn_id": 0,
        "memory": {
            "short_term": [],
            "last_command": None,
            "flags": {}
        }
    }


# ============================================================
# TURN MANAGEMENT
# ============================================================
def next_turn(context: Dict[str, Any]) -> int:
    """
    Advance the turn counter.

    Returns:
        int: New turn_id
    """
    context["turn_id"] += 1
    return context["turn_id"]


# ============================================================
# MODE MANAGEMENT
# ============================================================
def set_mode(context: Dict[str, Any], mode: str):
    """
    Update the active shell mode.
    """
    context["mode"] = mode


# ============================================================
# MEMORY MANAGEMENT
# ============================================================
def remember(
    context: Dict[str, Any],
    item: Any,
    limit: int = 10
):
    """
    Store a short-term memory item.

    Memory is capped to avoid unbounded growth.
    """
    memory = context["memory"]["short_term"]
    memory.append(item)

    if len(memory) > limit:
        memory.pop(0)


def set_last_command(context: Dict[str, Any], command_name: str | None):
    """
    Track the last executed command.
    """
    context["memory"]["last_command"] = command_name


def set_flag(context: Dict[str, Any], key: str, value: Any):
    """
    Set a contextual flag.
    """
    context["memory"]["flags"][key] = value


def get_flag(context: Dict[str, Any], key: str, default=None):
    """
    Get a contextual flag.
    """
    return context["memory"]["flags"].get(key, default)


# ============================================================
# SERIALIZATION
# ============================================================
def serialize_context(context: Dict[str, Any]) -> str:
    """
    Serialize a minimal, stable snapshot of the context.

    Used for conversation history persistence.
    """
    snapshot = {
        "session_id": context["session_id"],
        "mode": context["mode"],
        "turn_id": context["turn_id"],
        "last_command": context["memory"]["last_command"],
        "flags": context["memory"]["flags"]
    }
    return str(snapshot)


def hydrate_context(
    context: Dict[str, Any],
    *,
    turn_id: int | None = None,
    last_command: str | None = None,
    flags: dict | None = None
):
    """
    Hydrate an existing context with restored state.
    Used during session resume.
    """
    if turn_id is not None:
        context["turn_id"] = turn_id

    if last_command is not None:
        context["memory"]["last_command"] = last_command

    if flags is not None:
        context["memory"]["flags"].update(flags)
