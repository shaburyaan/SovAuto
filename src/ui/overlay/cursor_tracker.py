from __future__ import annotations

from PyQt6.QtCore import QPoint, QTimer
from PyQt6.QtGui import QCursor


class CursorTracker:
    def __init__(self, callback) -> None:
        self._callback = callback
        self._timer = QTimer()
        self._timer.timeout.connect(self._emit)
        self._timer.start(16)

    def _emit(self) -> None:
        point: QPoint = QCursor.pos()
        self._callback(point.x(), point.y())
