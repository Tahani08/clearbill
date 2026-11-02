import base64
import json
import os

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5vl:3b")


class AIUnavailableError(RuntimeError):
    """The AI model could not be reached or gave unusable output."""


PROMPT = """You are reading a medical bill. Extract every line item exactly as printed.
- date: the service date as printed
- code: the billing code exactly as printed
- description: the service description as printed
- amount: the charge for that line as printed, like 1,850.00
- total: the total amount due as printed on the bill
Do not invent, fix, or merge lines. If a value is unreadable, use an empty string."""

SCHEMA = {
    "type": "object",
    "properties": {
        "total": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "code": {"type": "string"},
                    "description": {"type": "string"},
                    "amount": {"type": "string"},
                },
                "required": ["date", "code", "description", "amount"],
            },
        },
    },
    "required": ["total", "items"],
}


def extract_bill(image_bytes: bytes) -> dict:
    """Ask the local model to read a bill image and return structured data."""
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "format": SCHEMA,
        "options": {"temperature": 0},
        "messages": [
            {
                "role": "user",
                "content": PROMPT,
                "images": [base64.b64encode(image_bytes).decode()],
            }
        ],
    }
    try:
        res = httpx.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=300)
        res.raise_for_status()
        return json.loads(res.json()["message"]["content"])
    except httpx.HTTPError as e:
        raise AIUnavailableError(
            "Could not reach the AI model. Is Ollama running and the model downloaded?"
        ) from e
    except (KeyError, json.JSONDecodeError) as e:
        raise AIUnavailableError("The AI model returned something unreadable.") from e