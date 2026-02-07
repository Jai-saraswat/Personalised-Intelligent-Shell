# ============================================================
# AICore.py
# ============================================================
# Orchestration layer for AI-powered command execution.
#
# Responsibilities:
# - Route user intent via semantic router
# - Extract arguments via LLM (Groq)
# - Execute ONLY registered commands
# - Enforce safety + confirmation boundaries
# - Return standardized responses
#
# This file does NOT:
# - Define commands
# - Define embeddings
# - Perform UI logic
#
# ============================================================

from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

from Core.command_contract import command_result
from Core.Function_Router import route_command
from Core.server_api import extract_arguments
from Core.db_reader import get_function_schema
from Core.db_writer import log_ai_decision

from External_Commands import commands as external_commands


# ============================================================
# COMMAND REGISTRY (STRICT, EXPLICIT)
# ============================================================

COMMAND_REGISTRY = {
    # --------------------------------------------------------
    # REGISTRY
    # --------------------------------------------------------
    "open": external_commands.shell_open,
    "register": external_commands.shell_register,

    # --------------------------------------------------------
    # SERVER
    # --------------------------------------------------------
    "server-last-boot": external_commands.shell_server_last_boot_time,
    "server-state": external_commands.shell_server_state,
    "server-ssh": external_commands.shell_server_ssh_helper,
    "nextcloud-status": external_commands.shell_server_nextcloud_status,
    "server-health": external_commands.shell_server_health,

    # --------------------------------------------------------
    # GITHUB
    # --------------------------------------------------------
    "github-repos": external_commands.shell_github_repos,
    "github-repo-summary": external_commands.shell_github_repo_summary,
    "github-recent-commits": external_commands.shell_github_recent_commits,
    "github-repo-activity": external_commands.shell_github_repo_activity,
    "github-languages": external_commands.shell_github_languages,

    # --------------------------------------------------------
    # INFORMATIVE
    # --------------------------------------------------------
    "news": external_commands.shell_news,
    "weather": external_commands.shell_weather,

    # --------------------------------------------------------
    # LOCAL SYSTEM
    # --------------------------------------------------------
    "system-specs": external_commands.shell_system_specs,
    "system-uptime": external_commands.shell_system_uptime,
    "wifi-status": external_commands.shell_current_wifi,

    # --------------------------------------------------------
    # AI / ANALYTICS
    # --------------------------------------------------------
    "summarize": external_commands.shell_summarize,
    "analytics": external_commands.shell_analytics_overview,
}


# ============================================================
# TOKENIZATION (AUXILIARY, EXPLAINABLE)
# ============================================================

def ai_core_tokenize(prompt: str) -> List[str]:
    """
    Lightweight tokenization used only as a weak signal
    for argument extraction.
    """
    if not prompt:
        return []
    return prompt.lower().split()


# ============================================================
# SAFE COMMAND EXECUTION
# ============================================================

def execute_command(
    command_name: str,
    args: List[str],
    context: Dict[str, Any]
) -> Dict:
    """
    Execute a registered command safely.
    """
    fn = COMMAND_REGISTRY.get(command_name)
    if not fn:
        return command_result(
            status="error",
            message=f"Command '{command_name}' is not executable by AI."
        )

    try:
        return fn(args, context)
    except Exception as e:
        return command_result(
            status="error",
            message=f"Execution failed: {e}"
        )


# ============================================================
# AI ENGINE (MAIN ENTRY POINT)
# ============================================================

def ai_engine(prompt: str, context: Dict[str, Any]) -> Dict:
    """
    Main AI orchestration entry point.
    """

    session_id = context.get("session_id")

    # --------------------------------------------------------
    # 1. Route intent (semantic)
    # --------------------------------------------------------
    command_id, decision, confidence = route_command(prompt)

    # Log AI decision (even if rejected)
    try:
        log_ai_decision(
            session_id=session_id,
            raw_input=prompt,
            chosen_command_id=command_id,
            confidence=confidence,
            decision_type=decision,
            reason=None
        )
    except Exception:
        # Logging failure must NEVER break execution
        pass

    if decision == "REJECT" or command_id is None:
        return command_result(
            status="success",
            message=(
                "I couldn’t confidently map that to a shell command.\n"
                "Try commands like: open, register, summarize, weather, analytics."
            ),
            confidence=confidence
        )

    # --------------------------------------------------------
    # 2. Resolve command schema
    # --------------------------------------------------------
    schema = get_function_schema(command_id)
    if not schema:
        return command_result(
            status="error",
            message="Command schema missing. Cannot execute safely.",
            confidence=confidence
        )

    command_name = schema["command_name"]

    if command_name not in COMMAND_REGISTRY:
        return command_result(
            status="error",
            message=f"Command '{command_name}' is not allowed.",
            confidence=confidence
        )

    # --------------------------------------------------------
    # 3. Confirmation gate
    # --------------------------------------------------------
    if schema.get("requires_confirmation") and decision == "CONFIRM":
        return command_result(
            status="success",
            message=(
                f"The command `{command_name}` requires confirmation.\n"
                "Please confirm before proceeding."
            ),
            confidence=confidence
        )

    # --------------------------------------------------------
    # 4. Argument extraction (Groq)
    # --------------------------------------------------------
    try:
        args_dict = extract_arguments(
            prompt=prompt,
            function_name=command_name,
            schema=schema.get("schema_json"),
            tokenized_prompt=ai_core_tokenize(prompt)
        )
    except Exception as e:
        return command_result(
            status="error",
            message=f"Argument extraction failed: {e}",
            confidence=confidence
        )

    # --------------------------------------------------------
    # 5. Normalize args → CLI-style list
    # --------------------------------------------------------
    args: List[str] = []
    for key, value in args_dict.items():
        if isinstance(value, bool):
            if value:
                args.append(f"--{key}")
        else:
            args.append(str(value))

    # --------------------------------------------------------
    # 6. Execute command
    # --------------------------------------------------------
    result = execute_command(
        command_name=command_name,
        args=args,
        context=context
    )

    # --------------------------------------------------------
    # 7. Attach AI confidence
    # --------------------------------------------------------
    result["confidence"] = confidence
    return result
