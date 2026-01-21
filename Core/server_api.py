import requests
import json

from sympy import true, false


def extract_arguments(prompt, function_name, schema, tokenized_prompt):
    payload = {
        "model": "openai/gpt-oss-120b",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an argument extraction engine.\n"
                    "Rules:\n"
                    "- Extract ONLY arguments explicitly stated.\n"
                    "- Do not invent flags or defaults.\n"
                    "- Output valid JSON only."
                )
            },
            {
                "role": "user",
                "content": f"Command: {prompt}\nSchema: {schema}\nTokenized prompt: {tokenized_prompt}"
            }
        ]
    }
    TOKEN = "a3c9f4e8b1c0d92f6f7a1c9e4d8b5a7f9c3e2b1a4d6e8f7c2b9a1d4e5f6"
    r = requests.post(
        "http://100.115.250.33:8001/groq/chat",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json=payload,
        timeout=20
    )

    return json.loads(r.json()["content"])


schema_json = {
  "target": {
    "type": "enum",
    "values": ["downloads", "temp", "cache", "recycle_bin"],
    "required": true,
    "description": "Which system folder to clean"
  },
  "confirm": {
    "type": "boolean",
    "required": false,
    "description": "Whether user explicitly confirmed destructive action"
  }
}

# print(extract_arguments(prompt="Clean the downloads folder and i do not confirm it", function_name="clean folders", schema=schema_json))