# ============================================================
# db_writer.py
# ============================================================
# Write-only persistence layer for JaiShell.
#
# This module is responsible for inserting factual records
# into the database. It does not interpret, reason, or decide.
#
# RULES:
# - Accept primitives only (str, int, bool, float)
# - Generate timestamps internally
# - Never accept raw dicts
# ============================================================

from datetime import datetime
from Core.db_connection import get_connection

# ============================================================
# SESSION LOGGING
# ============================================================
def log_session_start(session_id: int, start_timestamp: str):
    """
    Record the start of a shell session.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sessions (session_id, start_timestamp, grace_termination)
            VALUES (?, ?, 0)
            """,
            (session_id, start_timestamp)
        )
        conn.commit()
    finally:
        conn.close()


def log_session_end(session_id: int, graceful: bool, end_timestamp: str):
    """
    Mark the end of a shell session.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE sessions
            SET end_timestamp = ?, grace_termination = ?
            WHERE session_id = ?
            """,
            (end_timestamp, 1 if graceful else 0, session_id)
        )
        conn.commit()
    finally:
        conn.close()

# ============================================================
# COMMAND EXECUTION LOGGING
# ============================================================
def log_command_execution(
    session_id: int,
    raw_input: str,
    status: str,
    mode: str,
    function_called: str = None,
    command_id: int = None
):
    """
    Log a command execution event.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO command_executions
            (session_id, raw_input, command_id, status, mode, function_called, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                raw_input,
                command_id,
                status,
                mode,
                function_called,
                datetime.now().isoformat()
            )
        )
        conn.commit()
    finally:
        conn.close()

# ============================================================
# ERROR LOGGING
# ============================================================
def log_error(
    session_id: int,
    error_name: str,
    error_description: str,
    origin_function: str
):
    """
    Log a system or command error.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO errors
            (session_id, error_name, error_description, origin_function, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                error_name,
                error_description,
                origin_function,
                datetime.now().isoformat()
            )
        )
        conn.commit()
    finally:
        conn.close()

# ============================================================
# REGISTRY MANAGEMENT
# ============================================================
def register_entry(name: str, path: str, type_: str):
    """
    Add or update a registry shortcut.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO registry (name, path, type)
            VALUES (?, ?, ?)
            """,
            (name, path, type_)
        )
        conn.commit()
    finally:
        conn.close()


def unregister_entry(name: str):
    """
    Remove a registry shortcut.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM registry WHERE name = ?",
            (name,)
        )
        conn.commit()
    finally:
        conn.close()

# ============================================================
# CONVERSATION HISTORY LOGGING
# ============================================================
def log_conversation_turn(
    session_id: int,
    turn_id: int,
    mode: str,
    user_input: str,
    assistant_output: str,
    command_called: str = None,
    status: str = None,
    confidence: float = None,
    context_snapshot: str = None
):
    """
    Persist a single conversation turn (rule / ai / chat).

    This function:
    - Writes immutable conversational facts
    - Does NOT interpret content
    - Does NOT manage context
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO conversation_history
            (
                session_id,
                turn_id,
                mode,
                user_input,
                assistant_output,
                command_called,
                status,
                confidence,
                context_snapshot,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                turn_id,
                mode,
                user_input,
                assistant_output,
                command_called,
                status,
                confidence,
                context_snapshot,
                datetime.now().isoformat()
            )
        )
        conn.commit()
    finally:
        conn.close()
