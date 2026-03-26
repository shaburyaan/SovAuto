from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class OverlayInputShield:
    visual_only: bool = True
    blocks_engine_timing: bool = False
    participates_in_dispatch: bool = False
