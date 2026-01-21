# Core/db_writer.py
from datetime import datetime
from db_connection import get_connection

# --- WRITE OPERATIONS ---

def log_session_start(session_id: int):
    """
    Creates a new session entry.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sessions (session_id, start_timestamp, grace_termination)
            VALUES (?, ?, 0)
        """, (session_id, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()

def log_session_end(session_id: int, graceful: bool = True):
    """
    Updates the session with end time and termination status.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE sessions 
            SET end_timestamp = ?, grace_termination = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), 1 if graceful else 0, session_id))
        conn.commit()
    finally:
        conn.close()

def log_command(session_id: int, prompt: str, result: dict, mode: str, function_called: str = None):
    """
    Logs a command execution based on the standardized result contract.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO commands_executed 
            (session_id, prompt, status, description, mode, function_called, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            prompt,
            result.get("status", "unknown"),
            result.get("message", ""),
            mode,
            function_called,
            result.get("timestamp", datetime.now().isoformat())
        ))
        conn.commit()
    finally:
        conn.close()

def log_error(session_id: int, error_name: str, description: str, origin: str):
    """
    Logs a specific system error.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO errors 
            (session_id, error_name, error_description, origin_function, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            error_name,
            description,
            origin,
            datetime.now().isoformat()
        ))
        conn.commit()
    finally:
        conn.close()

def register_entry(name: str, path: str, type_: str):
    """
    Adds or updates a registry entry (for 'open' command).
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO registry (name, path, type)
            VALUES (?, ?, ?)
        """, (name, path, type_))
        conn.commit()
    finally:
        conn.close()

def unregister_entry(name: str):
    """
    Removes a registry entry.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM registry WHERE name = ?", (name,))
        conn.commit()
    finally:
        conn.close()