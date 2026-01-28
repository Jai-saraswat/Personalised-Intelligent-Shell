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
import requests
import webbrowser
import subprocess
import platform
from pathlib import Path

from Core.command_contract import command_result
from Core.db_writer import register_entry, unregister_entry
from Core.db_reader import get_registry_entry, get_registry_entries

# ============================================================
# GLOBAL SERVER CONFIG (v1.0)
# ============================================================
SERVER_USER = "nextcloud"
SERVER_IP = "192.168.50.102"
NEXTCLOUD_PING_TARGET = SERVER_IP

# ============================================================
# GITHUB GLOBAL VARIABLES
# ============================================================

GITHUB_API_BASE = "https://api.github.com"
GITHUB_USERNAME = "Jai-saraswat"
DEFAULT_COMMIT_COUNT = 5

# ============================================================
# Helper Function
# ============================================================

def _github_headers():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

# ============================================================
# OPEN / REGISTRY
# ============================================================

def shell_open(args, context):
    if not args:
        return command_result("error", "Usage: open <name | list | remove>")

    sub = args[0]

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

    if sub == "remove":
        if len(args) < 2:
            return command_result("error", "Usage: open remove <name>")

        unregister_entry(args[1])
        return command_result("success", f"Removed '{args[1]}' from registry.")

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
    except Exception:
        return command_result("error", f"Failed to open '{sub}'.")

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
# SERVER COMMANDS
# ============================================================

# ------------------------------------------------------------
# Server: Last Boot Time
# ------------------------------------------------------------

def shell_server_last_boot_time(args, context):
    result = subprocess.run(
        ["ssh", f"{SERVER_USER}@{SERVER_IP}", "uptime -s"],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode != 0:
        return command_result(
            "error",
            "Unable to fetch server boot time. Server may be unreachable."
        )

    return command_result(
        "success",
        "Server last boot time:",
        data={"content": [result.stdout.strip()]}
    )

# ------------------------------------------------------------
# Server: State (Ping)
# ------------------------------------------------------------

def shell_server_state(args, context):
    param = "-n" if platform.system().lower() == "windows" else "-c"

    try:
        result = subprocess.run(
            ["ping", param, "1", SERVER_IP],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )

        state = (
            "Server is reachable (ON)"
            if result.returncode == 0
            else "Server is unreachable (OFF)"
        )

        return command_result(
            "success",
            "Server state:",
            data={"content": [state]}
        )

    except Exception:
        return command_result("error", "Unable to determine server state.")

# ------------------------------------------------------------
# Server: SSH Helper (Launcher Only)
# ------------------------------------------------------------

def shell_server_ssh_helper(args, context):
    if platform.system() != "Windows":
        return command_result(
            "error",
            "This command is supported only on Windows hosts."
        )

    try:
        subprocess.run(
            [
                "powershell",
                "-Command",
                "Start-Process powershell -Verb RunAs "
                "-ArgumentList '-NoExit','-Command','start-nextcloud'"
            ],
            check=True
        )

        return command_result(
            "success",
            "Server wake command executed:",
            data={"content": ["Admin PowerShell opened with start-nextcloud."]}
        )

    except subprocess.CalledProcessError:
        return command_result("error", "Failed to launch admin PowerShell.")

# ------------------------------------------------------------
# Server: Nextcloud Status (Ping Only)
# ------------------------------------------------------------

def shell_server_nextcloud_status(args, context):
    param = "-n" if platform.system().lower() == "windows" else "-c"

    try:
        result = subprocess.run(
            ["ping", param, "1", NEXTCLOUD_PING_TARGET],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )

        status = (
            "Nextcloud server is reachable (ONLINE)"
            if result.returncode == 0
            else "Nextcloud server is unreachable (OFFLINE)"
        )

        return command_result(
            "success",
            "Nextcloud status:",
            data={"content": [status]}
        )

    except Exception:
        return command_result("error", "Unable to determine Nextcloud status.")

# ------------------------------------------------------------
# Server: Health Snapshot (CPU / RAM / GPU / Temps)
# ------------------------------------------------------------

def shell_server_health(args, context):
    """
    Fetches CPU, RAM, GPU (if available), and temperature info.
    Missing components are reported as 'Unavailable'.
    """

    remote_cmd = (
        "echo CPU; top -bn1 | grep 'Cpu(s)' || echo 'Unavailable'; "
        "echo MEM; free -m | grep Mem || echo 'Unavailable'; "
        "echo GPU; nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null || echo 'Unavailable'; "
        "echo TEMP; sensors 2>/dev/null | grep -m1 -E 'Core|Package' || echo 'Unavailable'"
    )

    result = subprocess.run(
        ["ssh", f"{SERVER_USER}@{SERVER_IP}", remote_cmd],
        capture_output=True,
        text=True,
        timeout=15
    )

    if result.returncode != 0:
        return command_result(
            "error",
            "Unable to fetch server health data."
        )

    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]

    content = []
    it = iter(lines)
    for label in it:
        try:
            value = next(it)
        except StopIteration:
            value = "Unavailable"
        content.append(f"{label}: {value}")

    return command_result(
        "success",
        "Server health snapshot:",
        data={"content": content}
    )

