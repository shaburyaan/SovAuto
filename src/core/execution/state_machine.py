from __future__ import annotations

from core.models.state import EngineState, EngineStatus


class ExecutionStateMachine:
    _transitions = {
        EngineStatus.IDLE: {EngineStatus.COUNTDOWN},
        EngineStatus.COUNTDOWN: {EngineStatus.RUNNING, EngineStatus.PAUSED, EngineStatus.STOPPED, EngineStatus.FAILED},
        EngineStatus.RUNNING: {EngineStatus.PAUSED, EngineStatus.STOPPED, EngineStatus.FAILED, EngineStatus.COMPLETED},
        EngineStatus.PAUSED: {EngineStatus.RUNNING, EngineStatus.STOPPED, EngineStatus.FAILED},
        EngineStatus.STOPPED: {EngineStatus.IDLE},
        EngineStatus.FAILED: {EngineStatus.IDLE},
        EngineStatus.COMPLETED: {EngineStatus.IDLE},
    }

    def __init__(self) -> None:
        self.state = EngineState()

    def transition(self, new_state: EngineStatus) -> EngineStatus:
        allowed = self._transitions.get(self.state.status, set())
        if new_state not in allowed:
            raise ValueError(f"Illegal transition: {self.state.status} -> {new_state}")
        old_state = self.state.status
        self.state.status = new_state
        return old_state
