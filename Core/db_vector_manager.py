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
import os
from pathlib import Path

from sentence_transformers import SentenceTransformer
from Core.db_connection import get_connection

# ============================================================
# MODEL CONFIGURATION (SINGLE SOURCE OF TRUTH)
# ============================================================

DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[1] / "Finetuned-gte-large-en-v1.5"
MODEL_PATH = Path(os.getenv("EMBEDDING_MODEL_PATH", DEFAULT_MODEL_DIR))

# ============================================================
# EMBEDDING PIPELINE
# ============================================================

def generate_and_store_command_embeddings():
    """
    Generate embeddings for all commands defined in the database
    and store them in the command_embeddings table.
    """

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Embedding model not found at: {MODEL_PATH}"
        )

    print(f"[Embeddings] Loading model from: {MODEL_PATH}")

    model = SentenceTransformer(
        str(MODEL_PATH),
        trust_remote_code=True
    )

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Always work in deterministic order
        cur.execute(
            """
            SELECT command_id, description
            FROM commands
            ORDER BY command_id ASC
            """
        )
        commands = cur.fetchall()

        if not commands:
            print("[Embeddings] No commands found. Nothing to embed.")
            return

        print(f"[Embeddings] Generating embeddings for {len(commands)} commands...")

        # Remove stale embeddings first
        cur.execute("DELETE FROM command_embeddings")

        for command_id, description in commands:
            embedding = model.encode(
                description,
                normalize_embeddings=True
            ).tolist()

            cur.execute(
                """
                INSERT INTO command_embeddings
                (command_id, embedding_json)
                VALUES (?, ?)
                """,
                (command_id, json.dumps(embedding))
            )

        conn.commit()
        print("[Embeddings] Command embeddings regenerated successfully.")

    finally:
        conn.close()

# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    generate_and_store_command_embeddings()
