from __future__ import annotations

from typing import Protocol


class PreStepGuard(Protocol):
    def check(self, step: dict) -> None:
        ...


class PreStepGuardPipeline:
    def __init__(self, guards: list[PreStepGuard] | None = None) -> None:
        self.guards = guards or []

    def check(self, step: dict) -> None:
        for guard in self.guards:
            guard.check(step)
