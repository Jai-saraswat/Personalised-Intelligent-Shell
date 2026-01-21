# Core/CoreShell.py
import os
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
# INTERNAL MODULES
# ---------------------------
from Core.db_init import init_db
from Core.db_writer import (
    log_session_start,
    log_session_end,
    log_command,
    log_error
)
from Core.command_contract import command_result

# ---------------------------
# COMMAND MODULES
# ---------------------------
from General_Commands.commands import (
    shell_exit,
    shell_help,
    shell_status,
    shell_clear,
    shell_history,
    shell_logs
)

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

from AICore import ai_engine

# ---------------------------
# CONFIGURATION
# ---------------------------
VERSION = os.getenv("VERSION", "0.0")
USER_NAME = os.getenv("USER_NAME", "user")
DEFAULT_MODE = os.getenv("DEFAULT_MODE", "rule")
TYPING_SPEED = 0.003  # seconds per character

# ---------------------------
# FUNCTION MAP (RULE MODE)
# NOTE: Must stay logically in sync with AI command registry
# ---------------------------
FUNCTION_MAP = {
    # General
    "exit": shell_exit,
    "quit": shell_exit,
    "help": shell_help,
    "status": shell_status,
    "clear": shell_clear,
    "history": shell_history,
    "logs": shell_logs,

    # External / System
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
# CONTEXT CREATION
# ---------------------------
def create_context():
    return {
        "session_id": int(time.time()),
        "user_name": USER_NAME,
        "mode": DEFAULT_MODE,
        "start_time": datetime.now().isoformat(),
    }

# ---------------------------
# OUTPUT UTILITIES
# ---------------------------
def type_print(text, delay=TYPING_SPEED):
    """Print text with typing effect."""
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

    # Main message
    message = result.get("message")
    if message:
        type_print(message)

    # Optional list output
    data = result.get("data")
    if data and isinstance(data.get("content"), list):
        for line in data["content"]:
            type_print(line, delay=0.001)

# ---------------------------
# MAIN SHELL LOOP
# ---------------------------
def main():
    # Initialization
    type_print("Booting JaiShell Core...")
    init_db()
    context = create_context()

    # Session start logging
    try:
        log_session_start(context["session_id"])
    except Exception as e:
        type_print(f"Warning: Could not log session start: {e}")

    type_print(f"Welcome, {context['user_name']}. Shell is ready.")
    type_print("Type 'help' for commands.")

    # Main loop
    while True:
        try:
            mode_indicator = "AI" if context["mode"] == "ai" else "Rule"
            raw_input = input(f"JaiShell [{mode_indicator}] ▸ ").strip()

            if not raw_input:
                continue

            # Mode switching
            if raw_input.lower() == "mode ai":
                context["mode"] = "ai"
                type_print("Switched to AI Mode.")
                continue

            if raw_input.lower() == "mode rule":
                context["mode"] = "rule"
                type_print("Switched to Rule Mode.")
                continue

            # Tokenization
            try:
                tokens = shlex.split(raw_input)
                cmd = tokens[0].lower()
                args = tokens[1:]
            except ValueError:
                type_print("Error: Invalid command format (check quotes).")
                continue

            result = None
            function_name = None

            # ---------------------------
            # EXECUTION ENGINE
            # ---------------------------
            if context["mode"] == "rule":
                if cmd in FUNCTION_MAP:
                    func = FUNCTION_MAP[cmd]
                    function_name = func.__name__
                    result = func(args, context)
                else:
                    type_print(f"Unknown command: {cmd}")

                    log_command(
                        context["session_id"],
                        raw_input,
                        {"status": "error", "message": "Unknown command"},
                        "rule"
                    )

                    log_error(
                        context["session_id"],
                        "UnknownCommand",
                        f"Command '{cmd}' not found",
                        "main_loop"
                    )
                    continue
            else:
                function_name = "ai_engine"
                result = ai_engine(raw_input, context)

            # ---------------------------
            # OUTPUT & LOGGING
            # ---------------------------
            if result:
                print_response(result)

                log_command(
                    context["session_id"],
                    raw_input,
                    result,
                    context["mode"],
                    function_name
                )

                if result.get("status") == "error":
                    error = result.get("error", {})
                    log_error(
                        context["session_id"],
                        error.get("type", "CommandError"),
                        error.get("details", result.get("message")),
                        function_name or "unknown"
                    )

                data = result.get("data") or {}

                if data.get("action") == "exit":
                    break

                if data.get("action") == "clear_screen":
                    print("\n" * 100)


        except KeyboardInterrupt:
            type_print("\nForce Close detected.")
            break
        except Exception as e:
            type_print(f"Critical Shell Error: {e}")
            log_error(
                context["session_id"],
                "CriticalCrash",
                str(e),
                "main_loop"
            )

    # Session end
    log_session_end(context["session_id"], graceful=True)
    type_print("Session Closed.")

# ---------------------------
# ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    main()
