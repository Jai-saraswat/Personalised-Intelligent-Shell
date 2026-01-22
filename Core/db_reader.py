# ============================================================
# db_reader.py
# ============================================================
# Read-only database access layer for JaiShell.
#
# This module exposes explicit queries used by:
#   - CoreShell
#   - General commands
#   - AI orchestration
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
# COMMAND HISTORY
# ============================================================

def get_recent_commands(limit: int = 10):
    """
    Fetch recent command executions across all sessions.
    Used by the 'history' command.
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

# ============================================================
# ERROR LOGS
# ============================================================

def get_recent_errors(limit: int = 5):
    """
    Fetch recent system or command errors.
    Used by the 'logs' command.
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

