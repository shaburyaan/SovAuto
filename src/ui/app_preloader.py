from __future__ import annotations

from ui.app_window import AppWindow


class AppPreloader:
    def __init__(self, controller) -> None:
        self.window = AppWindow(controller)
        controller.app_window = self.window
        self.window.setWindowOpacity(0.0)

    def preload(self) -> AppWindow:
        return self.window