def shell_github_repos(args, context):
    headers = _github_headers()
    if not headers:
        return command_result("error", "GITHUB_TOKEN not set in environment.")

    url = f"{GITHUB_API_BASE}/users/{GITHUB_USERNAME}/repos?per_page=100"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return command_result("error", "Failed to fetch repositories.")

        repos = resp.json()
        if not repos:
            return command_result(
                "success",
                "GitHub repositories:",
                data={"content": ["No repositories found."]}
            )

        lines = []
        for r in repos:
            name = r.get("name")
            desc = r.get("description") or "No description"
            stars = r.get("stargazers_count", 0)
            lang = r.get("language") or "Unknown"
            vis = "Private" if r.get("private") else "Public"
            updated = r.get("updated_at", "")[:10]

            lines.append(
                f"{name} — ⭐ {stars} | {lang} | {vis} | Updated {updated}"
            )

        return command_result(
            "success",
            "GitHub repositories:",
            data={"content": lines}
        )

    except Exception:
        return command_result("error", "Unable to fetch GitHub repositories.")

def shell_github_repo_summary(args, context):
    if not args:
        return command_result("error", "Usage: github-repo-summary <repo-name>")

    repo = args[0]
    headers = _github_headers()
    if not headers:
        return command_result("error", "GITHUB_TOKEN not set in environment.")

    url = f"{GITHUB_API_BASE}/repos/{GITHUB_USERNAME}/{repo}"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return command_result("error", "Repository not found under your account.")
        if resp.status_code != 200:
            return command_result("error", "Failed to fetch repository details.")

        r = resp.json()

        content = [
            f"Description     : {r.get('description') or 'None'}",
            f"Stars           : {r.get('stargazers_count', 0)}",
            f"Forks           : {r.get('forks_count', 0)}",
            f"Open Issues     : {r.get('open_issues_count', 0)}",
            f"Default Branch  : {r.get('default_branch')}",
            f"Primary Language: {r.get('language') or 'Unknown'}",
            f"License         : {(r.get('license') or {}).get('name', 'None')}",
            f"Last Updated    : {r.get('updated_at')[:10]}",
        ]

        return command_result(
            "success",
            f"Repository summary — {repo}:",
            data={"content": content}
        )

    except Exception:
        return command_result("error", "Unable to fetch repository summary.")

def shell_github_recent_commits(args, context):
    if not args:
        return command_result("error", "Usage: github-recent-commits <repo-name>")

    repo = args[0]
    headers = _github_headers()
    if not headers:
        return command_result("error", "GITHUB_TOKEN not set in environment.")

    url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_USERNAME}/{repo}/commits"
        f"?per_page={DEFAULT_COMMIT_COUNT}"
    )

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return command_result("error", "Repository not found under your account.")
        if resp.status_code != 200:
            return command_result("error", "Failed to fetch commits.")

        commits = resp.json()
        if not commits:
            return command_result(
                "success",
                "Recent commits:",
                data={"content": ["No commits found."]}
            )

        lines = []
        for c in commits:
            msg = c["commit"]["message"].split("\n")[0]
            author = c["commit"]["author"]["name"]
            date = c["commit"]["author"]["date"][:10]
            lines.append(f"{msg} — {author} ({date})")

        return command_result(
            "success",
            f"Recent commits — {repo}:",
            data={"content": lines}
        )

    except Exception:
        return command_result("error", "Unable to fetch recent commits.")

def shell_github_repo_activity(args, context):
    if not args:
        return command_result("error", "Usage: github-repo-activity <repo-name>")

    repo = args[0]
    headers = _github_headers()
    if not headers:
        return command_result("error", "GITHUB_TOKEN not set in environment.")

    url = f"{GITHUB_API_BASE}/repos/{GITHUB_USERNAME}/{repo}/commits?per_page=1"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return command_result("error", "Unable to determine repo activity.")

        commit = resp.json()[0]
        date = commit["commit"]["author"]["date"]

        return command_result(
            "success",
            "Repository activity:",
            data={"content": [f"Last commit on {date[:10]} (ACTIVE)"]}
        )

    except Exception:
        return command_result("error", "Unable to determine repo activity.")

def shell_github_languages(args, context):
    if not args:
        return command_result("error", "Usage: github-languages <repo-name>")

    repo = args[0]
    headers = _github_headers()
    if not headers:
        return command_result("error", "GITHUB_TOKEN not set in environment.")

    url = f"{GITHUB_API_BASE}/repos/{GITHUB_USERNAME}/{repo}/languages"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return command_result("error", "Unable to fetch language data.")

        data = resp.json()
        total = sum(data.values())
        if total == 0:
            return command_result(
                "success",
                "Languages used:",
                data={"content": ["No language data available."]}
            )

        lines = []
        for lang, count in data.items():
            percent = (count / total) * 100
            lines.append(f"{lang}: {percent:.1f}%")

        return command_result(
            "success",
            f"Languages — {repo}:",
            data={"content": lines}
        )

    except Exception:
        return command_result("error", "Unable to fetch language breakdown.")

