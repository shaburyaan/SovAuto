from __future__ import annotations

from core.contracts.normalized_events import RawInputEvent


class InputEventFilter:
    def __init__(self, debounce_ms: float = 250.0, move_threshold: int = 3) -> None:
        self.debounce_ms = debounce_ms
        self.move_threshold = move_threshold
        self._last_click: RawInputEvent | None = None

    def allow(self, event: RawInputEvent) -> bool:
        if self._last_click is None or event.event_type != "click":
            if event.event_type == "click":
                self._last_click = event
            return True
        delta_ms = (event.timestamp - self._last_click.timestamp) * 1000
        if delta_ms <= self.debounce_ms and abs(event.x - self._last_click.x) <= self.move_threshold and abs(event.y - self._last_click.y) <= self.move_threshold:
            return False
        self._last_click = event
        return True
