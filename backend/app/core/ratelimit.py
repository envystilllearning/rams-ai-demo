"""Minimal in-memory per-user rate limiter (PRD §45).

Protects expensive endpoints (AI generation) from accidental abuse.
Not distributed — single-process demo scope. For multi-worker deploys,
replace with Redis.
"""

import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.max_calls:
            return False
        hits.append(now)
        # Opportunistic cleanup to bound memory
        if len(self._hits) > 10000:
            self._hits.clear()
        return True


# Demo policy: 10 generations per user per hour
generate_limiter = RateLimiter(max_calls=10, window_seconds=3600)
