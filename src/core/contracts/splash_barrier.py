from __future__ import annotations

from dataclasses import dataclass
from threading import Event


@dataclass(slots=True)
class SplashLockBarrier:
    _ready_event: Event
    min_duration_elapsed: bool = False
    bootstrap_complete: bool = False
    fallback_triggered: bool = False

    @classmethod
    def create(cls) -> "SplashLockBarrier":
        return cls(_ready_event=Event())

    def mark_min_duration_elapsed(self) -> None:
        self.min_duration_elapsed = True
        self._try_open()

    def mark_bootstrap_complete(self) -> None:
        self.bootstrap_complete = True
        self._try_open()

    def mark_fallback(self) -> None:
        self.fallback_triggered = True
        self._try_open()

    def wait(self, timeout: float | None = None) -> bool:
        return self._ready_event.wait(timeout)

    def _try_open(self) -> None:
        if self.min_duration_elapsed and (self.bootstrap_complete or self.fallback_triggered):
            self._ready_event.set()
