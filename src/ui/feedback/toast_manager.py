from __future__ import annotations

from PyQt6.QtCore import QPropertyAnimation, QTimer, QEasingCurve
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class ToastManager(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("toastMessage")
        self.setProperty("kind", "default")
        self.icon_label = QLabel(self)
        self.icon_label.setObjectName("toastIcon")
        self.message_label = QLabel(self)
        self.message_label.setObjectName("toastText")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label)
        self.hide()
        self._animation = QPropertyAnimation(self, b"windowOpacity", self)
        self._animation.setDuration(220)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._animation.finished.connect(self._handle_animation_finished)
        self._fading_out = False

    def show_message(self, payload: object, timeout_ms: int = 2600) -> None:
        message, kind, resolved_timeout = self._resolve_payload(payload, timeout_ms)
        self.setProperty("kind", kind)
        self.icon_label.setText("✓" if kind == "success" else "✕" if kind == "error" else "i")
        self.message_label.setText(message)
        self.style().unpolish(self)
        self.style().polish(self)
        self.adjustSize()
        self.resize(self.sizeHint())
        parent = self.parentWidget()
        if parent is not None:
            self.move(max(24, parent.width() - self.width() - 28), 24)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()
        QTimer.singleShot(resolved_timeout, self._fade_out)

    def _fade_out(self) -> None:
        self._animation.stop()
        self._fading_out = True
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()

    def _handle_animation_finished(self) -> None:
        if self._fading_out:
            self.hide()
            self._fading_out = False

    def _resolve_payload(self, payload: object, timeout_ms: int) -> tuple[str, str, int]:
        if isinstance(payload, dict):
            return (
                str(payload.get("message", "")),
                str(payload.get("kind", "default")),
                int(payload.get("timeout_ms", timeout_ms)),
            )
        return str(payload), "default", timeout_ms
