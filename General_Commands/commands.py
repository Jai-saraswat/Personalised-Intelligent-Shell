# General_Commands/commands.py
import sys
from datetime import datetime

# Adjust path to import from Core (assuming standard module structure)
# In production, relative imports or package installation is preferred.
sys.path.append("..")

from Core.command_contract import command_result
from Core.db_reader import (
    get_total_sessions,
    get_recent_commands,
    get_recent_errors,
    get_session_stats
)


# ---------------------------
# Shell Control Commands
# ---------------------------

def shell_exit(args, context):
    """
    Terminates the shell session.
    """
    return command_result(
        status="success",
        message="Exiting shell...",
        data={"action": "exit"},
        effects=["system_termination"]
    )


def shell_status(args, context):
    """
    Displays current session information.
    """
    session_id = context.get("session_id")
    user = context.get("user_name", "Unknown")
    mode = context.get("mode", "Unknown")

    # Fetch real-time stats from DB
    try:
        total_sessions = get_total_sessions()
        current_stats = get_session_stats(session_id)
        cmd_count = current_stats.get("command_count", 0)
    except Exception as e:
        return command_result(
            status="error",
            message="Failed to retrieve status.",
            error={"type": "DBError", "details": str(e)}
        )

    content = [
        "────────────────────────────────────────────────────────",
        "Shell Status",
        f"User        : {user}",
        f"Mode        : {mode}",
        f"Session ID  : {session_id}",
        f"Commands Run: {cmd_count}",
        f"Total Logins: {total_sessions}",
        "────────────────────────────────────────────────────────"
    ]

    return command_result(
        status="success",
        message="Status displayed.",
        data={"content": content}
    )


def shell_clear(args, context):
    """
    Clears the terminal screen.
    """
    return command_result(
        status="success",
        message="Screen cleared.",
        data={"action": "clear_screen"},
        effects=["ui_reset"]
    )


def shell_help(args, context):
    """
    Displays the help menu.
    """
    help_text = [
        "────────────────────────────────────────────────────────",
        "JaiShell Help Menu",
        "",
        "General:",
        "  status      - View session details",
        "  clear       - Clear screen",
        "  history     - View recent commands",
        "  logs        - View error logs",
        "  exit        - Quit application",
        "",
        "System:",
        "  clean <loc> - Clean temp/downloads",
        "  open <name> - Open app/url/folder",
        "  register    - Add new 'open' entry",
        "",
        "External:",
        "  (Add external commands here)",
        "────────────────────────────────────────────────────────"
    ]

    return command_result(
        status="success",
        message="Help displayed.",
        data={"content": help_text}
    )


# ---------------------------
# History & Logs
# ---------------------------

def shell_history(args, context):
    """
    Retrieves execution history from DB.
    """
    limit = 10
    if args and args[0].isdigit():
        limit = int(args[0])

    try:
        rows = get_recent_commands(limit)
    except Exception as e:
        return command_result(
            status="error",
            message="Failed to fetch history.",
            error={"type": "DBError", "details": str(e)}
        )

    content = ["──────────────── History ────────────────"]
    if not rows:
        content.append("No history found.")
    else:
        for prompt, status, ts in rows:
            # Simple formatting of timestamp (slice ISO string)
            time_str = ts[11:19] if len(ts) > 19 else ts
            content.append(f"[{time_str}] {prompt} ({status})")
    content.append("─────────────────────────────────────────")

    return command_result(
        status="success",
        message=f"Showed last {len(rows)} commands.",
        data={"content": content}
    )


def shell_logs(args, context):
    """
    Retrieves error logs from DB.
    """
    try:
        rows = get_recent_errors(5)
    except Exception as e:
        return command_result(
            status="error",
            message="Failed to fetch logs.",
            error={"type": "DBError", "details": str(e)}
        )

    content = ["──────────────── Error Logs ────────────────"]
    if not rows:
        content.append("No recent errors recorded.")
    else:
        for name, desc, ts in rows:
            content.append(f"[{ts}] {name}: {desc}")
    content.append("────────────────────────────────────────────")

    return command_result(
        status="success",
        message="Logs displayed.",
        data={"content": content}
    )