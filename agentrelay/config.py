"""Configuration and project path helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def project_root() -> Path:
    return Path.cwd()


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    root = project_root()
    load_dotenv(root / ".env", override=False)
    config_path = Path(path) if path else Path("config/agents.yaml")
    if not config_path.is_absolute():
        config_path = root / config_path
    if not config_path.exists():
        example = root / "config" / "agents.example.yaml"
        if example.exists() and path is None:
            config_path = example
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data.get("agents"), dict) or not data["agents"]:
        raise ValueError("Configuration must define at least one agent under 'agents'.")
    data.setdefault("brain", {})
    data.setdefault("mode_default", "manual")
    data.setdefault("max_steps", 10)
    return data


def api_key(config: dict[str, Any]) -> str | None:
    name = config.get("brain", {}).get("api_key_env", "GEMMA_API_KEY")
    return os.getenv(name)
