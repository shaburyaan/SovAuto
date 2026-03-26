from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionEvent:
    run_id: str


@dataclass(slots=True)
class StateChangedEvent(ExecutionEvent):
    old_state: str
    new_state: str


@dataclass(slots=True)
class StepStartedEvent(ExecutionEvent):
    step_id: str


@dataclass(slots=True)
class StepFinishedEvent(ExecutionEvent):
    step_id: str
    status: str
