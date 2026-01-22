# ============================================================
# Function_Router.py
# ============================================================
# Semantic intent router for JaiShell.
#
# This module is responsible ONLY for:
#   - Loading the sentence embedding model
#   - Comparing user input against stored command embeddings
#   - Producing ranked routing decisions
#
# It does NOT:
#   - Execute commands
#   - Ask for confirmation
#   - Log decisions
#   - Know anything about UX
#
# ============================================================

import json
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from Core.db_connection import get_connection

# ============================================================
# MODEL CONFIGURATION
# ============================================================
# Use your fine-tuned model path here
MODEL_PATH = r"D:\Coding\Projects\Personlised_Intelligent_Shell\Finetuned-gte-large-en-v1.5"

# Thresholds (tuned later, kept explicit)
AUTO_EXECUTE_THRESHOLD = 0.75
CONFIRM_THRESHOLD = 0.60
MIN_MARGIN = 0.08

# ============================================================
# MODEL LOADING
# ============================================================
_model = None

def get_model() -> SentenceTransformer:
    """
    Lazy-load the embedding model.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(
            MODEL_PATH,
            trust_remote_code=True
        )
    return _model

# ============================================================
# EMBEDDING FETCH
# ============================================================
def _load_command_embeddings():
    """
    Fetch command embeddings from the database.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                c.command_id,
                c.command_name,
                ce.embedding_json
            FROM commands c
            JOIN command_embeddings ce
                ON c.command_id = ce.command_id
            """
        )

        rows = cur.fetchall()

        command_ids = []
        command_names = []
        embeddings = []

        for command_id, command_name, embedding_json in rows:
            command_ids.append(command_id)
            command_names.append(command_name)
            embeddings.append(json.loads(embedding_json))

        return (
            command_ids,
            command_names,
            np.array(embeddings, dtype="float32")
        )

    finally:
        conn.close()

# ============================================================
# ROUTING CORE
# ============================================================
def predict_intent(query: str, top_k: int = 3) -> List[Tuple[int, str, float]]:
    """
    Rank commands by semantic similarity.

    Returns:
        List of (command_id, command_name, score)
    """
    model = get_model()
    q_embedding = model.encode(query, normalize_embeddings=True)

    command_ids, command_names, command_embeddings = _load_command_embeddings()

    if len(command_embeddings) == 0:
        return []

    scores = cosine_similarity(
        [q_embedding],
        command_embeddings
    )[0]

    ranked = sorted(
        zip(command_ids, command_names, scores),
        key=lambda x: x[2],
        reverse=True
    )

    return ranked[:top_k]

# ============================================================
# DECISION LOGIC
# ============================================================
def route_command(query: str):
    """
    Determine routing action based on similarity confidence.
    """
    ranked = predict_intent(query, top_k=2)

    if len(ranked) == 0:
        return None, "REJECT", 0.0

    (cmd_id_1, cmd_name_1, score_1) = ranked[0]
    (_, _, score_2) = ranked[1] if len(ranked) > 1 else (None, None, 0.0)

    # High confidence + clear margin
    if score_1 >= AUTO_EXECUTE_THRESHOLD and (score_1 - score_2) >= MIN_MARGIN:
        return cmd_id_1, "AUTO_EXECUTE", score_1

    # Medium confidence
    if score_1 >= CONFIRM_THRESHOLD:
        return cmd_id_1, "CONFIRM", score_1

    return None, "REJECT", score_1
