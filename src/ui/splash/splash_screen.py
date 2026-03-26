from __future__ import annotations

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QLinearGradient, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QLabel, QWidget

from ui.i18n.strings import UiStrings
from ui.splash.assets import SplashAssetProvider


class LoadingSpinner(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(16)
        self.setFixedSize(36, 36)

    def _advance(self) -> None:
        self._angle = (self._angle + 8) % 360
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        pen = QPen(QColor("#8d8169"), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(-12, -12, 24, 24, 0, 250 * 16)


class SplashScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())
        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner = LoadingSpinner(self)
        self.loading_label = QLabel(UiStrings.SPLASH_LOADING, self)
        self.loading_label.setStyleSheet("color: #625646; font-size: 16px; font-weight: 600;")
        self.subtitle_label = QLabel(UiStrings.SPLASH_SUBTITLE, self)
        self.subtitle_label.setStyleSheet("color: #8d8169; font-size: 13px;")
        self.asset_provider = SplashAssetProvider()
        self._set_logo()
        self._position_loading()

    def _set_logo(self) -> None:
        pixmap: QPixmap = self.asset_provider.load_logo()
        self.logo_label.setPixmap(pixmap.scaledToWidth(480, Qt.TransformationMode.SmoothTransformation))
        self.logo_label.adjustSize()
        self.logo_label.move(
            max(0, (self.width() - self.logo_label.width()) // 2),
            max(0, (self.height() - self.logo_label.height()) // 2),
        )

    def _position_loading(self) -> None:
        center_x = self.width() // 2
        base_y = max(40, self.height() - 180)
        self.spinner.move(center_x - (self.spinner.width() // 2), base_y)
        self.loading_label.adjustSize()
        self.loading_label.move(center_x - (self.loading_label.width() // 2), base_y + 52)
        self.subtitle_label.adjustSize()
        self.subtitle_label.move(center_x - (self.subtitle_label.width() // 2), base_y + 82)

    def resizeEvent(self, _event) -> None:  # noqa: N802
        self._set_logo()
        self._position_loading()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#f2eadc"))
        gradient.setColorAt(1.0, QColor("#e4d8c0"))
        painter.fillRect(self.rect(), gradient)
