from __future__ import annotations

from PyQt6.QtCore import QTimer

from ui.overlay.overlay_manager import OverlayManager


class RecordOverlay:
    RECORD_HINT = "Наведи курсор и нажми ALT для записи шага"
    STOP_HINT = "F8 или ESC — остановить запись"

    def __init__(self, overlay_manager: OverlayManager) -> None:
        self.overlay_manager = overlay_manager

    def show(self, mode_label: str) -> None:
        self.overlay_manager.show(self._compose_text(mode_label), click_through=True, presentation="recording")

    def update_status(self, text: str) -> None:
        self.overlay_manager.show(self._compose_text(text), click_through=True, presentation="recording")

    def hide(self) -> None:
        self.overlay_manager.hide()

    def trigger_marker(self, x: int, y: int) -> None:
        self.overlay_manager.trigger_ripple(x, y)

    def show_click_indicator(self, x: int, y: int, duration_ms: int = 260) -> None:
        self.overlay_manager.trigger_ripple(x, y)
        QTimer.singleShot(duration_ms, self.overlay_manager.clear_ripple)

    def _compose_text(self, text: str) -> str:
        return f"{text}\n{self.RECORD_HINT}\n{self.STOP_HINT}"
