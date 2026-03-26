from __future__ import annotations

from core.contracts.normalized_events import NormalizedDomainEvent


class ActionClassifier:
    def classify(self, event: NormalizedDomainEvent) -> str:
        return event.event_type
