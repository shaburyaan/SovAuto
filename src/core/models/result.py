from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FailureInfo:
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WarningInfo:
    code: str
    message: str


@dataclass(slots=True)
class StepResult:
    step_id: str
    status: str
    message: str = ""
    failure: FailureInfo | None = None
    warning: WarningInfo | None = None


@dataclass(slots=True)
class RunResult:
    status: str
    step_results: list[StepResult] = field(default_factory=list)
