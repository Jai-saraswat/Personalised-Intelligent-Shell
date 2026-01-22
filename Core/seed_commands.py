# ============================================================
# seed_commands.py
# ============================================================
# Seeds the authoritative command registry for JaiShell.
#
# This script defines:
# - What commands exist
# - How AI understands them
# - Which commands are destructive
#
# SAFE TO RUN MULTIPLE TIMES.
# ============================================================

import json
from Core.db_connection import get_connection

COMMANDS = [

    # ---------------------------
    # SYSTEM / REGISTRY
    # ---------------------------
    {
        "command_name": "open",
        "category": "system.registry",
        "description": "Open a registered application, folder, or URL.",
        "schema": {
            "name": {
                "type": "string",
                "required": True,
                "description": "Registered name to open"
            }
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

    # ---------------------------
    # FILE / SYSTEM
    # ---------------------------
    {
        "command_name": "clean",
        "category": "system.cleanup",
        "description": "Clean system folders such as temp or downloads.",
        "schema": {
            "target": {
                "type": "enum",
                "values": ["temp", "downloads"],
                "required": True
            }
        },
        "is_destructive": 1,
        "requires_confirmation": 1,
    },
    {
        "command_name": "make",
        "category": "file.create",
        "description": "Create a file or folder.",
        "schema": {
            "type": {
                "type": "enum",
                "values": ["file", "folder"],
                "required": True
            },
            "name": {
                "type": "string",
                "required": True
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "read",
        "category": "file.read",
        "description": "Read and display the contents of a file.",
        "schema": {
            "filename": {
                "type": "string",
                "required": True
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ---------------------------
    # WEB / INFO
    # ---------------------------
    {
        "command_name": "search",
        "category": "web.search",
        "description": "Search the web for information.",
        "schema": {
            "query": {
                "type": "string",
                "required": True
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "news",
        "category": "web.info",
        "description": "View the latest news headlines.",
        "schema": {},
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "weather",
        "category": "web.info",
        "description": "Check the weather for a location.",
        "schema": {
            "location": {
                "type": "string",
                "required": True
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
    {
        "command_name": "stocks",
        "category": "web.finance",
        "description": "View stock prices for a symbol.",
        "schema": {
            "symbol": {
                "type": "string",
                "required": True
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ---------------------------
    # NETWORK
    # ---------------------------
    {
        "command_name": "download",
        "category": "network.download",
        "description": "Download a file from a URL.",
        "schema": {
            "url": {
                "type": "string",
                "required": True
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },

    # ---------------------------
    # AI
    # ---------------------------
    {
        "command_name": "summarize",
        "category": "ai.text",
        "description": "Summarize text or the contents of a file.",
        "schema": {
            "text": {
                "type": "string",
                "required": True
            }
        },
        "is_destructive": 0,
        "requires_confirmation": 0,
    },
]

# ============================================================
# INSERT INTO DATABASE
# ============================================================

conn = get_connection()
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
            cmd["requires_confirmation"]
        )
    )

conn.commit()
conn.close()

print(f"Seeded {len(COMMANDS)} commands into database.")
