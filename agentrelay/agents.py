"""Agent status and optional subprocess launch helpers."""

from __future__ import annotations

import shlex
import subprocess
from typing import Any

from . import context


def list_agents(config: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        state = context.load_state()
    except FileNotFoundError:
        state = {}
    return [{"name": name, "description": item.get("description", ""),
             "status": "active" if state.get("current_agent") == name and state.get("status") == "running" else "idle",
             "launch_cmd": item.get("launch_cmd", "")}
            for name, item in config.get("agents", {}).items()]


def launch(agent: str, config: dict[str, Any]) -> int:
    item = config.get("agents", {}).get(agent)
    if not item:
        raise ValueError(f"Unknown agent: {agent}")
    command = item.get("launch_cmd")
    if not command:
        raise ValueError(f"No launch_cmd configured for {agent}")
    # Commands in trusted local config are parsed into argv; no shell is invoked.
    result = subprocess.run(shlex.split(command, posix=False), check=False)
    return result.returncode


def mark_done(agent: str, output: str) -> None:
    state = context.load_state()
    state["steps"][-1]["output"] = output
    context.save_state(state)
