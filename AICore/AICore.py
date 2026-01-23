# ============================================================
# AICore.py
# ============================================================
# Orchestration layer for AI-powered command execution.
#
# Responsibilities:
# - Route user intent via semantic router
# - Extract arguments via LLM (Groq)
# - Execute ONLY registered commands
# - Format final response
#
# This file does NOT:
# - Define commands
# - Define embeddings
# - Access DB directly (except via readers)
# - Perform UI logic
#
# ============================================================

from typing import List

from Core.command_contract import command_result
from Core.Function_Router import route_command
from Core.server_api import extract_arguments
from Core.db_reader import get_function_schema
from External_Commands import commands as external_commands
from dotenv import load_dotenv
load_dotenv()
# ============================================================
# COMMAND REGISTRY (STRICT)
# ============================================================
# AI can ONLY execute commands defined here.
COMMAND_REGISTRY = {
    "open": external_commands.shell_open,
    "register": external_commands.shell_register,
    "clean": external_commands.shell_clean,
    "make": external_commands.shell_make,
    "read": external_commands.shell_read,
    "search": external_commands.shell_search,
    "news": external_commands.shell_news,
    "weather": external_commands.shell_weather,
    "stocks": external_commands.shell_stocks,
    "download": external_commands.shell_download,
    "summarize": external_commands.shell_summarize,
}

# ============================================================
# TOKENIZATION (LIGHTWEIGHT, EXPLAINABLE)
# ============================================================
def ai_core_tokenize(prompt: str) -> List[str]:
    """
    Simple semantic tokenization.
    Used only as auxiliary signal for argument extraction.
    """
    if not prompt:
        return []

    return prompt.lower().split()

# ============================================================
# COMMAND EXECUTION
# ============================================================
def execute_command(
    command_name: str,
    args: List[str],
    context: dict
):
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
# AI ENGINE (MAIN ENTRY)
# ============================================================
def ai_engine(prompt: str, context: dict):
    """
    Main AI orchestration entry point.
    """
    # --------------------------------------------------------
    # 1. Route intent
    # --------------------------------------------------------
    command_id, decision, confidence = route_command(prompt)

    if decision == "REJECT" or command_id is None:
        return command_result(
            status="success",
            message=(
                "I couldn’t confidently map that to a shell command.\n"
                "Try commands like: open, clean, read, summarize, weather."
            ),
            confidence=confidence
        )

    # --------------------------------------------------------
    # 2. Resolve command name & schema
    # --------------------------------------------------------
    schema = get_function_schema(command_id)
    if not schema:
        return command_result(
            status="error",
            message="Command schema missing. Cannot execute safely.",
            confidence=confidence
        )

    command_name = schema.get("command_name")
    if command_name not in COMMAND_REGISTRY:
        return command_result(
            status="error",
            message=f"Command '{command_name}' is not allowed.",
            confidence=confidence
        )

    # --------------------------------------------------------
    # 3. Confirmation gate (destructive commands)
    # --------------------------------------------------------
    if schema.get("requires_confirmation") and decision == "CONFIRM":
        return command_result(
            status="success",
            message=(
                f"The command `{command_name}` requires confirmation.\n"
                f"Please confirm before proceeding."
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

    # Convert extracted args → CLI-style args
    args = []
    for key, value in args_dict.items():
        if isinstance(value, bool):
            if value:
                args.append(f"--{key}")
        else:
            args.append(str(value))

    # --------------------------------------------------------
    # 5. Execute command
    # --------------------------------------------------------
    result = execute_command(
        command_name=command_name,
        args=args,
        context=context
    )

    # --------------------------------------------------------
    # 6. Attach confidence & return
    # --------------------------------------------------------
    result["confidence"] = confidence
    return result
