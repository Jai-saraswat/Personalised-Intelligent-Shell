# ============================================================
# External_Commands/commands.py
# ============================================================
# Concrete implementations of external/system commands.
#
# These commands:
# - Perform real work
# - Return standardized command_result
# - Never log directly (CoreShell handles logging)
#
# ============================================================

import os
import sys
import shutil
import webbrowser
import subprocess
import requests
from pathlib import Path

from Core.command_contract import command_result
from Core.db_writer import register_entry, unregister_entry
from Core.db_reader import get_registry_entry, get_registry_entries

# ============================================================
# OPEN / REGISTRY
# ============================================================
def shell_open(args, context):
    if not args:
        return command_result(
            "error",
            "Usage: open <name | list | remove>"
        )

    sub = args[0]

    # LIST
    if sub == "list":
        entries = get_registry_entries()
        if not entries:
            return command_result("success", "Registry is empty.")

        lines = ["Registered entries:"]
        for name, path, type_ in entries:
            lines.append(f"  {name:<15} [{type_}] → {path}")

        return command_result(
            "success",
            "Registry listed.",
            data={"content": lines}
        )

    # REMOVE
    if sub == "remove":
        if len(args) < 2:
            return command_result("error", "Usage: open remove <name>")

        unregister_entry(args[1])
        return command_result("success", f"Removed '{args[1]}' from registry.")

    # EXECUTE
    entry = get_registry_entry(sub)
    if not entry:
        return command_result("error", f"Entry '{sub}' not found.")

    path, type_ = entry

    try:
        if type_ == "url":
            webbrowser.open(path)
        elif sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        return command_result("error", f"Failed to open '{sub}': {e}")

    return command_result("success", f"Opened '{sub}'.")


def shell_register(args, context):
    if len(args) < 2:
        return command_result(
            "error",
            "Usage: register <name> <path> [program|folder|url]"
        )

    name, path = args[0], args[1]
    type_ = args[2].lower() if len(args) > 2 else "program"

    if type_ not in ("program", "folder", "url"):
        return command_result("error", "Type must be program, folder, or url.")

    register_entry(name, path, type_)
    return command_result("success", f"Registered '{name}' as {type_}.")

# ============================================================
# CLEAN
# ============================================================
def shell_clean(args, context):
    if not args:
        return command_result("error", "Usage: clean <temp|downloads>")

    target = args[0].lower()
    paths = {
        "temp": Path(os.getenv("TEMP", "")),
        "downloads": Path.home() / "Downloads"
    }

    if target not in paths or not paths[target].exists():
        return command_result("error", f"Unknown or invalid target: {target}")

    removed = 0
    for item in paths[target].iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            removed += 1
        except Exception:
            continue

    return command_result(
        "success",
        f"Cleaned {removed} items from {target}."
    )

# ============================================================
# MAKE
# ============================================================
def shell_make(args, context):
    if len(args) < 2:
        return command_result("error", "Usage: make <file|folder> <name>")

    kind, name = args[0], args[1]
    path = Path(name)

    try:
        if kind == "file":
            path.touch(exist_ok=False)
        elif kind == "folder":
            path.mkdir(parents=True, exist_ok=False)
        else:
            return command_result("error", "Type must be file or folder.")
    except Exception as e:
        return command_result("error", f"Creation failed: {e}")

    return command_result("success", f"Created {kind}: {name}")

# ============================================================
# READ
# ============================================================
def shell_read(args, context):
    if not args:
        return command_result("error", "Usage: read <filename>")

    path = Path(args[0])
    if not path.exists() or not path.is_file():
        return command_result("error", "File not found.")

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        return command_result("error", f"Read failed: {e}")

    return command_result(
        "success",
        f"Showing contents of {path.name}:",
        data={"content": lines[:200]}
    )

# ============================================================
# SEARCH / INFO
# ============================================================
def shell_search(args, context):
    if not args:
        return command_result("error", "Usage: search <query>")

    query = "+".join(args)
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return command_result("success", f"Search opened for: {' '.join(args)}")


def shell_news(args, context):
    webbrowser.open("https://news.google.com")
    return command_result("success", "Opened latest news.")


def shell_weather(args, context):
    if not args:
        return command_result("error", "Usage: weather <location>")

    loc = "+".join(args)
    webbrowser.open(f"https://www.google.com/search?q=weather+{loc}")
    return command_result("success", f"Weather lookup opened for {' '.join(args)}.")


def shell_stocks(args, context):
    if not args:
        return command_result("error", "Usage: stocks <symbol>")

    webbrowser.open(f"https://www.google.com/finance/quote/{args[0]}")
    return command_result("success", f"Stock page opened for {args[0]}.")

# ============================================================
# DOWNLOAD
# ============================================================
def shell_download(args, context):
    if not args:
        return command_result("error", "Usage: download <url>")

    url = args[0]
    filename = url.split("/")[-1]
    dest = Path.cwd() / filename

    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        return command_result("error", f"Download failed: {e}")

    return command_result("success", f"Downloaded to {dest}")

# ============================================================
# SUMMARIZE (GROQ – RAW REST)
# ============================================================
def shell_summarize(args, context):
    """
    Summarize text or a file using Groq LLM.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return command_result(
            "error",
            "GROQ_API_KEY not set in environment."
        )

    if not args:
        return command_result(
            "error",
            "Usage: summarize <text or file>"
        )

    raw_input = " ".join(args)
    path = Path(raw_input)

    try:
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
        else:
            text = raw_input
    except Exception as e:
        return command_result("error", f"Failed to read input: {e}")

    if not text.strip():
        return command_result("error", "Nothing to summarize.")

    text = text[:8000]  # safety cap

    model = os.getenv("GROQ_SUMMARY_MODEL", "openai/gpt-oss-120b")
    endpoint = os.getenv(
        "GROQ_ENDPOINT",
        "https://api.groq.com/openai/v1/chat/completions"
    )

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Summarize the following text concisely.\n"
                    "Do not add opinions or new information."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return command_result(
                "error",
                f"Groq API error {response.status_code}: {response.text}"
            )

        data = response.json()
        summary = data["choices"][0]["message"]["content"]

    except Exception as e:
        return command_result("error", f"Summarization failed: {e}")

    return command_result(
        "success",
        "Summary:",
        data={"content": summary.splitlines()}
    )
