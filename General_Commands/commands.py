# ============================================================
# General_Commands/commands.py
# ============================================================
# Core shell control and informational commands.
#
# These commands:
# - Never perform system actions
# - Only read from DB
# - Always return standardized command_result
#
# ============================================================

from Core.command_contract import command_result
from Core.db_reader import (
    get_total_sessions,
    get_recent_commands,
    get_recent_errors,
    get_session_stats
)

# ============================================================
# SHELL CONTROL
# ============================================================

def shell_exit(args, context):
    """
    Terminate the shell session.
    """
    return command_result(
        status="success",
        message="Exiting shell...",
        data={"action": "exit"}
    )


def shell_clear(args, context):
    """
    Clear the terminal screen.
    """
    return command_result(
        status="success",
        message="Screen cleared.",
        data={"action": "clear_screen"}
    )

# ============================================================
# STATUS
# ============================================================

def shell_status(args, context):
    """
    Display current session status.
    """
    session_id = context.get("session_id")
    user = context.get("user_name", "Unknown")
    mode = context.get("mode", "Unknown")

    try:
        total_sessions = get_total_sessions()
        stats = get_session_stats(session_id)
        command_count = stats.get("command_count", 0)
    except Exception as e:
        return command_result(
            status="error",
            message=f"Failed to retrieve status: {e}"
        )

    content = [
        "────────────────────────────────────────",
        "Shell Status",
        f"User         : {user}",
        f"Mode         : {mode}",
        f"Session ID   : {session_id}",
        f"Commands Run : {command_count}",
        f"Total Sessions: {total_sessions}",
        "────────────────────────────────────────"
    ]

    return command_result(
        status="success",
        message="Status displayed.",
        data={"content": content}
    )

# ============================================================
# HELP
# ============================================================

def shell_help(args, context):
    """
    Display help menu.
    """
    content = [
        "────────────────────────────────────────",
        "JaiShell Help Menu",
        "",
        "General:",
        "  status        - View session details",
        "  clear         - Clear screen",
        "  history [n]   - View recent commands",
        "  logs          - View error logs",
        "  exit          - Quit shell",
        "",
        "System:",
        "  open          - Open app/url/folder",
        "  register      - Register shortcut",
        "  clean         - Clean temp/downloads",
        "",
        "External:",
        "  read          - Read a file",
        "  make          - Create file/folder",
        "  search        - Web search",
        "  news          - Latest news",
        "  weather       - Weather info",
        "  stocks        - Stock prices",
        "  download      - Download a file",
        "  summarize     - Summarize text/file",
        "────────────────────────────────────────"
    ]

    return command_result(
        status="success",
        message="Help displayed.",
        data={"content": content}
    )

# ============================================================
# HISTORY
# ============================================================

def shell_history(args, context):
    """
    Show recent command history.
    """
    limit = 10
    if args and args[0].isdigit():
        limit = int(args[0])

    try:
        rows = get_recent_commands(limit)
    except Exception as e:
        return command_result(
            status="error",
            message=f"Failed to fetch history: {e}"
        )

    content = ["──────────────── History ────────────────"]

    if not rows:
        content.append("No history available.")
    else:
        for raw_input, status, mode, ts in rows:
            time_str = ts[11:19] if len(ts) >= 19 else ts
            content.append(f"[{time_str}] {raw_input} ({status}, {mode})")

    content.append("────────────────────────────────────────")

    return command_result(
        status="success",
        message=f"Showing last {len(rows)} commands.",
        data={"content": content}
    )

# ============================================================
# LOGS
# ============================================================

def shell_logs(args, context):
    """
    Show recent error logs.
    """
    try:
        rows = get_recent_errors(5)
    except Exception as e:
        return command_result(
            status="error",
            message=f"Failed to fetch logs: {e}"
        )

    content = ["──────────────── Error Logs ────────────────"]

    if not rows:
        content.append("No recent errors recorded.")
    else:
        for name, desc, origin, ts in rows:
            content.append(f"[{ts}] {name} ({origin}): {desc}")

    content.append("────────────────────────────────────────")

    return command_result(
        status="success",
        message="Logs displayed.",
        data={"content": content}
    )
