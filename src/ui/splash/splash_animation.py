from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QRect
from PyQt6.QtWidgets import QLabel, QWidget, QGraphicsOpacityEffect


class SplashAnimationTimeline:
    def __init__(self, screen: QWidget, logo: QLabel) -> None:
        self.screen = screen
        self.logo = logo
        self.opacity = QGraphicsOpacityEffect(logo)
        self.logo.setGraphicsEffect(self.opacity)

    def build(self) -> QParallelAnimationGroup:
        group = QParallelAnimationGroup(self.screen)
        fade = QPropertyAnimation(self.opacity, b"opacity")
        fade.setDuration(2400)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.InOutCubic)
        start_rect = self.logo.geometry()
        zoom_rect = QRect(
            start_rect.x() + 12,
            start_rect.y() + 12,
            max(1, start_rect.width() - 24),
            max(1, start_rect.height() - 24),
        )
        scale = QPropertyAnimation(self.logo, b"geometry")
        scale.setDuration(10000)
        scale.setStartValue(zoom_rect)
        scale.setEndValue(start_rect)
        scale.setEasingCurve(QEasingCurve.Type.InOutCubic)
        group.addAnimation(fade)
        group.addAnimation(scale)
        return group
