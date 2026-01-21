import streamlit as st
import sys
import os
import shlex
import time
from datetime import datetime
from pathlib import Path

# ---------------------------
# PATH SETUP
# ---------------------------
CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parent.parent
sys.path.append(str(ROOT_DIR))

# ---------------------------
# INTERNAL MODULES
# ---------------------------
from Core.db_init import init_db
from Core.db_writer import (
    log_session_start,
    log_command,
    log_error
)

# ---------------------------
# COMMAND MODULES
# ---------------------------
from General_Commands.commands import (
    shell_exit, shell_help, shell_status,
    shell_clear, shell_history, shell_logs
)
from External_Commands.commands import (
    shell_open, shell_register, shell_clean,
    shell_make, shell_read, shell_search,
    shell_news, shell_weather, shell_stocks,
    shell_download
)

from AICore import ai_engine

# ---------------------------
# STREAMLIT CONFIG
# ---------------------------
st.set_page_config(
    page_title="Personalised Intelligent Shell",
    page_icon="⚡",
    layout="wide"
)

USER_NAME = os.getenv("USER_NAME", "Jai")

# ---------------------------
# CSS (Clean, Terminal Feel)
# ---------------------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.stChatInput {
    position: fixed;
    bottom: 20px;
    width: 100%;
    z-index: 1000;
}

.stCodeBlock {
    background-color: #0e1117;
    border: 1px solid #30333d;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# FUNCTION MAP (RULE MODE)
# ---------------------------
FUNCTION_MAP = {
    "exit": shell_exit,
    "quit": shell_exit,
    "help": shell_help,
    "status": shell_status,
    "clear": shell_clear,
    "history": shell_history,
    "logs": shell_logs,
    "open": shell_open,
    "register": shell_register,
    "clean": shell_clean,
    "make": shell_make,
    "read": shell_read,
    "search": shell_search,
    "news": shell_news,
    "weather": shell_weather,
    "stocks": shell_stocks,
    "download": shell_download,
}

# ---------------------------
# HELPERS
# ---------------------------
def format_response(result):
    if not isinstance(result, dict):
        return "Command finished."

    parts = []

    if result.get("message"):
        parts.append(result["message"])

    data = result.get("data")
    if isinstance(data, dict):
        content = data.get("content")
        if isinstance(content, list):
            parts.append(f"```bash\n" + "\n".join(map(str, content)) + "\n```")
        elif isinstance(content, str):
            parts.append(content)

    return "\n\n".join(parts)


def normalize_result(result):
    if result is None:
        return {
            "status": "success",
            "message": "Command completed.",
            "data": {}
        }
    if not isinstance(result, dict):
        return {
            "status": "success",
            "message": str(result),
            "data": {}
        }
    return result


def execute_command(prompt, context):
    # Mode switching
    if prompt.lower() == "mode ai":
        context["mode"] = "ai"
        return {"message": "Switched to AI mode.", "status": "success"}

    if prompt.lower() == "mode rule":
        context["mode"] = "rule"
        return {"message": "Switched to rule mode.", "status": "success"}

    try:
        tokens = shlex.split(prompt)
        cmd = tokens[0].lower()
        args = tokens[1:]
    except ValueError:
        return {"message": "That command looks malformed.", "status": "error"}

    try:
        if context["mode"] == "rule":
            if cmd not in FUNCTION_MAP:
                log_error(context["session_id"], "UnknownCommand", cmd, "streamlit")
                return {"message": f"Unknown command: `{cmd}`", "status": "error"}

            func = FUNCTION_MAP[cmd]
            result = normalize_result(func(args, context))
            function_name = func.__name__

        else:
            result = normalize_result(ai_engine(prompt, context))
            function_name = "ai_engine"

        log_command(
            context["session_id"],
            prompt,
            result,
            context["mode"],
            function_name
        )

        data = result.get("data")
        if isinstance(data, dict) and data.get("action") == "clear_screen":
            st.session_state.messages = []
            return {"message": "Console cleared.", "status": "success"}

        return result

    except Exception as e:
        log_error(context["session_id"], "CriticalCrash", str(e), "streamlit")
        return {
            "message": "That command didn’t return anything usable yet.",
            "status": "error"
        }

# ---------------------------
# INITIALIZATION
# ---------------------------
if "initialized" not in st.session_state:
    init_db()

    st.session_state.context = {
        "session_id": int(time.time()),
        "user_name": USER_NAME,
        "mode": "rule",
        "start_time": datetime.now().isoformat()
    }

    log_session_start(st.session_state.context["session_id"])

    st.session_state.messages = [{
        "role": "assistant",
        "content": f"Shell ready.\n\nWelcome, {USER_NAME}. Type `help` to get started."
    }]

    st.session_state.pending_result = None
    st.session_state.initialized = True

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.title("⚡ Personalised Shell")
    st.divider()

    st.markdown(f"**Mode:** `{st.session_state.context['mode'].upper()}`")
    st.markdown(f"**Session:** `{st.session_state.context['session_id']}`")

    st.divider()

    if st.button("Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("Toggle mode", use_container_width=True):
        st.session_state.context["mode"] = (
            "ai" if st.session_state.context["mode"] == "rule" else "rule"
        )
        st.toast(f"Switched to {st.session_state.context['mode'].upper()} mode")
        st.rerun()

# ---------------------------
# CHAT HISTORY
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# CHAT INPUT (FULL WIDTH)
# ---------------------------
if prompt := st.chat_input(
    f"Type a command ({st.session_state.context['mode']} mode)…"
):
    if st.session_state.pending_result is None:
        st.session_state.messages.append({"role": "user", "content": prompt})

        result = execute_command(prompt, st.session_state.context)
        response_text = format_response(result)

        st.session_state.pending_result = response_text
        st.rerun()

# ---------------------------
# ASSISTANT RESPONSE
# ---------------------------
if st.session_state.pending_result:
    with st.chat_message("assistant"):
        placeholder = st.empty()
        rendered = ""

        for word in st.session_state.pending_result.split(" "):
            rendered += word + " "
            time.sleep(0.02)
            placeholder.markdown(rendered + "▌")

        placeholder.markdown(rendered)

    st.session_state.messages.append({
        "role": "assistant",
        "content": st.session_state.pending_result
    })

    st.session_state.pending_result = None
