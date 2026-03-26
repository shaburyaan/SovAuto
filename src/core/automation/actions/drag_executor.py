from __future__ import annotations

from pynput.mouse import Button, Controller

from core.automation.target_resolver import TargetResolver
from core.models.targets import RelativePoint, WindowTarget


class DragExecutor:
    def __init__(self) -> None:
        self.mouse = Controller()
        self.resolver = TargetResolver()

    def execute(self, step: dict) -> None:
        window = WindowTarget(**step["window"])
        start = self.resolver.resolve(window, RelativePoint(**step["start"]))
        end = self.resolver.resolve(window, RelativePoint(**step["end"]))
        self.mouse.position = (start.x, start.y)
        self.mouse.press(Button.left)
        self.mouse.position = (end.x, end.y)
        self.mouse.release(Button.left)
