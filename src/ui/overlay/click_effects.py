from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RippleEffectController:
    x: int = 0
    y: int = 0
    visible: bool = False

    def trigger(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.visible = True

    def clear(self) -> None:
        self.visible = False
