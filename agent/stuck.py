from __future__ import annotations

import hashlib


def is_stuck(history: list[dict], window: int = 2) -> bool:
    """Return True if the last `window` history entries share the same URL and extracted text."""
    if len(history) < window:
        return False
    recent = history[-window:]
    keys = tuple(
        (entry["url"], hashlib.md5(entry["extracted"].encode()).hexdigest())
        for entry in recent
    )
    return len(set(keys)) == 1
