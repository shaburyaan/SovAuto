from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EngineStatus(StrEnum):
    IDLE = "idle"
    COUNTDOWN = "countdown"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"
    COMPLETED = "completed"


@dataclass(slots=True)
class EngineState:
    status: EngineStatus = EngineStatus.IDLE


@dataclass(slots=True)
class RecorderState:
    status: str = "idle"


@dataclass(slots=True)
class OverlayState:
    status: str = "hidden"
