import time
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str) -> None:
        current_time = time.time()

        if user_id not in self.user_requests:
            return

        window = self.user_requests[user_id]
        cutoff = current_time - self.window_size

        while window and window[0] <= cutoff:
            window.popleft()

        if not window:
            del self.user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        self._cleanup_window(user_id)

        if user_id not in self.user_requests:
            return True

        return len(self.user_requests[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        self._cleanup_window(user_id)

        current_time = time.time()

        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()

        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(current_time)
            return True

        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        self._cleanup_window(user_id)

        if user_id not in self.user_requests:
            return 0.0

        window = self.user_requests[user_id]

        if len(window) < self.max_requests:
            return 0.0

        current_time = time.time()
        return max(0.0, window[0] + self.window_size - current_time)