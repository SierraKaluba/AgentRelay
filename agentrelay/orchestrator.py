"""P1 — Coordonne cerveau + contexte + agents. Voir SPEC.md § Flux d'une session."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import brain, context, agents, logger


MAX_SUMMARY_CHARS = 2000


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _build_summary(state: dict) -> str:
    """Résumé compact des étapes passées, borné pour tenir dans le contexte du cerveau."""
    lines: list[str] = [f"Goal: {state.get('goal', '')}"]
    for i, step in enumerate(state.get("steps", []), start=1):
        agent = step.get("agent", "?")
        task = (step.get("task") or "").strip()
        out = (step.get("output") or "").strip().replace("\n", " ")
        if len(out) > 300:
            out = out[:300] + "..."
        lines.append(f"Step {i} ({agent}): {task} → {out}")
    summary = "\n".join(lines)
    if len(summary) > MAX_SUMMARY_CHARS:
        summary = summary[-MAX_SUMMARY_CHARS:]
    return summary


def _apply_decision(decision: dict, state: dict, config: dict) -> dict:
    """Écrit le contexte pour l'agent choisi et met à jour le state."""
    agent_name = decision["agent"]
    task = decision.get("task", "")
    summary = _build_summary(state)
    context.write_task_for(agent_name, task, summary)

    state["current_agent"] = agent_name
    state["pending_step"] = {
        "agent": agent_name,
        "task": task,
        "reason": decision.get("reason", ""),
        "started_at": _now_iso(),
    }
    state["last_decision"] = {
        "agent": agent_name,
        "task": task,
        "reason": decision.get("reason", ""),
        "source": decision.get("source", "brain"),
        "at": _now_iso(),
    }
    state["awaiting_user"] = not state.get("auto", False)
    state["done"] = False
    context.save_state(state)
    logger.log("ROUTE", agent_name, task[:80])
    return state


def _finish(state: dict, reason: str) -> dict:
    state["done"] = True
    state["awaiting_user"] = False
    state["current_agent"] = None
    state["pending_step"] = None
    state["last_decision"] = {"done": True, "reason": reason, "at": _now_iso()}
    context.save_state(state)
    logger.log("DONE", "", reason[:120])
    return state


def start(goal: str, config: dict, auto: bool = False) -> dict:
    """Démarre une session, demande au cerveau le premier agent."""
    state = context.init_session(goal)
    state["mode"] = "auto" if auto else "manual"
    state["auto"] = bool(auto)
    state["steps"] = []
    state["started_at"] = _now_iso()
    context.save_state(state)
    logger.log("CHECKPOINT", "", f"session started: {goal[:80]}")

    decision = brain.decide_next(state, config)
    if decision is None:
        # Cerveau indisponible : on bascule en mode manuel, l'utilisateur choisit l'agent.
        state["awaiting_user"] = True
        state["needs_manual_pick"] = True
        state["last_decision"] = {"source": "fallback", "at": _now_iso()}
        context.save_state(state)
        logger.log("ERROR", "", "brain unavailable, manual pick required")
        return state
    if decision.get("done"):
        return _finish(state, decision.get("reason", "nothing to do"))
    return _apply_decision(decision, state, config)


def step_next(output: str | None, config: dict) -> dict:
    """Consigne la sortie précédente, réinterroge le cerveau, écrit la nouvelle tâche."""
    state = context.load_state()
    pending = state.get("pending_step")
    if pending:
        step = {
            **pending,
            "output": output or "",
            "ended_at": _now_iso(),
        }
        state.setdefault("steps", []).append(step)
        context.append_history(step)
        agents.mark_done(pending["agent"], output or "")
        logger.log("HANDOFF", pending["agent"], "step done")
        state["pending_step"] = None

    # Sécurité pour le mode auto : ne pas boucler indéfiniment.
    max_steps = int(config.get("max_steps", 10))
    if len(state.get("steps", [])) >= max_steps:
        return _finish(state, f"max_steps reached ({max_steps})")

    decision = brain.decide_next(state, config)
    if decision is None:
        state["awaiting_user"] = True
        state["needs_manual_pick"] = True
        state["last_decision"] = {"source": "fallback", "at": _now_iso()}
        context.save_state(state)
        logger.log("ERROR", "", "brain unavailable, manual pick required")
        return state
    if decision.get("done"):
        return _finish(state, decision.get("reason", "done"))
    return _apply_decision(decision, state, config)


def takeover(agent_name: str, config: dict, task: str | None = None) -> dict:
    """Force manuellement un agent pour la prochaine étape (court-circuite le cerveau une fois)."""
    state = context.load_state()
    decision = {
        "agent": agent_name,
        "task": task or state.get("goal", ""),
        "reason": "manual takeover",
        "source": "user",
    }
    logger.log("BRAIN", agent_name, "manual takeover")
    return _apply_decision(decision, state, config)


def set_mode(mode: str, config: dict) -> dict:
    """Bascule entre 'manual' et 'auto'."""
    if mode not in ("manual", "auto"):
        raise ValueError("mode must be 'manual' or 'auto'")
    try:
        state = context.load_state()
    except Exception:
        state = {}
    state["mode"] = mode
    state["auto"] = mode == "auto"
    context.save_state(state)
    logger.log("CHECKPOINT", "", f"mode → {mode}")
    return state


def stop(config: dict) -> dict:
    """Termine proprement la session en cours."""
    try:
        state = context.load_state()
    except Exception:
        state = {}
    return _finish(state, "stopped by user")


def get_status(config: dict) -> dict[str, Any]:
    """État complet pour le dashboard."""
    try:
        state = context.load_state()
    except Exception:
        state = {}
    return {
        "session": {
            "goal": state.get("goal"),
            "mode": state.get("mode", "manual"),
            "current_agent": state.get("current_agent"),
            "awaiting_user": state.get("awaiting_user", False),
            "done": state.get("done", False),
            "started_at": state.get("started_at"),
            "steps_count": len(state.get("steps", [])),
        },
        "last_decision": state.get("last_decision"),
        "pending_step": state.get("pending_step"),
        "agents": agents.list_agents(config),
        "history": context.read_history(20),
        "events": logger.recent(30),
    }
