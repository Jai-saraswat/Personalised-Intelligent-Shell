# External_Commands/commands.py
import sys
import os
import webbrowser
import subprocess
from pathlib import Path

# Adjust path to import from Core
sys.path.append("..")

from Core.command_contract import command_result
from Core.db_writer import register_entry, unregister_entry
from Core.db_reader import get_registry_entry, get_registry_entries


# ---------------------------
# 1. REAL IMPLEMENTATIONS
# ---------------------------

def shell_open(args, context):
    """
    [REAL] Opens a registered application, URL, or folder.
    """
    if not args:
        return command_result(
            status="error",
            message="Usage: open <name | list | remove>",
            error={"type": "MissingArgument", "details": "Target required."}
        )

    subcommand = args[0]

    # --- LIST ---
    if subcommand == "list":
        entries = get_registry_entries()
        content = ["Registered Entries:"]
        for name, path, type_ in entries:
            content.append(f"  {name:<15} [{type_}] -> {path}")
        return command_result(
            status="success",
            message="Registry listed.",
            data={"content": content}
        )

    # --- REMOVE ---
    if subcommand == "remove":
        if len(args) < 2:
            return command_result(
                status="error",
                message="Usage: open remove <name>",
                error={"type": "MissingArgument", "details": "Name required."}
            )
        name_to_remove = args[1]
        unregister_entry(name_to_remove)
        return command_result(
            status="success",
            message=f"Removed '{name_to_remove}' from registry.",
            effects=["registry_modification"]
        )

    # --- EXECUTE ---
    entry = get_registry_entry(subcommand)
    if not entry:
        return command_result(
            status="error",
            message=f"Entry '{subcommand}' not found.",
            error={"type": "RegistryError", "details": "Not registered."}
        )

    path, type_ = entry

    try:
        if type_ == "url":
            webbrowser.open(path)
        elif type_ in ["program", "folder"]:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

    except Exception as e:
        return command_result(
            status="error",
            message=f"Failed to launch '{subcommand}'.",
            error={"type": "ExecutionError", "details": str(e)}
        )

    return command_result(
        status="success",
        message=f"Opened {subcommand}.",
        data={"name": subcommand, "type": type_, "path": path},
        effects=["process_launch"]
    )


def shell_register(args, context):
    """
    [REAL] Registers a new entry for the 'open' command.
    """
    if len(args) < 2:
        return command_result(
            status="error",
            message="Usage: register <name> <path> [program|url|folder]",
            error={"type": "MissingArgument", "details": "Name and path required."}
        )

    name = args[0]
    path = args[1]
    type_ = args[2].lower() if len(args) > 2 else "program"

    if type_ not in ["program", "url", "folder"]:
        return command_result(
            status="error",
            message="Invalid type.",
            error={"type": "InvalidArgument", "details": "Must be program, url, or folder."}
        )

    try:
        register_entry(name, path, type_)
    except Exception as e:
        return command_result(
            status="error",
            message="Registration failed.",
            error={"type": "DBError", "details": str(e)}
        )

    return command_result(
        status="success",
        message=f"Registered '{name}' as {type_}.",
        data={"name": name, "path": path, "type": type_},
        effects=["registry_modification"]
    )


# ---------------------------
# 2. PLACEHOLDERS (Scalable Structure)
# ---------------------------

def shell_clean(args, context):
    if not args:
        return command_result("error", "Usage: clean <temp|downloads>", error={"type": "MissingArgument"})

    target = args[0]
    # TODO: Implement cleaning logic

    return command_result("success", f"[PLACEHOLDER] Clean called on {target}.")


def shell_make(args, context):
    if len(args) < 2:
        return command_result("error", "Usage: make <file|folder> <name>", error={"type": "MissingArgument"})

    type_, name = args[0], args[1]
    # TODO: Implement creation logic

    return command_result("success", f"[PLACEHOLDER] Make called for {type_}: {name}")


def shell_read(args, context):
    if not args:
        return command_result("error", "Usage: read <filename>", error={"type": "MissingArgument"})

    filename = args[0]
    # TODO: Implement reading logic

    return command_result("success", f"[PLACEHOLDER] Read called for {filename}")


def shell_search(args, context):
    if not args:
        return command_result("error", "Usage: search <query>", error={"type": "MissingArgument"})

    query = " ".join(args)
    # TODO: Implement web search logic

    return command_result("success", f"[PLACEHOLDER] Search called for: {query}")


def shell_news(args, context):
    # Args optional for news
    # TODO: Implement news fetcher
    return command_result("success", "[PLACEHOLDER] News feed fetched.")


def shell_weather(args, context):
    if not args:
        return command_result("error", "Usage: weather <location>", error={"type": "MissingArgument"})

    location = args[0]
    # TODO: Implement weather API

    return command_result("success", f"[PLACEHOLDER] Weather for {location}.")


def shell_stocks(args, context):
    if not args:
        return command_result("error", "Usage: stocks <symbol>", error={"type": "MissingArgument"})

    symbol = args[0]
    # TODO: Implement stock API

    return command_result("success", f"[PLACEHOLDER] Stocks for {symbol}.")


def shell_download(args, context):
    if not args:
        return command_result("error", "Usage: download <url>", error={"type": "MissingArgument"})

    url = args[0]
    # TODO: Implement downloader

    return command_result("success", f"[PLACEHOLDER] Download queued for {url}.")