"""Small in-memory activity log shared by the API and CLI."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock

_events: deque[dict] = deque(maxlen=200)
_lock = Lock()


def log(event: str, agent: str = "", detail: str = "") -> None:
    item = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "agent": agent, "detail": detail}
    with _lock:
        _events.appendleft(item)


def recent(n: int = 20) -> list[dict]:
    with _lock:
        return list(_events)[:n]
