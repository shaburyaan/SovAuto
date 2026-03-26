from __future__ import annotations

from core.contracts.overlay_shield import OverlayInputShield


class OverlayInputShieldBridge:
    def __init__(self) -> None:
        self.contract = OverlayInputShield()
