"""P3 — Persistance et handoff via AGENTS.md / CLAUDE.md. Voir SPEC.md § Contexte."""


def init_session(goal: str) -> dict:
    """Crée .agentrelay/ avec state.json, task.md et history.jsonl."""
    raise NotImplementedError  # TODO P3.1


def load_state() -> dict:
    """Lit .agentrelay/state.json."""
    raise NotImplementedError  # TODO P3.1


def save_state(state: dict) -> None:
    """Écrit .agentrelay/state.json."""
    raise NotImplementedError  # TODO P3.1


def write_task_for(agent: str, task: str, context: str) -> None:
    """Écrit AGENTS.md (ou CLAUDE.md) + .agentrelay/task.md pour l'agent cible."""
    raise NotImplementedError  # TODO P3.1


def append_history(entry: dict) -> None:
    """Ajoute une ligne JSON à .agentrelay/history.jsonl."""
    raise NotImplementedError  # TODO P3.1


def read_history(n: int = 20) -> list[dict]:
    """Lit les n dernières lignes de history.jsonl."""
    raise NotImplementedError  # TODO P3.1
