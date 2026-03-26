from __future__ import annotations

from dataclasses import dataclass

from core.contracts.app_lifecycle import AppLifecycleState
from core.contracts.event_bus import EventEnvelope, GlobalEventBus


@dataclass(slots=True)
class SystemController:
    event_bus: GlobalEventBus
    state: AppLifecycleState = AppLifecycleState.BOOTSTRAP

    def transition_to(self, state: AppLifecycleState) -> None:
        self.state = state
        self.event_bus.publish(
            EventEnvelope(
                event_type="APP_STATE_CHANGED",
                source="system_controller",
                app_state=state,
                payload={"state": state},
            )
        )
