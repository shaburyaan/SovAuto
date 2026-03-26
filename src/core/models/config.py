from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from core.models.config_metadata import ConfigReliabilityMetadata


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class ConfigSettings:
    delayBetweenSteps: int = 300
    retryCount: int = 3
    countdownSeconds: int = 5
    lockMode: str = "soft"
    requireActiveOneCWindow: bool = True


@dataclass(slots=True)
class ConfigMetadata:
    version: str = "1.0"
    createdAt: str = field(default_factory=_now)
    updatedAt: str = field(default_factory=_now)


@dataclass(slots=True)
class Config:
    name: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    settings: ConfigSettings = field(default_factory=ConfigSettings)
    metadata: ConfigMetadata = field(default_factory=ConfigMetadata)
    reliability: ConfigReliabilityMetadata = field(default_factory=ConfigReliabilityMetadata)
    id: str = field(default_factory=lambda: uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
