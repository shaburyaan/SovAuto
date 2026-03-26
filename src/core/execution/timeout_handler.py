from __future__ import annotations

from core.contracts.execution_clock import ExecutionClock


class TimeoutHandler:
    def __init__(self, clock: ExecutionClock) -> None:
        self.clock = clock

    def is_expired(self, started_at: float, timeout_ms: int) -> bool:
        return (self.clock.now_monotonic() - started_at) * 1000 >= timeout_ms
