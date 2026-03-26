from __future__ import annotations

from core.contracts.execution_clock import ExecutionClock


class ExecutionClockBridge:
    def __init__(self, clock: ExecutionClock) -> None:
        self.clock = clock

    def now(self) -> float:
        return self.clock.now_monotonic()
