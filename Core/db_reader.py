# Core/db_reader.py
from datetime import datetime
from Core.db_connection import get_connection
import json
# Note: Using relative import assuming this is run as a module.
# If run directly as script, use 'from db_connection import ...'

# ---------------------------
# Session & Stats Reading
# ---------------------------

def get_total_sessions():
    """Returns the total count of sessions recorded."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessions")
        return cur.fetchone()[0]
    finally:
        conn.close()

def get_session_stats(session_id):
    """Returns stats for a specific session."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT count(*) 
            FROM commands_executed 
            WHERE session_id = ?
        """, (session_id,))
        count = cur.fetchone()[0]
        return {"command_count": count}
    finally:
        conn.close()

# ---------------------------
# History & Logs
# ---------------------------

def get_recent_commands(limit=10):
    """
    Fetches the most recent commands executed across all sessions.
    Used by the 'history' command.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT prompt, status, timestamp 
            FROM commands_executed 
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        return cur.fetchall()
    finally:
        conn.close()

def get_recent_errors(limit=5):
    """
    Fetches recent system errors.
    Used by the 'logs' command.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT error_name, error_description, timestamp 
            FROM errors 
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        return cur.fetchall()
    finally:
        conn.close()

# ---------------------------
# Registry (for External Commands)
# ---------------------------

def get_registry_entries():
    """
    Fetches all registered 'open' shortcuts.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, path, type FROM registry ORDER BY name ASC")
        return cur.fetchall()
    finally:
        conn.close()

def get_registry_entry(name):
    """
    Fetches a specific registry entry by name.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT path, type FROM registry WHERE name = ?", (name,))
        return cur.fetchone()
    finally:
        conn.close()


def get_function_schema(function_name):
    """
    Retrieves the JSON schema for a specific function from the database.
    Used by the AI to understand what arguments to extract.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Query the functions table we created
        cursor.execute(
            "SELECT schema_json FROM functions WHERE function_name = ?",
            (function_name,)
        )
        row = cursor.fetchone()

        if row:
            # Parse the stored string back into a Python dictionary
            return json.loads(row[0])
        return None

    except Exception as e:
        print(f"Error retrieving schema: {e}")
        return None
    finally:
        conn.close()