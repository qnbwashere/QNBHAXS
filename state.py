"""
Shared mutable state between the scheduler thread and the Telegram bot thread.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AppState:
    paused: bool = False
    running: bool = False
    next_post_at: datetime | None = None
    last_post_at: datetime | None = None
    last_subject: dict | None = None
    post_count: int = 0
    log: list[str] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    # Set this to trigger an immediate post from the bot
    force_post: threading.Event = field(default_factory=threading.Event, repr=False)

    def add_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        with self._lock:
            self.log.append(entry)
            if len(self.log) > 100:
                self.log.pop(0)
        print(entry)

    def recent_logs(self, n: int = 10) -> list[str]:
        with self._lock:
            return list(self.log[-n:])


# Single global instance shared across threads
app_state = AppState()
