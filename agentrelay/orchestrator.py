"""P1 — Coordonne cerveau + contexte + agents. Voir SPEC.md § Flux d'une session."""


def start(goal: str, config: dict, auto: bool = False) -> dict:
    """Démarre une session, demande au cerveau le premier agent."""
    raise NotImplementedError  # TODO P1.1


def step_next(output: str | None, config: dict) -> dict:
    """Consigne la sortie précédente, réinterroge le cerveau, écrit la nouvelle tâche."""
    raise NotImplementedError  # TODO P1.1


def get_status(config: dict) -> dict:
    """État complet pour le dashboard : session, agents, dernière décision, historique."""
    raise NotImplementedError  # TODO P1.1
