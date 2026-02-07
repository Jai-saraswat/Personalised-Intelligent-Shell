# ============================================================
# ContextManager.py
# ============================================================
# In-memory context lifecycle manager for JaiShell.
#
# Responsibilities:
# - Create and maintain session context
# - Track turn progression
# - Hold lightweight cross-mode memory
# - Provide safe serialization for persistence
#
# This module does NOT:
# - Read or write the database
# - Execute commands
# - Call AI or Chat engines
# ============================================================

from datetime import datetime
from typing import Dict, Any, Optional
import json


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
    """
    context["turn_id"] += 1
    return context["turn_id"]


# ============================================================
# MODE MANAGEMENT
# ============================================================

def set_mode(context: Dict[str, Any], mode: str) -> None:
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
) -> None:
    """
    Store a short-term memory item.

    Memory is capped to avoid unbounded growth.
    """
    memory = context["memory"]["short_term"]
    memory.append(item)

    if len(memory) > limit:
        memory.pop(0)


def set_last_command(
    context: Dict[str, Any],
    command_name: Optional[str]
) -> None:
    """
    Track the last executed command.
    """
    context["memory"]["last_command"] = command_name


def set_flag(
    context: Dict[str, Any],
    key: str,
    value: Any
) -> None:
    """
    Set a contextual flag.
    """
    context["memory"]["flags"][key] = value


def get_flag(
    context: Dict[str, Any],
    key: str,
    default: Any = None
) -> Any:
    """
    Retrieve a contextual flag.
    """
    return context["memory"]["flags"].get(key, default)


# ============================================================
# SERIALIZATION (STABLE & SAFE)
# ============================================================

def serialize_context(context: Dict[str, Any]) -> str:
    """
    Serialize a minimal, stable snapshot of the context.

    This snapshot is:
    - Deterministic
    - JSON-safe
    - Suitable for DB persistence
    """
    snapshot = {
        "session_id": context["session_id"],
        "mode": context["mode"],
        "turn_id": context["turn_id"],
        "last_command": context["memory"]["last_command"],
        "flags": context["memory"]["flags"]
    }

    return json.dumps(snapshot, separators=(",", ":"))


def hydrate_context(
    context: Dict[str, Any],
    *,
    turn_id: Optional[int] = None,
    last_command: Optional[str] = None,
    flags: Optional[dict] = None
) -> None:
    """
    Hydrate an existing context with restored state.
    Used during session resume.
    """
    if turn_id is not None:
        context["turn_id"] = turn_id

    if last_command is not None:
        context["memory"]["last_command"] = last_command

    if flags:
        context["memory"]["flags"].update(flags)
