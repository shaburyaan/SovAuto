from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from uuid import uuid4

from core.contracts.cancellation import CancellationReason, CancellationTokenSource


@dataclass(slots=True)
class RunController:
    run_id: str = field(default_factory=lambda: uuid4().hex)
    cancellation: CancellationTokenSource = field(default_factory=CancellationTokenSource)
    _pause_requested: bool = False
    _lock: Lock = field(default_factory=Lock)

    def request_pause(self) -> None:
        with self._lock:
            self._pause_requested = True

    def clear_pause(self) -> None:
        with self._lock:
            self._pause_requested = False

    def is_pause_requested(self) -> bool:
        with self._lock:
            return self._pause_requested

    def stop(self) -> None:
        self.cancellation.cancel(CancellationReason.USER_STOP)
