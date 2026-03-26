from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ui.i18n.strings import UiStrings


@dataclass(slots=True)
class OnboardingStep:
    title: str
    text: str
    target: QWidget


class OnboardingOverlay(QWidget):
    next_requested = pyqtSignal()
    skip_requested = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("onboardingOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.current_step: OnboardingStep | None = None

        self.bubble = QWidget(self)
        self.bubble.setObjectName("onboardingBubble")
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(20, 20, 20, 20)
        self.title_label = QLabel()
        self.title_label.setObjectName("onboardingTitle")
        self.text_label = QLabel()
        self.text_label.setObjectName("onboardingText")
        self.text_label.setWordWrap(True)
        self.next_button = QPushButton(UiStrings.ACTION_NEXT)
        self.skip_button = QPushButton(UiStrings.ACTION_SKIP)
        self.next_button.clicked.connect(self.next_requested.emit)
        self.skip_button.clicked.connect(self.skip_requested.emit)
        bubble_layout.addWidget(self.title_label)
        bubble_layout.addWidget(self.text_label)
        bubble_layout.addWidget(self.next_button)
        bubble_layout.addWidget(self.skip_button)
        self.hide()

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._position_bubble()
        super().resizeEvent(event)

    def show_step(self, step: OnboardingStep, is_last: bool = False) -> None:
        self.current_step = step
        self.title_label.setText(step.title)
        self.text_label.setText(step.text)
        self.next_button.setText(UiStrings.ACTION_FINISH if is_last else UiStrings.ACTION_NEXT)
        self.setGeometry(self.parentWidget().rect())
        self._position_bubble()
        self.show()
        self.raise_()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(6, 10, 18, 180))
        if self.current_step is not None:
            target_rect = self._target_rect()
            painter.setPen(QPen(QColor("#dec28f"), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(target_rect.adjusted(-8, -8, 8, 8), 12, 12)

    def _target_rect(self) -> QRect:
        assert self.current_step is not None
        target = self.current_step.target
        top_left = target.mapTo(self, target.rect().topLeft())
        return QRect(top_left, target.rect().size())

    def _position_bubble(self) -> None:
        if self.current_step is None:
            self.bubble.move(40, 40)
            return
        rect = self._target_rect()
        self.bubble.adjustSize()
        bubble_x = min(max(24, rect.right() + 24), max(24, self.width() - self.bubble.width() - 24))
        bubble_y = min(max(24, rect.top()), max(24, self.height() - self.bubble.height() - 24))
        self.bubble.move(bubble_x, bubble_y)