# ============================================================
# INFORMATIVE COMMANDS (NEWS / WEATHER)
# ============================================================

def shell_news(args, context):
    api_key = os.getenv("NEWS_DATA_IO_API")
    if not api_key:
        return command_result("error", "NEWS_DATA_IO_API not set in environment.")

    url = (
        "https://newsdata.io/api/1/news"
        f"?apikey={api_key}&language=en"
    )

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return command_result("error", "Failed to fetch news.")

        data = resp.json().get("results", [])
        if not data:
            return command_result(
                "success",
                "Latest news:",
                data={"content": ["No news articles available."]}
            )

        lines = []
        for article in data[:5]:
            title = article.get("title", "Untitled")
            source = article.get("source_id", "Unknown")
            lines.append(f"{title} — {source}")

        return command_result(
            "success",
            "Latest news:",
            data={"content": lines}
        )

    except Exception:
        return command_result("error", "Unable to fetch news.")


def shell_weather(args, context):
    if not args:
        return command_result("error", "Usage: weather <city>")

    api_key = os.getenv("OPEN_WEATHER_API")
    if not api_key:
        return command_result("error", "OPEN_WEATHER_API not set in environment.")

    city = " ".join(args)
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return command_result("error", "Failed to fetch weather data.")

        w = resp.json()
        content = [
            f"Location : {w['name']}",
            f"Condition: {w['weather'][0]['description']}",
            f"Temp     : {w['main']['temp']} °C",
            f"Humidity : {w['main']['humidity']}%",
        ]

        return command_result(
            "success",
            f"Weather — {city}:",
            data={"content": content}
        )

    except Exception:
        return command_result("error", "Unable to fetch weather information.")

# ============================================================
# LOCAL SYSTEM MONITORING (BASIC)
# ============================================================

def shell_system_specs(args, context):
    try:
        content = [
            f"OS        : {platform.system()} {platform.release()}",
            f"Processor : {platform.processor()}",
            f"Machine   : {platform.machine()}",
            f"Python    : {platform.python_version()}",
        ]

        return command_result(
            "success",
            "System specifications:",
            data={"content": content}
        )

    except Exception:
        return command_result("error", "Unable to fetch system specs.")


def shell_system_uptime(args, context):
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(
                ["net", "stats", "workstation"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.splitlines():
                if "Statistics since" in line:
                    uptime = line.strip()
                    break
            else:
                uptime = "Unavailable"
        else:
            uptime = subprocess.run(
                ["uptime", "-p"],
                capture_output=True,
                text=True
            ).stdout.strip()

        return command_result(
            "success",
            "System uptime:",
            data={"content": [uptime]}
        )

    except Exception:
        return command_result("error", "Unable to fetch system uptime.")


def shell_current_wifi(args, context):
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True
            )
            ssid = next(
                (l.split(":")[1].strip() for l in result.stdout.splitlines() if "SSID" in l and "BSSID" not in l),
                "Unknown"
            )
        else:
            ssid = subprocess.run(
                ["iwgetid", "-r"],
                capture_output=True,
                text=True
            ).stdout.strip() or "Unknown"

        return command_result(
            "success",
            "Current WiFi:",
            data={"content": [f"Connected SSID: {ssid}"]}
        )

    except Exception:
        return command_result("error", "Unable to determine WiFi status.")

# ============================================================
# SUMMARIZE (FILE → GROQ)
# ============================================================

def shell_summarize(args, context):
    if not args:
        return command_result("error", "Usage: summarize <file-path>")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return command_result("error", "GROQ_API_KEY not set in environment.")

    path = Path(args[0])
    if not path.exists() or not path.is_file():
        return command_result("error", "File not found.")

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:8000]
    except Exception:
        return command_result("error", "Unable to read file.")

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": "Summarize the following text concisely."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.2
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        if resp.status_code != 200:
            return command_result("error", "Summarization failed.")

        summary = resp.json()["choices"][0]["message"]["content"]

        return command_result(
            "success",
            "Summary:",
            data={"content": summary.splitlines()}
        )

    except Exception:
        return command_result("error", "Unable to summarize content.")

# ============================================================
# ANALYTICS (DATABASE-DRIVEN)
# ============================================================

def shell_analytics_overview(args, context):
    try:
        from Core.db_reader import (
            get_total_sessions,
            get_recent_commands,
            get_recent_errors
        )

        sessions = get_total_sessions()
        commands = len(get_recent_commands(100))
        errors = len(get_recent_errors(100))

        content = [
            f"Total sessions : {sessions}",
            f"Commands logged: {commands}",
            f"Errors recorded: {errors}",
        ]

        return command_result(
            "success",
            "System analytics:",
            data={"content": content}
        )

    except Exception:
        return command_result("error", "Unable to fetch analytics.")
