# ============================================================
# seed_commands.py
# ============================================================
# Seeds the authoritative command registry for JaiShell.
#
# SAFE TO RUN MULTIPLE TIMES.
# ============================================================

import json
from Core.db_connection import get_connection

# ============================================================
# COMMAND DEFINITIONS (AUTHORITATIVE)
# ============================================================

COMMANDS = [

    # ========================================================
    # SYSTEM / REGISTRY
    # ========================================================
    {
        "command_name": "open",
        "category": "system.registry",
        "description": "Open a registered application, folder, or URL.",
        "schema": {
            "name": {"type": "string", "required": True}
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "register",
        "category": "system.registry",
        "description": "Register a shortcut for opening an app, folder, or URL.",
        "schema": {
            "name": {"type": "string", "required": True},
            "path": {"type": "string", "required": True},
            "type": {
                "type": "enum",
                "values": ["program", "folder", "url"],
                "required": False
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ========================================================
    # SERVER (NO USER ARGS)
    # ========================================================
    {
        "command_name": "server-last-boot",
        "category": "server.monitoring",
        "description": "Check the last boot time of the server.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "server-state",
        "category": "server.monitoring",
        "description": "Check whether the server is reachable.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "server-ssh",
        "category": "server.control",
        "description": "Open an admin PowerShell session to manage the server.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "nextcloud-status",
        "category": "server.service",
        "description": "Check if the Nextcloud service is reachable.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "server-health",
        "category": "server.monitoring",
        "description": "Fetch CPU, RAM, GPU and temperature data from the server.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ========================================================
    # GITHUB
    # ========================================================
    {
        "command_name": "github-repos",
        "category": "github.monitoring",
        "description": "List repositories from your GitHub account.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "github-repo-summary",
        "category": "github.monitoring",
        "description": "Show a summary of a specific GitHub repository.",
        "schema": {
            "repo": {"type": "string", "required": True}
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "github-recent-commits",
        "category": "github.monitoring",
        "description": "Show recent commits of a GitHub repository.",
        "schema": {
            "repo": {"type": "string", "required": True}
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "github-repo-activity",
        "category": "github.monitoring",
        "description": "Check recent activity of a GitHub repository.",
        "schema": {
            "repo": {"type": "string", "required": True}
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "github-languages",
        "category": "github.monitoring",
        "description": "Show language breakdown of a GitHub repository.",
        "schema": {
            "repo": {"type": "string", "required": True}
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ========================================================
    # INFORMATIVE
    # ========================================================
    {
        "command_name": "news",
        "category": "info.news",
        "description": "Fetch the latest news headlines.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "weather",
        "category": "info.weather",
        "description": "Fetch weather information for a city.",
        "schema": {
            "city": {"type": "string", "required": True}
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ========================================================
    # LOCAL SYSTEM
    # ========================================================
    {
        "command_name": "system-specs",
        "category": "system.monitoring",
        "description": "Display local system specifications.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "system-uptime",
        "category": "system.monitoring",
        "description": "Show local machine uptime.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "wifi-status",
        "category": "system.monitoring",
        "description": "Show currently connected WiFi network.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ========================================================
    # AI
    # ========================================================
    {
        "command_name": "summarize",
        "category": "ai.text",
        "description": "Summarize the contents of a file using AI.",
        "schema": {
            "file_path": {"type": "string", "required": True}
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ========================================================
    # ANALYTICS
    # ========================================================
    {
        "command_name": "analytics",
        "category": "system.analytics",
        "description": "Show analytics about sessions, commands, and errors.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
]

# ============================================================
# SEED ROUTINE
# ============================================================

def seed_commands():
    conn = get_connection()
    try:
        cur = conn.cursor()
        for cmd in COMMANDS:
            cur.execute(
                """
                INSERT OR IGNORE INTO commands
                (command_name, category, description, schema_json, is_destructive, requires_confirmation)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cmd["command_name"],
                    cmd["category"],
                    cmd["description"],
                    json.dumps(cmd["schema"]),
                    cmd["is_destructive"],
                    cmd["requires_confirmation"],
                )
            )
        conn.commit()
        print(f"Seeded {len(COMMANDS)} commands into database.")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_commands()
