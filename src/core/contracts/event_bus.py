from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from threading import RLock
from time import monotonic
from typing import Any, Callable
from uuid import uuid4


EventHandler = Callable[["EventEnvelope"], None]


@dataclass(slots=True)
class EventEnvelope:
    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    app_state: str | None = None
    event_id: str = field(default_factory=lambda: uuid4().hex)
    timestamp_monotonic: float = field(default_factory=monotonic)
    priority: int = 0


@dataclass(slots=True)
class EventSubscription:
    event_type: str
    handler: EventHandler


class GlobalEventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event_type: str, handler: EventHandler) -> EventSubscription:
        with self._lock:
            self._handlers[event_type].append(handler)
        return EventSubscription(event_type=event_type, handler=handler)

    def unsubscribe(self, subscription: EventSubscription) -> None:
        with self._lock:
            handlers = self._handlers.get(subscription.event_type, [])
            if subscription.handler in handlers:
                handlers.remove(subscription.handler)

    def publish(self, envelope: EventEnvelope) -> None:
        with self._lock:
            handlers = list(self._handlers.get(envelope.event_type, []))
            wildcard = list(self._handlers.get("*", []))
        for handler in handlers + wildcard:
            handler(envelope)
