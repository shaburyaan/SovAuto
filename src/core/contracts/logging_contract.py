from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LogEnvelope:
    message: str
    module_source: str
    severity: str
    event_type: str | None = None
    state_type: str | None = None
    timestamp_execution_clock: float = 0.0
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class LoggingContract:
    requires_execution_timestamp: bool = True
    requires_module_source: bool = True
