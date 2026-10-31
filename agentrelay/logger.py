"""P4 — Logs colorés terminal + journal mémoire pour le dashboard."""
from __future__ import annotations

import sys
from collections import deque
from datetime import datetime, timezone
from typing import Deque


# Couleurs ANSI
_RESET = "\033[0m"
_COLORS: dict[str, str] = {
    "BRAIN":      "\033[1;35m",  # magenta gras
    "RULES":      "\033[33m",    # jaune
    "ROUTE":      "\033[34m",    # bleu
    "CALL":       "\033[36m",    # cyan
    "LAUNCH":     "\033[34m",    # bleu
    "LIMIT":      "\033[31m",    # rouge
    "QUOTA":      "\033[33m",    # jaune
    "FALLBACK":   "\033[33m",    # jaune
    "HANDOFF":    "\033[36m",    # cyan
    "CHECKPOINT": "\033[35m",    # magenta
    "DONE":       "\033[32m",    # vert
    "OK":         "\033[32m",    # vert
    "ERROR":      "\033[1;31m",  # rouge gras
}

_MAX = 100
_JOURNAL: Deque[dict] = deque(maxlen=_MAX)


def _color_enabled() -> bool:
    """Désactive les couleurs si la sortie n'est pas un terminal."""
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def log(event: str, agent: str = "", detail: str = "") -> None:
    """Affiche une ligne colorée et stocke dans le journal mémoire."""
    event = (event or "").upper()
    agent = (agent or "").upper()
    detail = detail or ""
    now = datetime.now(timezone.utc)
    time_str = now.strftime("%H:%M:%S")

    entry = {
        "time": now.isoformat(timespec="seconds"),
        "event": event,
        "agent": agent.lower(),
        "detail": detail,
    }
    _JOURNAL.append(entry)

    color = _COLORS.get(event, "")
    use_color = _color_enabled() and color != ""
    if use_color:
        line = f"{time_str}  {color}[{event:<10}]{_RESET}  {agent:<10}  {detail}"
    else:
        line = f"{time_str}  [{event:<10}]  {agent:<10}  {detail}"
    try:
        print(line, flush=True)
    except Exception:
        pass


def recent(n: int = 20) -> list[dict]:
    """Retourne les n derniers événements (plus récents en tête)."""
    if n <= 0:
        return []
    items = list(_JOURNAL)[-n:]
    return list(reversed(items))


def clear() -> None:
    """Vide le journal mémoire (utile pour les tests)."""
    _JOURNAL.clear()
