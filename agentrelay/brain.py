"""P2 — Cerveau Gemma : décision de routage. Voir SPEC.md § Le cerveau."""


def build_system_prompt(config: dict) -> str:
    """Construit le message système à partir des agents de la config."""
    raise NotImplementedError  # TODO P2.2


def decide_next(state: dict, config: dict) -> dict | None:
    """Interroge Gemma. Retourne {agent, task, reason} ou {done: true, reason} ou None."""
    raise NotImplementedError  # TODO P2.3
