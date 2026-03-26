from __future__ import annotations

from pynput.mouse import Button, Controller

from core.automation.target_resolver import TargetResolver
from core.models.targets import AnchorOffset, AnchorTarget, RelativePoint, WindowTarget


class ClickExecutor:
    def __init__(self) -> None:
        self.mouse = Controller()
        self.resolver = TargetResolver()

    def execute(self, step: dict) -> None:
        resolved = self.resolver.resolve(
            WindowTarget(**step["window"]),
            RelativePoint(**step["target"]),
            AnchorTarget(**step.get("anchor", {})),
            AnchorOffset(**step.get("offset", {})),
        )
        self.mouse.position = (resolved.x, resolved.y)
        button = Button.left if step.get("button", "left") == "left" else Button.right
        self.mouse.click(button)
