"""
Rate Limiting & Anti-Abuse Middleware.
Tracks per-user invocation frequencies, cooldown intervals between heavy market analyses,
and protects outbound market data APIs from throttling or bans.
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from app.config import settings
from app.logging_config import logger


class RateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(
        self,
        max_requests_per_min: int = 20,
        cooldown_seconds: float = 5.0
    ):
        self.max_requests = max_requests_per_min
        self.cooldown = cooldown_seconds
        self._user_requests: Dict[int, List[float]] = defaultdict(list)
        self._last_analysis: Dict[int, float] = {}

    def is_allowed(self, user_id: int) -> Tuple[bool, str]:
        """Check if user is permitted to make a general bot request."""
        now = time.time()
        timestamps = self._user_requests[user_id]

        # Purge timestamps older than 60s
        self._user_requests[user_id] = [t for t in timestamps if now - t < 60.0]

        if len(self._user_requests[user_id]) >= self.max_requests:
            retry_after = int(60.0 - (now - self._user_requests[user_id][0]))
            return False, f"⏳ Rate limit reached. Please wait {max(1, retry_after)} seconds."

        self._user_requests[user_id].append(now)
        return True, ""

    def check_analysis_cooldown(self, user_id: int) -> Tuple[bool, str]:
        """Check if user has satisfied the analysis cooldown between heavy market queries."""
        now = time.time()
        last_time = self._last_analysis.get(user_id, 0.0)
        elapsed = now - last_time

        if elapsed < self.cooldown:
            wait_time = int(self.cooldown - elapsed) + 1
            return False, f"⏱ Analysis cooldown active. Please wait {wait_time}s before running another analysis."

        self._last_analysis[user_id] = now
        return True, ""


# Global singleton rate limiter
rate_limiter = RateLimiter(
    max_requests_per_min=settings.RATE_LIMIT_REQUESTS_PER_MIN,
    cooldown_seconds=settings.ANALYSIS_COOLDOWN_SECONDS,
)
