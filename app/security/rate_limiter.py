import time
from collections import defaultdict
from typing import Tuple, Dict, List
from flask import current_app

class SlidingWindowRateLimiter:
    """
    In-memory Sliding Window Rate Limiter.
    Prevents brute-force attacks on sensitive endpoints (/donor/login, /admin/login, /register).
    """

    _requests_store: Dict[str, List[float]] = defaultdict(list)

    @classmethod
    def is_rate_limited(
        cls,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Evaluates rate limit for a client identifier.
        """
        # Check Flask app config if rate limiting is enabled
        try:
            if current_app and not current_app.config.get("RATE_LIMIT_ENABLED", True):
                return False, max_requests
        except RuntimeError:
            pass

        now = time.time()
        window_start = now - window_seconds

        timestamps = cls._requests_store[identifier]
        valid_timestamps = [t for t in timestamps if t > window_start]
        cls._requests_store[identifier] = valid_timestamps

        if len(valid_timestamps) >= max_requests:
            return True, 0

        valid_timestamps.append(now)
        cls._requests_store[identifier] = valid_timestamps

        remaining = max_requests - len(valid_timestamps)
        return False, remaining

    @classmethod
    def reset(cls, identifier: str = None):
        """
        Resets rate limit counter for an identifier or clears all.
        """
        if identifier:
            cls._requests_store.pop(identifier, None)
        else:
            cls._requests_store.clear()
