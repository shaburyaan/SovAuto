from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from core.models.policy import ExecutionPolicy
from core.models.targets import AnchorOffset, AnchorTarget, RelativePoint, WindowTarget


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class BaseStep:
    type: str
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    enabled: bool = True
    createdAt: str = field(default_factory=_now)
    updatedAt: str = field(default_factory=_now)
    policy: ExecutionPolicy = field(default_factory=ExecutionPolicy)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ClickStep(BaseStep):
    type: str = "click"
    window: WindowTarget = field(default_factory=WindowTarget)
    target: RelativePoint = field(default_factory=lambda: RelativePoint(0.5, 0.5))
    anchor: AnchorTarget = field(default_factory=AnchorTarget)
    offset: AnchorOffset = field(default_factory=AnchorOffset)
    button: str = "left"


@dataclass(slots=True)
class InputStep(BaseStep):
    type: str = "input"
    window: WindowTarget = field(default_factory=WindowTarget)
    target: RelativePoint = field(default_factory=lambda: RelativePoint(0.5, 0.5))
    value: str = ""


@dataclass(slots=True)
class DragStep(BaseStep):
    type: str = "drag"
    window: WindowTarget = field(default_factory=WindowTarget)
    start: RelativePoint = field(default_factory=lambda: RelativePoint(0.4, 0.4))
    end: RelativePoint = field(default_factory=lambda: RelativePoint(0.6, 0.6))


@dataclass(slots=True)
class WaitForWindowStep(BaseStep):
    type: str = "wait_for_window"
    window: WindowTarget = field(default_factory=WindowTarget)
    timeoutMs: int = 5000


@dataclass(slots=True)
class WaitForPixelStep(BaseStep):
    type: str = "wait_for_pixel"
    x: int = 0
    y: int = 0
    color: str = "#FFFFFF"
    timeoutMs: int = 5000


@dataclass(slots=True)
class WaitForColorStep(BaseStep):
    type: str = "wait_for_color"
    x: int = 0
    y: int = 0
    color: str = "#FFFFFF"
    timeoutMs: int = 5000


@dataclass(slots=True)
class WaitForTextStep(BaseStep):
    type: str = "wait_for_text"
    region: dict[str, int] = field(default_factory=dict)
    expected: str = ""
    timeoutMs: int = 5000


@dataclass(slots=True)
class CompareStep(BaseStep):
    type: str = "compare"
    regionA: dict[str, int] = field(default_factory=dict)
    regionB: dict[str, int] = field(default_factory=dict)
    ifGreater: list[dict[str, Any]] = field(default_factory=list)
    ifLess: list[dict[str, Any]] = field(default_factory=list)
