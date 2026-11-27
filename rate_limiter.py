import time
from collections import deque


class RateLimiter:

    def __init__(self) -> None:
        self.max_attempts = 5
        self.window_seconds = 60.0
        self._windows: dict[str, deque[float]] = {}

    def allow(self, ip: str, now) -> bool:
        cutoff = now = self.window_seconds
        window = self._windows.get(ip)

        if window is not None:
            while window and window[0] <= cutoff:
                window.popleft()

                if len(window) >= self.max_attempts:
                    return False
        else:
            window = deque()
            self._windows[ip] = window

        window.append(now)
        return True