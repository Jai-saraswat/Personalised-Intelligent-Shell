# ============================================================
# db_reader.py
# ============================================================
# Read-only database access layer for JaiShell.
#
# This module exposes explicit queries used by:
#   - CoreShell
#   - General commands
#   - AI orchestration
#   - ChatCore
#
# RULES:
# - No writes
# - No business logic
# - No AI reasoning
# - No schema mutation
# ============================================================

import json
from Core.db_connection import get_connection

# ============================================================
# SESSION & STATS
# ============================================================

def get_total_sessions():
    """
    Return total number of recorded sessions.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessions")
        return cur.fetchone()[0]
    finally:
        conn.close()


def get_session_stats(session_id: int):
    """
    Return basic statistics for a given session.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*)
            FROM command_executions
            WHERE session_id = ?
            """,
            (session_id,),
        )
        command_count = cur.fetchone()[0]
        return {
            "command_count": command_count
        }
    finally:
        conn.close()

# ============================================================
# COMMAND HISTORY (GLOBAL)
# ============================================================

def get_recent_commands(limit: int = 10):
    """
    Fetch recent command executions across all sessions.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                raw_input,
                status,
                mode,
                timestamp
            FROM command_executions
            ORDER BY execution_id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
    finally:
        conn.close()


def get_session_commands(session_id: int, limit: int = 20):
    """
    Fetch command executions for a specific session.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                raw_input,
                status,
                mode,
                timestamp
            FROM command_executions
            WHERE session_id = ?
            ORDER BY execution_id DESC
            LIMIT ?
            """,
            (session_id, limit),
        )
        return cur.fetchall()
    finally:
        conn.close()

# ============================================================
# ERROR LOGS
# ============================================================

def get_recent_errors(limit: int = 5):
    """
    Fetch recent system or command errors.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                error_name,
                error_description,
                origin_function,
                timestamp
            FROM errors
            ORDER BY error_id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
    finally:
        conn.close()

# ============================================================
# REGISTRY (OPEN COMMAND)
# ============================================================

def get_registry_entries():
    """
    Fetch all registered shortcuts.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT name, path, type
            FROM registry
            ORDER BY name ASC
            """
        )
        return cur.fetchall()
    finally:
        conn.close()


def get_registry_entry(name: str):
    """
    Fetch a specific registry entry by name.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT path, type
            FROM registry
            WHERE name = ?
            """,
            (name,),
        )
        return cur.fetchone()
    finally:
        conn.close()

# ============================================================
# COMMAND REGISTRY (AI SOURCE OF TRUTH)
# ============================================================

def get_all_commands():
    """
    Fetch all registered command definitions.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                command_id,
                command_name,
                category,
                description,
                schema_json,
                is_destructive,
                requires_confirmation
            FROM commands
            """
        )
        rows = cur.fetchall()

        commands = []
        for row in rows:
            commands.append({
                "command_id": row[0],
                "command_name": row[1],
                "category": row[2],
                "description": row[3],
                "schema_json": json.loads(row[4]),
                "is_destructive": bool(row[5]),
                "requires_confirmation": bool(row[6]),
            })

        return commands
    finally:
        conn.close()


def get_command_by_name(command_name: str):
    """
    Fetch a single command definition by name.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                command_id,
                command_name,
                category,
                description,
                schema_json,
                is_destructive,
                requires_confirmation
            FROM commands
            WHERE command_name = ?
            """,
            (command_name,),
        )
        row = cur.fetchone()

        if not row:
            return None

        return {
            "command_id": row[0],
            "command_name": row[1],
            "category": row[2],
            "description": row[3],
            "schema_json": json.loads(row[4]),
            "is_destructive": bool(row[5]),
            "requires_confirmation": bool(row[6]),
        }
    finally:
        conn.close()

# ============================================================
# SCHEMA ACCESS (AI CORE)
# ============================================================

def get_function_schema(command_id: int):
    """
    Fetch full command metadata for AI execution.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                command_name,
                schema_json,
                is_destructive,
                requires_confirmation
            FROM commands
            WHERE command_id = ?
            """,
            (command_id,)
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "command_name": row[0],
            "schema_json": json.loads(row[1]),
            "is_destructive": bool(row[2]),
            "requires_confirmation": bool(row[3]),
        }
    finally:
        conn.close()

# ============================================================
# CONVERSATION HISTORY (SESSION-AWARE MEMORY)
# ============================================================

def get_conversation_history(session_id: int, limit: int = 20):
    """
    Fetch recent conversation turns for a session.
    Returns list[dict] in DESC order.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                turn_id,
                mode,
                user_input,
                assistant_output,
                command_called,
                status,
                confidence,
                context_snapshot,
                timestamp
            FROM conversation_history
            WHERE session_id = ?
            ORDER BY turn_id DESC
            LIMIT ?
            """,
            (session_id, limit)
        )

        rows = cur.fetchall()

        return [
            {
                "turn_id": r[0],
                "mode": r[1],
                "user_input": r[2],
                "assistant_output": r[3],
                "command_called": r[4],
                "status": r[5],
                "confidence": r[6],
                "context_snapshot": r[7],
                "timestamp": r[8],
            }
            for r in rows
        ]

    finally:
        conn.close()


def get_last_conversation_turn(session_id: int):
    """
    Fetch the most recent conversation turn for a session.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                turn_id,
                mode,
                user_input,
                assistant_output,
                command_called,
                status,
                confidence,
                context_snapshot,
                timestamp
            FROM conversation_history
            WHERE session_id = ?
            ORDER BY turn_id DESC
            LIMIT 1
            """,
            (session_id,)
        )
        return cur.fetchone()
    finally:
        conn.close()


def get_conversation_turns_after(session_id: int, turn_id: int):
    """
    Fetch conversation turns after a given turn_id.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                turn_id,
                mode,
                user_input,
                assistant_output,
                command_called,
                status,
                confidence,
                context_snapshot,
                timestamp
            FROM conversation_history
            WHERE session_id = ? AND turn_id > ?
            ORDER BY turn_id ASC
            """,
            (session_id, turn_id)
        )
        return cur.fetchall()
    finally:
        conn.close()

# ============================================================
# SESSION RESUME HELPERS
# ============================================================

def get_last_session_id():
    """
    Fetch the most recent session_id.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT session_id
            FROM sessions
            ORDER BY start_timestamp DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def get_last_turn_id(session_id: int):
    """
    Fetch the last recorded turn_id for a session.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT MAX(turn_id)
            FROM conversation_history
            WHERE session_id = ?
            """,
            (session_id,)
        )
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else 0
    finally:
        conn.close()
