"""P1 — Serveur FastAPI pour le dashboard. Voir SPEC.md § Endpoints HTTP."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import orchestrator


app = FastAPI(title="AgentRelay", version="0.1.0")

# CORS ouvert sur /api/* pour que le dashboard (Lovable preview, ngrok, localhost:5173) puisse appeler.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_config() -> dict:
    import yaml
    from dotenv import load_dotenv

    load_dotenv()
    for name in ("config/agents.yaml", "config/agents.example.yaml"):
        path = Path(name)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    raise HTTPException(500, "no config file found (expected config/agents.yaml)")


@app.get("/api/status")
def get_status() -> dict[str, Any]:
    config = _load_config()
    return orchestrator.get_status(config)


@app.post("/api/start")
async def start_session(request: Request) -> dict[str, Any]:
    body = await request.json()
    goal = (body or {}).get("goal", "").strip()
    auto = bool((body or {}).get("auto", False))
    if not goal:
        raise HTTPException(400, "goal is required")
    config = _load_config()
    state = orchestrator.start(goal, config, auto=auto)
    return {"ok": True, "state": state}


@app.post("/api/next")
async def next_step(request: Request) -> dict[str, Any]:
    body: dict[str, Any] = {}
    try:
        body = await request.json()
    except Exception:
        body = {}
    output = (body or {}).get("output")
    config = _load_config()
    state = orchestrator.step_next(output, config)
    return {"ok": True, "state": state}


@app.post("/api/takeover/{agent}")
async def takeover_agent(agent: str, request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        body = {}
    task = (body or {}).get("task")
    config = _load_config()
    state = orchestrator.takeover(agent, config, task=task)
    return {"ok": True, "state": state}


@app.post("/api/mode")
async def change_mode(request: Request) -> dict[str, Any]:
    body = await request.json()
    mode = (body or {}).get("mode")
    if mode not in ("manual", "auto"):
        raise HTTPException(400, "mode must be 'manual' or 'auto'")
    config = _load_config()
    state = orchestrator.set_mode(mode, config)
    return {"ok": True, "state": state}


@app.post("/api/stop")
def stop_session() -> dict[str, Any]:
    config = _load_config()
    state = orchestrator.stop(config)
    return {"ok": True, "state": state}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Gestion simple des erreurs non prévues : format JSON lisible par le dashboard.
@app.exception_handler(Exception)
async def _global_exception_handler(_request: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
    return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})
