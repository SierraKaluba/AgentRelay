"""Session orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import agents, brain, context
from .logger import log, recent


def _choose(state: dict[str, Any], config: dict[str, Any], forced: str | None = None) -> dict[str, Any]:
    decision = {"agent": forced, "task": state["goal"], "reason": "Selected manually."} if forced else brain.decide_next(state, config)
    if not decision:
        decision = {"agent": next(iter(config["agents"])), "task": state["goal"] if not state["steps"] else "Continue the goal using the previous work and report the next useful result.", "reason": "Gemma unavailable; using the first configured agent as a manual fallback."}
    if decision.get("done"):
        state["status"] = "done"
        state["current_agent"] = None
        state["current_task"] = None
        state["last_decision"] = decision
        context.save_state(state)
        log("completed", detail=decision.get("reason", "Goal completed."))
        return state
    agent = decision.get("agent")
    if agent not in config["agents"]:
        raise ValueError(f"Brain chose an unknown agent: {agent}")
    if len(state["steps"]) >= int(config.get("max_steps", 10)):
        state["status"] = "limit_reached"
        context.save_state(state)
        return state
    state["current_agent"] = agent
    state["current_task"] = decision["task"]
    state["last_decision"] = decision
    state["status"] = "running" if state["mode"] == "auto" else "waiting"
    state["steps"].append({"agent": agent, "task": decision["task"], "reason": decision.get("reason", ""), "started_at": datetime.now(timezone.utc).isoformat(), "output": ""})
    context.save_state(state)
    context.write_task_for(agent, decision["task"], state.get("summary", ""), config)
    context.append_history({"type": "handoff", **decision, "timestamp": datetime.now(timezone.utc).isoformat()})
    log("handoff", agent, decision.get("reason", ""))
    if state["mode"] == "auto":
        state["status"] = "running"
        context.save_state(state)
        try:
            code = agents.launch(agent, config)
        except (OSError, ValueError) as exc:
            state["status"] = "error"
            state["error"] = str(exc)
            context.save_state(state)
            log("agent_error", agent, str(exc))
            return state
        if code:
            log("agent_exit", agent, f"Exit code {code}")
            state["status"] = "error"
            state["error"] = f"{agent} exited with code {code}"
            context.save_state(state)
    return state


def start(goal: str, config: dict[str, Any], auto: bool = False) -> dict[str, Any]:
    if not goal.strip():
        raise ValueError("Goal cannot be empty.")
    state = context.init_session(goal.strip())
    state["mode"] = "auto" if auto else config.get("mode_default", "manual")
    context.save_state(state)
    log("session_started", detail=goal.strip())
    return _choose(state, config)


def step_next(output: str | None, config: dict[str, Any]) -> dict[str, Any]:
    state = context.load_state()
    if state.get("status") in {"done", "stopped", "limit_reached"}:
        raise ValueError(f"Session is {state['status']}.")
    if state.get("current_agent") and state["steps"]:
        step = state["steps"][-1]
        step["output"] = output or ""
        step["finished_at"] = datetime.now(timezone.utc).isoformat()
        state["summary"] = (state.get("summary", "") + f"\n- {step['agent']}: {step['task']}\n  Result: {output or '(no output supplied)'}")[-12000:]
        context.append_history({"type": "result", "agent": step["agent"], "output": output or "", "timestamp": step["finished_at"]})
    state["status"] = "planning"
    context.save_state(state)
    return _choose(state, config)


def get_status(config: dict[str, Any]) -> dict[str, Any]:
    try:
        state = context.load_state()
    except FileNotFoundError:
        state = None
    return {"session": state, "agents": agents.list_agents(config), "history": context.read_history(), "activity": recent()}


def stop() -> dict[str, Any]:
    state = context.load_state()
    state["status"] = "stopped"
    context.save_state(state)
    log("session_stopped")
    return state


def set_mode(mode: str) -> dict[str, Any]:
    if mode not in {"manual", "auto"}:
        raise ValueError("Mode must be 'manual' or 'auto'.")
    state = context.load_state()
    state["mode"] = mode
    context.save_state(state)
    log("mode_changed", detail=mode)
    return state
