# ============================================================
# ChatCore.py
# ============================================================
# Conversational mode handler for JaiShell (LLM-powered).
#
# FINAL VERSION:
# - Session-aware
# - Full history-aware (RULE + AI + CHAT)
# - Execution-provenance aware
# - Strict non-execution boundaries
# ============================================================

from typing import Dict, List

from Core.command_contract import command_result
from Core.groq_client import chat_complete
from Core.db_reader import get_conversation_history


# ============================================================
# CHAT PARAMETERS
# ============================================================

TEMPERATURE = 0.2
TOP_P = 0.9
MAX_TOKENS = 800
HISTORY_WINDOW = 12


# ============================================================
# SYSTEM PROMPT (EXECUTION-AWARE & SAFE)
# ============================================================

SYSTEM_PROMPT = """
You are ChatCore, the conversational intelligence of JaiShell.

========================
EXECUTION CONTEXT (CRITICAL)
========================
JaiShell operates in multiple modes: RULE, AI, and CHAT.

- Commands executed in RULE or AI mode are REAL system executions.
- You did NOT execute those commands, but they DID occur.
- Execution records provided to you are FACTUAL and AUTHORITATIVE.
- You MUST treat them as real past events.
- You MUST NOT call them placeholders, simulations, or hypothetical.
- You MUST NOT claim that you executed them.

========================
CHAT MODE BOUNDARIES
========================
You are currently operating in CHAT MODE.

You MUST NOT:
- Execute or simulate commands
- Access files, network, system state, or DB yourself
- Invent outputs or imply system changes

========================
ALLOWED
========================
You MAY:
- Explain system behavior
- Answer questions about past executions
- Summarize sessions accurately
- Clarify which MODE executed what
- Reason step-by-step in text

========================
ACTION REQUESTS
========================
If the user asks to perform an action:
- Explain CHAT mode limitations
- Suggest switching to `mode ai` or `mode rule`

========================
SESSION SUMMARY RULE
========================
- Describe what the USER requested
- Describe what the SYSTEM executed
- Always reference the MODE
- Never fabricate or infer beyond history

STYLE:
- Clear
- Technical
- Concise
- Neutral
""".strip()


# ============================================================
# CHAT ENGINE (FINAL)
# ============================================================

def chat_engine(prompt: str, context: Dict) -> Dict:
    """
    Chat-mode LLM handler with full execution-aware history.
    """

    # ----------------------------
    # Validation
    # ----------------------------
    if not isinstance(prompt, str) or not prompt.strip():
        return command_result(
            status="error",
            message="Invalid chat input."
        )

    prompt = prompt.strip()

    session_id = context.get("session_id")
    user_name = context.get("user_name", "User")
    mode = context.get("mode", "chat")
    turn_id = context.get("turn_id", 0)

    # ----------------------------
    # System message
    # ----------------------------
    system_message = (
        SYSTEM_PROMPT
        + "\n\nSession Context:\n"
        + f"- User: {user_name}\n"
        + f"- Current Mode: {mode}\n"
        + f"- Turn: {turn_id}\n"
    )

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_message}
    ]

    # ----------------------------
    # Inject execution-aware history
    # ----------------------------
    try:
        history = get_conversation_history(
            session_id=session_id,
            limit=HISTORY_WINDOW
        )
    except Exception:
        history = []

    # Chronological order
    for entry in reversed(history):

        past_mode = entry["mode"]
        user_input = entry["user_input"]
        assistant_output = entry["assistant_output"]
        command_called = entry["command_called"]
        status = entry["status"]

        if past_mode == "chat":
            if user_input:
                messages.append({
                    "role": "user",
                    "content": user_input
                })
            if assistant_output:
                messages.append({
                    "role": "assistant",
                    "content": assistant_output
                })

        else:
            # RULE / AI execution — factual system record
            messages.append({
                "role": "system",
                "content": (
                    "[EXECUTION RECORD]\n"
                    f"- Mode: {past_mode.upper()}\n"
                    f"- User Input: {user_input}\n"
                    f"- Command Called: {command_called}\n"
                    f"- Status: {status}\n"
                    f"- Output:\n{assistant_output}\n\n"
                    "(This execution was performed by the system, not ChatCore.)"
                )
            })

    # ----------------------------
    # Current user prompt
    # ----------------------------
    messages.append({
        "role": "user",
        "content": prompt
    })

    # ----------------------------
    # Groq completion
    # ----------------------------
    try:
        reply = chat_complete(
            messages=messages,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=MAX_TOKENS,
        )

        if not reply or not reply.strip():
            raise RuntimeError("Empty response from chat model")

        return command_result(
            status="success",
            message=reply.strip(),
            confidence=0.85
        )

    except Exception as e:
        return command_result(
            status="error",
            message=f"Chat engine failure: {e}"
        )