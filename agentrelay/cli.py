"""P1 — Interface en ligne de commande (click). Voir SPEC.md § CLI."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

from . import orchestrator, context, logger


DEFAULT_CONFIG = Path("config/agents.yaml")
EXAMPLE_CONFIG = Path("config/agents.example.yaml")


def _load_config() -> dict:
    """Charge la config YAML (users.yaml) ou tombe sur l'exemple si absente."""
    # Import tardif pour éviter l'erreur si pyyaml n'est pas encore installé.
    import yaml
    from dotenv import load_dotenv

    load_dotenv()
    path = DEFAULT_CONFIG if DEFAULT_CONFIG.exists() else EXAMPLE_CONFIG
    if not path.exists():
        click.echo(f"✗ No config found at {DEFAULT_CONFIG} or {EXAMPLE_CONFIG}", err=True)
        sys.exit(2)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _show_decision(state: dict) -> None:
    pending = state.get("pending_step") or {}
    if state.get("done"):
        reason = (state.get("last_decision") or {}).get("reason", "done")
        click.secho(f"✓ session done: {reason}", fg="green")
        return
    if state.get("awaiting_user") and state.get("needs_manual_pick"):
        click.secho("⚠ brain unavailable — pick an agent manually with `agentrelay takeover`.", fg="yellow")
        return
    agent = pending.get("agent", "?")
    task = pending.get("task", "")
    reason = pending.get("reason", "")
    click.secho(f"→ next agent: {agent}", fg="cyan", bold=True)
    click.echo(f"  task:   {task}")
    if reason:
        click.echo(f"  reason: {reason}")
    if state.get("mode") == "manual":
        click.secho(f"  run `{agent}` in this folder, then: agentrelay next --output-text \"...\"", fg="white")


@click.group()
def cli() -> None:
    """AgentRelay — orchestrate your coding agents with Gemma as the brain."""


@cli.command()
@click.argument("goal", nargs=-1, required=True)
@click.option("--auto", is_flag=True, help="Enchaîne les agents sans intervention utilisateur.")
def start(goal: tuple[str, ...], auto: bool) -> None:
    """Démarre une nouvelle session avec le GOAL fourni."""
    config = _load_config()
    state = orchestrator.start(" ".join(goal), config, auto=auto)
    _show_decision(state)

    if auto:
        _run_auto_loop(config)


@cli.command()
@click.option("--output", "output_file", type=click.Path(exists=True, dir_okay=False), help="Fichier contenant la sortie de l'agent précédent.")
@click.option("--output-text", "output_text", type=str, help="Sortie en texte brut.")
def next(output_file: str | None, output_text: str | None) -> None:
    """Consigne la sortie et déclenche la prochaine étape."""
    config = _load_config()
    output = output_text
    if output is None and output_file:
        output = Path(output_file).read_text(encoding="utf-8")
    state = orchestrator.step_next(output, config)
    _show_decision(state)


@cli.command()
@click.argument("agent_name")
@click.option("--task", type=str, help="Tâche spécifique à donner à l'agent (sinon reprend le goal).")
def takeover(agent_name: str, task: str | None) -> None:
    """Force manuellement un agent pour la prochaine étape."""
    config = _load_config()
    state = orchestrator.takeover(agent_name, config, task=task)
    _show_decision(state)


@cli.command()
@click.argument("mode", type=click.Choice(["manual", "auto"]))
def mode(mode: str) -> None:
    """Bascule entre les modes manual et auto."""
    config = _load_config()
    orchestrator.set_mode(mode, config)
    click.secho(f"mode → {mode}", fg="cyan")


@cli.command()
def status() -> None:
    """Affiche l'état courant de la session."""
    config = _load_config()
    click.echo(json.dumps(orchestrator.get_status(config), indent=2, default=str))


@cli.command()
def stop() -> None:
    """Termine la session en cours."""
    config = _load_config()
    orchestrator.stop(config)
    click.secho("session stopped", fg="yellow")


@cli.command()
@click.option("--port", default=8000, type=int)
@click.option("--host", default="127.0.0.1", type=str)
def serve(port: int, host: str) -> None:
    """Démarre le serveur HTTP (dashboard)."""
    import uvicorn
    from . import server as _server  # noqa: F401 (chargement de l'app FastAPI)
    uvicorn.run("agentrelay.server:app", host=host, port=port, reload=False)


def _run_auto_loop(config: dict) -> None:
    """Boucle automatique : enchaîne step_next jusqu'à done ou max_steps."""
    import time

    max_steps = int(config.get("max_steps", 10))
    for _ in range(max_steps):
        state = context.load_state()
        if state.get("done") or state.get("awaiting_user"):
            break
        # En mode auto, on simule que l'agent précédent a terminé sans sortie textuelle réelle.
        # Les hooks natifs (futur) injecteront la vraie sortie.
        state = orchestrator.step_next(None, config)
        _show_decision(state)
        time.sleep(0.3)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
