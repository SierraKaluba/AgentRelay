"""Session state and agent handoff files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import project_root


def data_dir() -> Path:
    return project_root() / ".agentrelay"


def init_session(goal: str) -> dict[str, Any]:
    data_dir().mkdir(parents=True, exist_ok=True)
    state = {"goal": goal, "created_at": datetime.now(timezone.utc).isoformat(), "mode": "manual", "status": "planning", "current_agent": None, "current_task": None, "last_decision": None, "summary": "", "steps": []}
    save_state(state)
    (data_dir() / "history.jsonl").write_text("", encoding="utf-8")
    return state


def load_state() -> dict[str, Any]:
    path = data_dir() / "state.json"
    if not path.exists():
        raise FileNotFoundError("No active session. Start one with 'agentrelay start'.")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    data_dir().mkdir(parents=True, exist_ok=True)
    path = data_dir() / "state.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def write_task_for(agent: str, task: str, context: str, config: dict[str, Any] | None = None) -> None:
    settings = (config or {}).get("agents", {}).get(agent, {})
    filename = settings.get("context_file", "AGENTS.md")
    # Keep generated context confined to the project root.
    target = (project_root() / filename).resolve()
    if target.parent != project_root().resolve():
        raise ValueError("Agent context_file must be a filename in the project root.")
    state = load_state()
    content = (f"# Current task (via AgentRelay)\n\n**Goal:** {state['goal']}\n\n"
               f"**This step:** {task}\n\n**What's done:** {context or 'No previous work.'}\n\n"
               "**Instructions:** Continue from the existing work. Do not restart from scratch or contradict prior decisions.\n")
    target.write_text(content, encoding="utf-8")
    (data_dir() / "task.md").write_text(content, encoding="utf-8")


def append_history(entry: dict[str, Any]) -> None:
    data_dir().mkdir(parents=True, exist_ok=True)
    with (data_dir() / "history.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_history(n: int = 20) -> list[dict[str, Any]]:
    path = data_dir() / "history.jsonl"
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows[-n:]
