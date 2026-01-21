import json
import sqlite3
from sentence_transformers import SentenceTransformer
from Core.db_connection import get_connection


def save_function_embeddings(functions):
    """
    Encodes function descriptions and saves them to the database.
    """
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    conn = get_connection()
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS function_embeddings
                   (
                       function_name TEXT PRIMARY KEY,
                       description   TEXT,
                       embedding     TEXT
                   )
                   """)

    print("Generating and saving embeddings...")
    for name, description in functions:
        # Generate embedding vector
        vector = model.encode(description).tolist()

        # Save to DB (Insert or Replace ensures updates work)
        cursor.execute("""
            INSERT OR REPLACE INTO function_embeddings (function_name, description, embedding)
            VALUES (?, ?, ?)
        """, (name, description, json.dumps(vector)))

    conn.commit()
    conn.close()
    print("Successfully saved all embeddings to jaishell.db.")


if __name__ == "__main__":
    # Your list from the prompt
    FUNCTION_DESCRIPTIONS = [
        [
            "shell_open",
            "User wants to open or launch something already registered, such as an app, folder, or website."
        ],
        [
            "shell_clean",
            "User wants to remove junk, temporary files, or clear system folders like downloads or temp."
        ],
        [
            "shell_make",
            "User wants to create a new file or a new folder."
        ],
        [
            "shell_read",
            "User wants to read or view the contents of a specific file."
        ],
        [
            "shell_search",
            "User wants to search the internet for information."
        ],
        [
            "shell_news",
            "User wants to know current news or headlines."
        ],
        [
            "shell_weather",
            "User wants to know the weather for a specific location."
        ],
        [
            "shell_stocks",
            "User wants to know stock prices or market information."
        ],
        [
            "shell_download",
            "User wants to download a file from a URL."
        ]
    ]

    save_function_embeddings(FUNCTION_DESCRIPTIONS)