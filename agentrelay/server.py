"""FastAPI endpoints consumed by the dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import orchestrator
from .config import load_config

app = FastAPI(title="AgentRelay", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])


class StartRequest(BaseModel):
    goal: str
    auto: bool = False


class NextRequest(BaseModel):
    output: str | None = None


class ModeRequest(BaseModel):
    mode: str


def _config() -> dict[str, Any]:
    try:
        return load_config()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise HTTPException(500, str(exc)) from exc


def _run(fn, *args):
    try:
        return fn(*args)
    except (OSError, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/status")
def status():
    return orchestrator.get_status(_config())


@app.post("/api/start")
def start(body: StartRequest):
    return _run(orchestrator.start, body.goal, _config(), body.auto)


@app.post("/api/next")
def next_step(body: NextRequest):
    return _run(orchestrator.step_next, body.output, _config())


@app.post("/api/takeover/{agent}")
def takeover(agent: str):
    config = _config()
    if agent not in config["agents"]:
        raise HTTPException(404, "Unknown agent")
    return _run(orchestrator._choose, __import__("agentrelay.context", fromlist=["load_state"]).load_state(), config, agent)


@app.post("/api/mode")
def mode(body: ModeRequest):
    return _run(orchestrator.set_mode, body.mode)


@app.post("/api/stop")
def stop():
    return _run(orchestrator.stop)


@app.get("/")
def dashboard():
    page = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
    return FileResponse(page)
