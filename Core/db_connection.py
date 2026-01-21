# Core/db_connection.py
import sqlite3
from pathlib import Path

# --- GLOBAL CONFIGURATION ---
# Base directory is the parent of the current file (Core folder)
BASE_DIR = Path(__file__).resolve().parent
DB_NAME = "Shell_Warehouse.db"
DB_PATH = BASE_DIR / DB_NAME

def get_connection():
    """
    Establishes a connection to the SQLite database.
    Enforces foreign keys.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        # In a real scenario, we might log this, but since we can't connect to DB,
        # we raise it to be caught by Core.
        raise ConnectionError(f"Failed to connect to database at {DB_PATH}: {e}")