from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Any


@dataclass(slots=True)
class RawInputEvent:
    event_type: str
    x: int
    y: int
    button: str | None = None
    key: str | None = None
    timestamp: float = field(default_factory=monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NormalizedDomainEvent:
    event_type: str
    x: int
    y: int
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


class DomainEventNormalizer:
    def normalize(self, event: RawInputEvent) -> NormalizedDomainEvent:
        return NormalizedDomainEvent(
            event_type=event.event_type,
            x=int(event.x),
            y=int(event.y),
            timestamp=event.timestamp,
            metadata=dict(event.metadata),
        )
