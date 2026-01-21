# AICore.py
import sys
import re
import json
from typing import List

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

# ---------------------------
# Core Imports
# ---------------------------
sys.path.append("Core")

from Core.server_api import extract_arguments
from Core.db_reader import get_function_schema
from Core.db_connection import get_connection
from Core.Function_Router import route_command
from Core.command_contract import command_result

from External_Commands.commands import *

load_dotenv()
USER_NAME = os.getenv("USER_NAME", "User")

# ---------------------------
# Semantic Tokenization
# ---------------------------
SEMANTIC_PATTERNS = [
    r"%[A-Za-z0-9_]+%",
    r"\d+(?:\.\d+)?%",
    r"\d+(?:\.\d+)?[KMG]B",
    r"[A-Za-z]:[\\/][^\s\"\'\)\]\}\,]+",
    r"~\/[^\s\"\'\)\]\}\,]+",
    r"\/[^\s\"\'\)\]\}\,]+",
    r"--?[A-Za-z0-9_-]+",
    r"(?![\\/])[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+",
    r"[A-Za-z0-9_]+"
]

# ---------------------------
# Command Registry
# ---------------------------
COMMAND_REGISTRY = {
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

# Function names used for embedding alignment
FUNCTION_NAMES = [
    "shell_open",
    "shell_clean",
    "shell_make",
    "shell_read",
    "shell_search",
    "shell_news",
    "shell_weather",
    "shell_stocks",
    "shell_download",
]

# ---------------------------
# Embedding Loading
# ---------------------------
def load_embeddings_from_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT function_name, embedding FROM function_embeddings")
    rows = cursor.fetchall()
    conn.close()
    return {name: np.array(json.loads(vec)) for name, vec in rows}

def initialize_embeddings():
    global FUNCTION_EMBEDDINGS, FUNCTION_EMBEDDING_MATRIX, AVAILABLE_FUNCTION_NAMES

    if FUNCTION_EMBEDDINGS is not None:
        return  # already initialized

    FUNCTION_EMBEDDINGS = load_embeddings_from_db()

    if not FUNCTION_EMBEDDINGS:
        raise RuntimeError(
            "No function embeddings found. "
            "Run db_vector_manager.py to populate function_embeddings."
        )

    AVAILABLE_FUNCTION_NAMES = [
        name for name in FUNCTION_NAMES
        if name in FUNCTION_EMBEDDINGS
    ]
    FUNCTION_EMBEDDING_MATRIX = np.vstack(
        [FUNCTION_EMBEDDINGS[name] for name in AVAILABLE_FUNCTION_NAMES]
    )


FUNCTION_EMBEDDINGS = None
FUNCTION_EMBEDDING_MATRIX = None
AVAILABLE_FUNCTION_NAMES = None

model_embedding = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---------------------------
# AI Response Generator
# ---------------------------
def response_generator(func_name, user_name, output_data):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a response formatter for a system shell.
                    Rules:
                    - You MUST use only the provided data.
                    - You MUST NOT invent facts.
                    - If data is empty, respond: "No results found."
                    - Do not explain functions.
                    - Do not mention placeholders.
                    - Output 1–2 concise sentences.
                """
            ),
            (
                "user",
                """
                Function Executed: {func_name}
                User Context: {user_name}
                Raw Output: {output_data}
                Response:
                """
            ),
        ]
    )

    llm = ChatOllama(model="phi3:mini", temperature=0)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke(
        {
            "func_name": func_name,
            "user_name": user_name,
            "output_data": str(output_data),
        }
    ).strip()

# ---------------------------
# Command Executor
# ---------------------------
def execute_with_keys(command_name, arg_keys, arg_values, context):
    if len(arg_keys) != len(arg_values):
        return command_result(
            status="error",
            message="Argument mismatch.",
            error={"type": "ArgumentError"},
        )

    kwargs = dict(zip(arg_keys, arg_values))

    # Convert kwargs to CLI-style args
    args = []
    for key, value in kwargs.items():
        if isinstance(value, bool):
            if value:
                args.append(f"--{key}")
        else:
            args.append(str(value))

    command_fn = COMMAND_REGISTRY.get(command_name)
    if not command_fn:
        return command_result(
            status="error",
            message=f"Unknown command '{command_name}'.",
            error={"type": "UnknownCommand"},
        )

    try:
        return command_fn(args, context)
    except Exception as e:
        return command_result(
            status="error",
            message=f"Command '{command_name}' failed.",
            error={"type": "ExecutionError", "details": str(e)},
        )

# ---------------------------
# NLP Utilities
# ---------------------------
def ai_core_tokenize(prompt: str) -> List[str]:
    if not prompt or not prompt.strip():
        return []

    text = prompt.lower()
    tokens = []

    for pattern in SEMANTIC_PATTERNS:
        matches = re.findall(pattern, text)
        for m in matches:
            tokens.append(m)
            text = text.replace(m, " ")

    return tokens


# def get_sentence_embedding(sentence):
#     return model_embedding.encode(sentence) if sentence else []


# def prompt_to_function_mapping(prompt):
    # initialize_embeddings()

    # prompt_embedding = get_sentence_embedding(prompt)

    # similarities = cosine_similarity(
    #     prompt_embedding.reshape(1, -1),
    #     FUNCTION_EMBEDDING_MATRIX
    # )[0]

    # best_idx = np.argmax(similarities)
    # best_score = similarities[best_idx]

    # if best_score < 0:
    #     return None
    #
    # return AVAILABLE_FUNCTION_NAMES[best_idx]



def prompt_to_arguments(prompt, function_name, schema, tokenized_prompt):
    argument_dict = extract_arguments(
        prompt=prompt,
        function_name=function_name,
        schema=schema,
        tokenized_prompt=tokenized_prompt,
    )
    return list(argument_dict.keys()), list(argument_dict.values())

# ---------------------------
# AI Engine
# ---------------------------
def ai_engine(prompt, context):
    fn_name, confirmation = route_command(prompt)
    if fn_name is None:
        return command_result(
            status="success",
            message="Hi! I can help with shell commands like cleaning files, opening folders, reading files, or checking news and weather.",
            effects=["ai_chat"]
        )

    command_name = fn_name.replace("shell_", "")

    arg_keys, arg_values = prompt_to_arguments(
        prompt=prompt,
        function_name=fn_name,
        schema=get_function_schema(fn_name),
        tokenized_prompt=ai_core_tokenize(prompt),
    )

    execution_result = execute_with_keys(
        command_name=command_name,
        arg_keys=arg_keys,
        arg_values=arg_values,
        context=context,
    )

    final_response = response_generator(
        func_name=fn_name,
        user_name=USER_NAME,
        output_data=execution_result.get("message"),
    )
    # final_response = execution_result

    return command_result(
        status="success",
        message=final_response,
        data={"input": prompt, "engine": "Echo_Placeholder_v1"},
        effects=["ai_interaction"],
    )
