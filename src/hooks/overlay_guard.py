from __future__ import annotations


class OverlayGuard:
    def is_overlay_event(self, metadata: dict) -> bool:
        return metadata.get("overlay", False)
