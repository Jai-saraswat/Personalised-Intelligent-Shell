# ============================================================
# db_init.py
# ============================================================
# Database initialization and schema definition for JaiShell.
#
# This module is responsible ONLY for:
#   - Creating the database schema
#   - Ensuring tables, constraints, and indexes exist
#
# It must be:
#   - Safe to run multiple times
#   - Free of business logic
#   - Free of data mutation beyond schema creation
#
# Any logic beyond schema definition does NOT belong here.
# ============================================================

import sqlite3
from Core.db_connection import DB_PATH, get_connection

# ============================================================
# DATABASE SCHEMA (AUTHORITATIVE)
# ============================================================
SCHEMA_SQL = """

-- ============================================================
-- 1. Sessions
-- Tracks individual shell lifecycles.
-- ============================================================
CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY,
    start_timestamp TEXT NOT NULL,
    end_timestamp TEXT,
    grace_termination BOOLEAN DEFAULT 0
);

-- ============================================================
-- 2. Commands (SOURCE OF TRUTH)
-- Defines all valid shell commands.
-- ============================================================
CREATE TABLE IF NOT EXISTS commands (
    command_id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    schema_json TEXT NOT NULL,
    is_destructive BOOLEAN DEFAULT 0,
    requires_confirmation BOOLEAN DEFAULT 0
);

-- ============================================================
-- 3. Command Embeddings
-- Semantic representation for AI routing.
-- ============================================================
CREATE TABLE IF NOT EXISTS command_embeddings (
    command_id INTEGER PRIMARY KEY,
    embedding_json TEXT NOT NULL,
    FOREIGN KEY (command_id) REFERENCES commands (command_id)
);

-- ============================================================
-- 4. Command Executions
-- Immutable history of all user actions.
-- ============================================================
CREATE TABLE IF NOT EXISTS command_executions (
    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    raw_input TEXT NOT NULL,
    command_id INTEGER,
    status TEXT NOT NULL,
    mode TEXT NOT NULL,
    function_called TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
    FOREIGN KEY (command_id) REFERENCES commands (command_id)
);

-- ============================================================
-- 5. AI Decisions
-- Explainability layer for AI-assisted routing.
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    raw_input TEXT NOT NULL,
    chosen_command_id INTEGER,
    confidence REAL,
    decision_type TEXT NOT NULL,
    reason TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
    FOREIGN KEY (chosen_command_id) REFERENCES commands (command_id)
);

-- ============================================================
-- 6. Errors
-- System, execution, and internal failures.
-- ============================================================
CREATE TABLE IF NOT EXISTS errors (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    error_name TEXT NOT NULL,
    error_description TEXT,
    origin_function TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);

-- ============================================================
-- 7. Registry
-- User-defined shortcuts (open command).
-- ============================================================
CREATE TABLE IF NOT EXISTS registry (
    name TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    type TEXT CHECK (type IN ('program', 'folder', 'url')) NOT NULL
);

-- ============================================================
-- 8. Global Settings
-- Centralized configuration store.
-- ============================================================
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- ============================================================
-- 9. Conversation History
-- Persistent multi-mode (rule / ai / chat) memory.
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    turn_id INTEGER NOT NULL,
    mode TEXT NOT NULL,
    user_input TEXT NOT NULL,
    assistant_output TEXT,
    command_called TEXT,
    status TEXT,
    confidence REAL,
    context_snapshot TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Command executions
CREATE INDEX IF NOT EXISTS idx_exec_session
    ON command_executions (session_id);

-- Errors
CREATE INDEX IF NOT EXISTS idx_error_session
    ON errors (session_id);

-- AI decisions
CREATE INDEX IF NOT EXISTS idx_ai_session
    ON ai_decisions (session_id);

-- Conversation history lookups
CREATE INDEX IF NOT EXISTS idx_conversation_session
    ON conversation_history (session_id);

CREATE INDEX IF NOT EXISTS idx_conversation_turn
    ON conversation_history (session_id, turn_id);

-- Enforce unique turn ordering per session
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_session_turn
    ON conversation_history (session_id, turn_id);

-- Optimize session resume / lookup
CREATE INDEX IF NOT EXISTS idx_sessions_start_time
    ON sessions (start_timestamp);

"""

# ============================================================
# INITIALIZATION ROUTINE
# ============================================================
def init_db():
    """
    Initialize the JaiShell database.

    This function:
    - Enables SQLite foreign key enforcement
    - Creates all tables and indexes if missing
    - Is safe to run multiple times
    """
    print(f"Initializing database at: {DB_PATH}")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Ensure SQLite behaves correctly
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")

        # Apply schema
        cursor.executescript(SCHEMA_SQL)
        conn.commit()

        print("Database schema ready.")

    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()

# ============================================================
# SCRIPT ENTRY POINT
# ============================================================
if __name__ == "__main__":
    init_db()
