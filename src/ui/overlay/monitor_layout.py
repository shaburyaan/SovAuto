from __future__ import annotations

from PyQt6.QtGui import QGuiApplication


class MonitorLayoutService:
    def geometries(self) -> list:
        return [screen.geometry() for screen in QGuiApplication.screens()]
