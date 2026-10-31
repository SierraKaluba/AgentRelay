"""P4 — Logs colorés terminal + journal mémoire pour le dashboard."""


def log(event: str, agent: str = "", detail: str = "") -> None:
    """Affiche une ligne colorée et stocke dans le journal mémoire (max 100)."""
    raise NotImplementedError  # TODO P4.1


def recent(n: int = 20) -> list[dict]:
    """Retourne les n derniers événements pour /api/status."""
    raise NotImplementedError  # TODO P4.1
