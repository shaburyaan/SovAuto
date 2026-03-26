from __future__ import annotations

from ui.overlay.cursor_tracker import CursorTracker
from ui.overlay.monitor_layout import MonitorLayoutService
from ui.overlay.overlay_state import OverlayViewState
from ui.overlay.overlay_window import OverlayWindow


class OverlayManager:
    def __init__(self) -> None:
        self.layout_service = MonitorLayoutService()
        self.windows: list[OverlayWindow] = []
        self.view_state = OverlayViewState()
        self.cursor_tracker: CursorTracker | None = None

    def create(self) -> None:
        self.windows = [OverlayWindow(geometry) for geometry in self.layout_service.geometries()]
        self.cursor_tracker = CursorTracker(self.update_cursor)

    def show(
        self,
        text: str,
        click_through: bool = True,
        presentation: str = "recording",
        secondary_text: str = "",
    ) -> None:
        self.view_state.status_text = text
        self.view_state.state = presentation
        for window in self.windows:
            window.set_presentation(presentation, text, secondary_text)
            window.set_click_through(click_through)
            window.showFullScreen()
            window.ensure_non_blocking()
            window.raise_()

    def hide(self) -> None:
        for window in self.windows:
            window.hide()

    def update_cursor(self, x: int, y: int) -> None:
        for window in self.windows:
            window.update_cursor(x, y)

    def trigger_ripple(self, x: int, y: int) -> None:
        for window in self.windows:
            window.trigger_ripple(x, y)

    def clear_ripple(self) -> None:
        for window in self.windows:
            window.clear_ripple()
