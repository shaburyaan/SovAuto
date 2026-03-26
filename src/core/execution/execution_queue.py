from __future__ import annotations

from collections import deque
from typing import Any


class ExecutionQueue:
    def __init__(self) -> None:
        self._steps: deque[dict[str, Any]] = deque()

    def load(self, steps: list[dict[str, Any]]) -> None:
        self._steps = deque(steps)

    def next(self) -> dict[str, Any] | None:
        if not self._steps:
            return None
        return self._steps.popleft()

    def __len__(self) -> int:
        return len(self._steps)
