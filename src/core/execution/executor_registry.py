from __future__ import annotations

from typing import Any, Protocol


class StepExecutor(Protocol):
    def execute(self, step: dict[str, Any]) -> Any:
        ...


class ExecutorRegistry:
    def __init__(self) -> None:
        self._executors: dict[str, StepExecutor] = {}

    def register(self, step_type: str, executor: StepExecutor) -> None:
        self._executors[step_type] = executor

    def resolve(self, step_type: str) -> StepExecutor:
        if step_type not in self._executors:
            raise KeyError(f"Executor not registered for {step_type}")
        return self._executors[step_type]
