from __future__ import annotations

from typing import Callable

from pynput import keyboard


class HotkeyManager:
    def __init__(self, on_stop: Callable[[], None], on_pause: Callable[[], None], on_undo: Callable[[], None]) -> None:
        self._listener = keyboard.GlobalHotKeys(
            {
                "<esc>": on_stop,
                "<ctrl>+p": on_pause,
                "<ctrl>+z": on_undo,
            }
        )

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()
