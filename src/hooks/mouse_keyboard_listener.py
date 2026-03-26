from __future__ import annotations

from typing import Callable

from pynput import mouse

from core.contracts.normalized_events import RawInputEvent


class GlobalInputListener:
    def __init__(self, on_event: Callable[[RawInputEvent], None]) -> None:
        self._on_event = on_event
        self._listener = mouse.Listener(on_click=self._on_click)

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        if not pressed:
            self._on_event(
                RawInputEvent(
                    event_type="click",
                    x=x,
                    y=y,
                    button=str(button),
                )
            )

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()
