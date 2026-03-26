from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget
import win32con
import win32gui

from ui.brand.design_tokens import DesignTokens
from ui.overlay.click_effects import RippleEffectController


class OverlayWindow(QWidget):
    def __init__(self, geometry) -> None:
        super().__init__()
        self.setGeometry(geometry)
        self._transparent_input_flag = getattr(Qt.WindowType, "WindowTransparentForInput", None)
        base_flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setWindowFlags(base_flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._click_through = True
        self.presentation = "recording"
        self.status_text = ""
        self.secondary_text = ""
        self.cursor_pos = (0, 0)
        self.dim_alpha = 72
        self.show_cursor_indicator = True
        self.ripple = RippleEffectController()

    def set_click_through(self, enabled: bool) -> None:
        self._click_through = enabled
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, enabled)
        if self._transparent_input_flag is not None:
            self.setWindowFlag(self._transparent_input_flag, enabled)

    def ensure_non_blocking(self) -> None:
        hwnd = int(self.winId())
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        desired = ex_style | win32con.WS_EX_NOACTIVATE
        if self._click_through:
            desired |= win32con.WS_EX_TRANSPARENT
        else:
            desired &= ~win32con.WS_EX_TRANSPARENT
        if desired != ex_style:
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, desired)
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                0,
                0,
                0,
                0,
                win32con.SWP_NOMOVE
                | win32con.SWP_NOSIZE
                | win32con.SWP_NOACTIVATE
                | win32con.SWP_NOOWNERZORDER
                | win32con.SWP_FRAMECHANGED,
            )

    def set_presentation(self, presentation: str, text: str, secondary_text: str = "") -> None:
        self.presentation = presentation
        self.status_text = text
        self.secondary_text = secondary_text
        if presentation == "recording":
            self.dim_alpha = 72
            self.show_cursor_indicator = True
        else:
            self.dim_alpha = 164
            self.show_cursor_indicator = False
        self.update()

    def update_cursor(self, x: int, y: int) -> None:
        self.cursor_pos = (x, y)
        self.update()

    def trigger_ripple(self, x: int, y: int) -> None:
        self.ripple.trigger(x, y)
        self.update()

    def clear_ripple(self) -> None:
        self.ripple.clear()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self.dim_alpha))
        painter.setPen(QColor(255, 255, 255))
        if self.presentation == "recording":
            self._draw_recording_text(painter)
        elif self.presentation == "playback":
            self._draw_playback_banner(painter)
        else:
            self._draw_centered_text(painter)
        if self.show_cursor_indicator:
            painter.setPen(QPen(QColor(255, 214, 10), 3))
            x, y = self.cursor_pos
            painter.drawEllipse(x - 16, y - 16, 32, 32)
        if self.ripple.visible:
            painter.setPen(QPen(QColor(255, 214, 10), 3))
            painter.drawEllipse(self.ripple.x - 20, self.ripple.y - 20, 40, 40)

    def _draw_recording_text(self, painter: QPainter) -> None:
        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        rect = self.rect().adjusted(24, 24, -24, -24)
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
            self.status_text,
        )

    def _draw_playback_banner(self, painter: QPainter) -> None:
        font = QFont("Segoe UI", 13, QFont.Weight.DemiBold)
        painter.setFont(font)
        rect = self.rect().adjusted(24, 24, -24, -24)
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
            self.status_text,
        )

    def _draw_centered_text(self, painter: QPainter) -> None:
        if self.presentation == "countdown":
            title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
            value_font = QFont("Segoe UI", 68, QFont.Weight.Bold)
            title_rect = self.rect().adjusted(120, 180, -120, -40)
            value_rect = self.rect().adjusted(120, 280, -120, -180)
            painter.setFont(title_font)
            painter.drawText(
                title_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap,
                self.status_text,
            )
            painter.setFont(value_font)
            painter.drawText(
                value_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                self.secondary_text,
            )
            return

        if self.presentation == "completion":
            icon_font = QFont("Segoe UI", 60, QFont.Weight.Bold)
            text_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
            icon_rect = self.rect().adjusted(120, 180, -120, -120)
            text_rect = self.rect().adjusted(120, 320, -120, -120)
            painter.setFont(icon_font)
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, self.secondary_text or "✓")
            painter.setFont(text_font)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                self.status_text,
            )
            return

        text_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        painter.setFont(text_font)
        painter.drawText(
            self.rect().adjusted(120, 120, -120, -120),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self.status_text,
        )
