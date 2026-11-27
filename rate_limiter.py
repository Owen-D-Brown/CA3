import time
from collections import deque


class RateLimiter:

    def __init__(self, max_attempts: int = 5, window_seconds: float = 60.0) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._windows: dict[str, deque[float]] = {}

    def allow(self, ip: str, now: float) -> bool:
        cutoff = now - self.window_seconds
        window = self._windows.get(ip)

        if window is not None:
            while window and window[0] <= cutoff:
                window.popleft()

            if not window:
                del self._windows[ip]
                window = None
            elif len(window) >= self.max_attempts:
                return False

        if window is None:
            window = deque()
            self._windows[ip] = window

        window.append(now)
        return True