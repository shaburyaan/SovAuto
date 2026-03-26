from __future__ import annotations

from core.models.result import RunResult, StepResult


class ResultHandler:
    def __init__(self) -> None:
        self._results: list[StepResult] = []

    def add(self, result: StepResult) -> None:
        self._results.append(result)

    def finalize(self, status: str) -> RunResult:
        return RunResult(status=status, step_results=list(self._results))
