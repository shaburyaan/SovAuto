from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True, frozen=True)
class ExecutionClock:
    def now_monotonic(self) -> float:
        return monotonic()
