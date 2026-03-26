from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OverlayMode:
    mode: str = "click-through"


@dataclass(slots=True)
class OverlayViewState:
    state: str = "hidden"
    status_text: str = ""
    step_count: int = 0
