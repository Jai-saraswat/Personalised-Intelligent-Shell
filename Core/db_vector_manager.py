# ============================================================
# db_vector_manager.py
# ============================================================
# Embedding generation and persistence for JaiShell commands.
#
# Responsibilities:
# - Read command descriptions from database
# - Generate sentence embeddings using the SAME model as router
# - Persist embeddings back to database
#
# RULES:
# - Commands table is the source of truth
# - No schema creation here
# - No routing or similarity logic here
# - Model choice MUST stay consistent with Function_Router
# ============================================================

import json
from sentence_transformers import SentenceTransformer
from Core.db_connection import get_connection

# ============================================================
# MODEL CONFIGURATION (SINGLE SOURCE OF TRUTH)
# ============================================================
# MUST match Core/Function_Router.py
MODEL_PATH = r"D:\Coding\Projects\Personlised_Intelligent_Shell\Finetuned-gte-large-en-v1.5"

# ============================================================
# EMBEDDING PIPELINE
# ============================================================
def generate_and_store_command_embeddings():
    """
    Generate embeddings for all commands defined in the database
    and store them in the command_embeddings table.
    """
    print(f"Loading embedding model: {MODEL_PATH}")

    model = SentenceTransformer(
        MODEL_PATH,
        trust_remote_code=True
    )

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Commands table is the source of truth
        cur.execute(
            """
            SELECT command_id, description
            FROM commands
            """
        )
        commands = cur.fetchall()

        if not commands:
            print("No commands found in database. Nothing to embed.")
            return

        print(f"Generating embeddings for {len(commands)} commands...")

        for command_id, description in commands:
            embedding = model.encode(
                description,
                normalize_embeddings=True
            ).tolist()

            cur.execute(
                """
                INSERT OR REPLACE INTO command_embeddings
                (command_id, embedding_json)
                VALUES (?, ?)
                """,
                (command_id, json.dumps(embedding))
            )

        conn.commit()
        print("Command embeddings stored successfully.")

    finally:
        conn.close()

# ============================================================
# SCRIPT ENTRY POINT
# ============================================================
if __name__ == "__main__":
    generate_and_store_command_embeddings()
