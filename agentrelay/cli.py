"""AgentRelay command line interface."""

from __future__ import annotations

import json

import click

from . import context, orchestrator
from .config import load_config


def _print(data) -> None:
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


@click.group()
def main():
    """Coordinate coding agents while preserving project context."""


@main.command()
@click.argument("goal")
@click.option("--auto", is_flag=True, help="Launch configured agents automatically.")
def start(goal: str, auto: bool):
    _print(orchestrator.start(goal, load_config(), auto))


@main.command("next")
@click.option("--output", "output_file", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--output-text")
def next_command(output_file: str | None, output_text: str | None):
    if output_file and output_text:
        raise click.UsageError("Choose either --output or --output-text.")
    output = output_text
    if output_file:
        with open(output_file, encoding="utf-8") as handle:
            output = handle.read()
    _print(orchestrator.step_next(output, load_config()))


@main.command()
def status():
    _print(orchestrator.get_status(load_config()))


@main.command()
def stop():
    _print(orchestrator.stop())


@main.command()
@click.argument("agent")
def takeover(agent: str):
    config = load_config()
    if agent not in config["agents"]:
        raise click.ClickException(f"Unknown agent: {agent}")
    _print(orchestrator._choose(context.load_state(), config, agent))


@main.command()
@click.argument("mode", type=click.Choice(["manual", "auto"]))
def set_mode(mode: str):
    _print(orchestrator.set_mode(mode))


@main.command()
@click.option("--port", default=8000, show_default=True, type=click.IntRange(1, 65535))
@click.option("--host", default="127.0.0.1", show_default=True)
def serve(port: int, host: str):
    import uvicorn
    uvicorn.run("agentrelay.server:app", host=host, port=port)


if __name__ == "__main__":
    main()
