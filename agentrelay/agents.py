"""P3 — Adaptateurs par agent (Claude Code, Codex, OpenCode)."""


def list_agents(config: dict) -> list[dict]:
    """Liste chaque agent avec son statut : active, idle, exhausted."""
    raise NotImplementedError  # TODO P3.2


def launch(agent: str, config: dict) -> int:
    """Lance subprocess l'agent (mode auto). Retourne le code de retour."""
    raise NotImplementedError  # TODO P3.2


def mark_done(agent: str, output: str) -> None:
    """Consigne la sortie de l'agent dans l'historique."""
    raise NotImplementedError  # TODO P3.2
