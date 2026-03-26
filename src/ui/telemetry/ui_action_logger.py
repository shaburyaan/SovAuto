from __future__ import annotations

import logging
from typing import Any

from core.contracts.event_bus import EventEnvelope, GlobalEventBus


class UiActionLogger:
    def __init__(self, event_bus: GlobalEventBus, logger: logging.Logger) -> None:
        self.event_bus = event_bus
        self.logger = logger

    def log_ui_action(self, action: str, payload: dict[str, Any] | None = None) -> None:
        data = payload or {}
        self.logger.info("UI action | %s | %s", action, data)
        self.event_bus.publish(
            EventEnvelope(
                event_type="UI_ACTION_RECORDED",
                source="ui",
                payload={"action": action, **data},
            )
        )

    def log_screen_transition(self, screen: str) -> None:
        self.logger.info("Screen transition | %s", screen)
        self.event_bus.publish(
            EventEnvelope(
                event_type="SCREEN_TRANSITION",
                source="ui",
                payload={"screen": screen},
            )
        )

    def log_onboarding(self, step: str, skipped: bool = False) -> None:
        self.logger.info("Onboarding | step=%s | skipped=%s", step, skipped)
        self.event_bus.publish(
            EventEnvelope(
                event_type="ONBOARDING_STEP",
                source="ui",
                payload={"step": step, "skipped": skipped},
            )
        )

    def log_onec_event(self, state: str, payload: dict[str, Any] | None = None) -> None:
        data = payload or {}
        self.logger.info("1C session | %s | %s", state, data)
        self.event_bus.publish(
            EventEnvelope(
                event_type="ONEC_SESSION_EVENT",
                source="onec",
                payload={"state": state, **data},
            )
        )
