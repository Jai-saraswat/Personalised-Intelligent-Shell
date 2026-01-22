# ============================================================
# CoreShell.py
# ============================================================
# JaiShell Core Orchestrator
#
# Responsibilities:
#   - Boot sequence & CLI UX
#   - Session lifecycle
#   - Deterministic routing (rule mode)
#   - AI delegation (ai mode)
#   - Output rendering
#   - Centralized logging
#
# ============================================================
import os
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("ALL_PROXY", None)

import sys
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
# CORE MODULES
# ---------------------------
from Core.db_init import init_db
from Core.db_writer import (
    log_session_start,
    log_session_end,
    log_command_execution,
    log_error
)
from Core.command_contract import command_result

# ---------------------------
# GENERAL COMMANDS
# ---------------------------
from General_Commands.commands import (
    shell_exit,
    shell_help,
    shell_status,
    shell_clear,
    shell_history,
    shell_logs
)

# ---------------------------
# EXTERNAL COMMANDS
# ---------------------------
from External_Commands.commands import (
    shell_open,
    shell_register,
    shell_clean,
    shell_make,
    shell_read,
    shell_search,
    shell_news,
    shell_weather,
    shell_stocks,
    shell_download
)

# ---------------------------
# AI CORE (lazy import later)
# ---------------------------

# ---------------------------
# CONFIGURATION
# ---------------------------
VERSION = os.getenv("VERSION", "0.2")
USER_NAME = os.getenv("USER_NAME", "user")
DEFAULT_MODE = "rule"
TYPING_SPEED = 0.003

# ---------------------------
# RULE ENGINE MAP
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

# ============================================================
# CONTEXT
# ============================================================
def create_context():
    return {
        "session_id": int(time.time()),
        "user_name": USER_NAME,
        "mode": DEFAULT_MODE,
        "start_time": datetime.now().isoformat(),
    }

# ============================================================
# OUTPUT UTILITIES
# ============================================================
def type_print(text, delay=TYPING_SPEED):
    if not text:
        return
    for char in str(text):
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_response(result):
    if not result:
        return
    if result.get("message"):
        type_print(result["message"])
    content = result.get("data", {}).get("content")
    if isinstance(content, list):
        for line in content:
            type_print(line, delay=0.001)

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    # ---------------------------
    # BOOT
    # ---------------------------
    type_print("Initializing core systems...")
    type_print("Linking command registry...")
    type_print("Establishing local memory...\n")

    init_db()
    context = create_context()

    try:
        log_session_start(context["session_id"], context["start_time"])
    except Exception as e:
        type_print(f"Warning: session logging unavailable ({e})")

    type_print(f"Welcome, {context['user_name']}.")
    type_print("JaiShell is online.")
    type_print("Type 'help' to see available commands.\n")

    # ---------------------------
    # INTERACTIVE LOOP
    # ---------------------------
    while True:
        try:
            prompt_label = "AI" if context["mode"] == "ai" else "Rule"
            raw_input = input(f"JaiShell [{prompt_label}] ▸ ").strip()

            if not raw_input:
                continue

            # -----------------------
            # MODE SWITCHING
            # -----------------------
            if raw_input.lower() == "mode ai":
                context["mode"] = "ai"
                type_print("Switched to AI mode.")
                continue

            if raw_input.lower() == "mode rule":
                context["mode"] = "rule"
                type_print("Switched to Rule mode.")
                continue

            result = None
            function_name = None

            # -----------------------
            # RULE MODE
            # -----------------------
            if context["mode"] == "rule":
                try:
                    tokens = shlex.split(raw_input)
                    cmd = tokens[0].lower()
                    args = tokens[1:]
                except ValueError:
                    result = command_result("error", "Invalid command format.")
                    print_response(result)
                    continue

                if cmd in FUNCTION_MAP:
                    func = FUNCTION_MAP[cmd]
                    function_name = func.__name__
                    result = func(args, context)
                else:
                    result = command_result("error", f"Unknown command: {cmd}")

            # -----------------------
            # AI MODE
            # -----------------------
            else:
                from AICore import ai_engine
                function_name = "ai_engine"
                result = ai_engine(raw_input, context)

            # -----------------------
            # OUTPUT
            # -----------------------
            print_response(result)

            # -----------------------
            # LOGGING
            # -----------------------
            try:
                log_command_execution(
                    session_id=context["session_id"],
                    raw_input=raw_input,
                    status=result.get("status"),
                    mode=context["mode"],
                    function_called=function_name
                )
            except Exception as e:
                type_print(f"Logging error: {e}")

            if result.get("status") == "error":
                log_error(
                    context["session_id"],
                    "CommandError",
                    result.get("message"),
                    function_name or "unknown"
                )

            action = result.get("data", {}).get("action")
            if action == "exit":
                break
            if action == "clear_screen":
                print("\n" * 100)

        except KeyboardInterrupt:
            type_print("\nForce close detected.")
            break
        except Exception as e:
            type_print(f"Critical shell error: {e}")
            log_error(
                context["session_id"],
                "CriticalCrash",
                str(e),
                "main_loop"
            )

    # ---------------------------
    # SHUTDOWN
    # ---------------------------
    log_session_end(
        context["session_id"],
        graceful=True,
        end_timestamp=datetime.now().isoformat()
    )
    type_print("Session closed.")

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
