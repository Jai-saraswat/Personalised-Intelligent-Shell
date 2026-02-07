# ============================================================
# db_connection.py
# ============================================================
# Centralized SQLite connection manager for JaiShell.
#
# This module is responsible ONLY for:
#   - Defining where the database lives
#   - Creating safe, configured SQLite connections
#
# It must:
#   - Have no side effects
#   - Contain no schema logic
#   - Contain no read/write logic
#
# All database access flows through this file.
# ============================================================

import sqlite3
from pathlib import Path

# ============================================================
# DATABASE LOCATION
# ============================================================
# The database lives alongside the Core module.
BASE_DIR = Path(__file__).resolve().parent
DB_NAME = "Shell_Warehouse.db"
DB_PATH = BASE_DIR / DB_NAME

# ============================================================
# CONNECTION FACTORY
# ============================================================
def get_connection():
    """
    Create and return a configured SQLite connection.

    Configuration applied:
    - Foreign key enforcement
    - WAL journal mode (handled in db_init)
    - Explicit timeout to avoid lock contention
    - Row factory disabled (explicit tuples for clarity)
    """
    try:
        conn = sqlite3.connect(
            DB_PATH,
            timeout=30  # prevents 'database is locked' issues
        )

        # Enforce relational integrity
        conn.execute("PRAGMA foreign_keys = ON;")

        return conn

    except sqlite3.Error as e:
        # Cannot log to DB if DB connection itself failed
        raise ConnectionError(
            f"Failed to connect to database at {DB_PATH}: {e}"
        )
