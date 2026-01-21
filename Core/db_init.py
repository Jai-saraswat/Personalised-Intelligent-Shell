# Core/db_init.py
import sqlite3
from pathlib import Path
from Core.db_connection import DB_PATH, get_connection

# --- SCHEMA DEFINITION ---
SCHEMA_SQL = """
             -- ---------------------------
-- 1. Sessions Table
-- Tracks individual shell usage sessions.
-- ---------------------------
             CREATE TABLE IF NOT EXISTS sessions \
             ( \
                 session_id        INTEGER PRIMARY KEY, \
                 start_timestamp   TEXT NOT NULL, \
                 end_timestamp     TEXT, \
                 grace_termination BOOLEAN DEFAULT 0
             );

             -- ---------------------------
-- 2. Commands Executed Table
-- Logs every user interaction and its result.
-- ---------------------------
             CREATE TABLE IF NOT EXISTS commands_executed \
             ( \
                 id              INTEGER PRIMARY KEY AUTOINCREMENT, \
                 session_id      INTEGER NOT NULL, \
                 prompt          TEXT    NOT NULL, \
                 status          TEXT    NOT NULL, \
                 description     TEXT, \
                 mode            TEXT    NOT NULL, \
                 function_called TEXT, \
                 timestamp       TEXT    NOT NULL, \
                 FOREIGN KEY (session_id) REFERENCES sessions (session_id)
             );

             -- ---------------------------
-- 3. Errors Table
-- Logs internal or execution errors for debugging.
-- ---------------------------
             CREATE TABLE IF NOT EXISTS errors \
             ( \
                 id                INTEGER PRIMARY KEY AUTOINCREMENT, \
                 session_id        INTEGER NOT NULL, \
                 error_name        TEXT    NOT NULL, \
                 error_description TEXT, \
                 origin_function   TEXT, \
                 timestamp         TEXT    NOT NULL, \
                 FOREIGN KEY (session_id) REFERENCES sessions (session_id)
             );

             -- ---------------------------
-- 4. Registry Table
-- Stores user-defined shortcuts (Open command).
-- ---------------------------
             CREATE TABLE IF NOT EXISTS registry \
             ( \
                 name TEXT PRIMARY KEY, \
                 path TEXT                                              NOT NULL, \
                 type TEXT CHECK (type IN ('program', 'folder', 'url')) NOT NULL
             );

             -- ---------------------------
-- Indexes for Performance
-- ---------------------------
             CREATE INDEX IF NOT EXISTS idx_commands_session ON commands_executed (session_id);
             CREATE INDEX IF NOT EXISTS idx_errors_session ON errors (session_id); \
             -- ---------------------------
-- Function Embeddings (Semantic Router)
-- ---------------------------
CREATE TABLE IF NOT EXISTS function_embeddings (
    function_name TEXT PRIMARY KEY,
    description TEXT,
    embedding TEXT -- Stored as a JSON-stringified list
);
CREATE TABLE IF NOT EXISTS functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    schema_json TEXT NOT NULL -- Stored as a JSON string
);
             """


def init_db():
    """
    Initializes the database schema.
    Creates the database file if it doesn't exist.
    """
    print(f"Initializing database at: {DB_PATH}")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Execute the schema script
        cursor.executescript(SCHEMA_SQL)

        conn.commit()
        print("Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    init_db()