from __future__ import annotations

from core.contracts.normalized_events import NormalizedDomainEvent
from hooks.undo_stack import RecordingUndoStack


class RecordingSession:
    def __init__(self) -> None:
        self.undo_stack = RecordingUndoStack()

    def append_step(self, step: dict) -> None:
        self.undo_stack.push(step)

    def undo_last(self) -> dict | None:
        return self.undo_stack.undo()

    def steps(self) -> list[dict]:
        return self.undo_stack.items()

    def reset(self) -> None:
        self.undo_stack.clear()

    def from_event(self, event: NormalizedDomainEvent, input_mode: bool = False) -> dict:
        step_type = "input" if input_mode else "click"
        return {
            "id": f"rec-{len(self.undo_stack.items()) + 1}",
            "type": step_type,
            "target": {"x": event.x, "y": event.y},
            "raw_timestamp": event.timestamp,
        }
