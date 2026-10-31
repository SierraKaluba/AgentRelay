"""Gemma decision client using Google's OpenAI-compatible endpoint."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from .config import api_key


def build_system_prompt(config: dict[str, Any]) -> str:
    agents = config.get("agents", {})
    choices = "\n".join(f"- {name}: {item.get('description', '')}" for name, item in agents.items())
    return ("You coordinate coding agents. Pick one agent for the next concrete step, using prior work. "
            "Reply with exactly one JSON object: {\"agent\": name, \"task\": string, \"reason\": string}; "
            "or {\"done\": true, \"reason\": string} if the goal is complete.\nAvailable agents:\n" + choices)


def _parse_response(text: str, known_agents: set[str]) -> dict[str, Any] | None:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate, flags=re.IGNORECASE)
    try:
        result = json.loads(candidate)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(result, dict):
        return None
    if result.get("done") is True:
        return {"done": True, "reason": str(result.get("reason", "Goal completed."))}
    agent, task = result.get("agent"), result.get("task")
    if agent not in known_agents or not isinstance(task, str) or not task.strip():
        return None
    return {"agent": agent, "task": task.strip(), "reason": str(result.get("reason", ""))}


def decide_next(state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any] | None:
    brain = config.get("brain", {})
    key = api_key(config)
    if not key:
        return None
    state_text = json.dumps(state, ensure_ascii=False)
    limit = int(brain.get("max_input_chars", 6000))
    body = {"model": brain.get("model", "gemma-3-27b-it"), "temperature": 0,
            "max_tokens": 300, "messages": [
                {"role": "system", "content": build_system_prompt(config)},
                {"role": "user", "content": "Session state (JSON):\n" + state_text[:limit]},
            ]}
    base_url = brain.get("base_url", "https://generativelanguage.googleapis.com/v1beta/openai").rstrip("/")
    try:
        response = httpx.post(f"{base_url}/chat/completions", json=body,
                              headers={"Authorization": f"Bearer {key}"}, timeout=float(brain.get("timeout", 30)))
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]
        return _parse_response(text, set(config.get("agents", {})))
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None
