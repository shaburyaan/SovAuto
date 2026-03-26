from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MainViewModel:
    engine_state: str = "idle"
