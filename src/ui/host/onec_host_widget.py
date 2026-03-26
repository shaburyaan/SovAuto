from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ui.i18n.strings import UiStrings
from ui.splash.splash_screen import LoadingSpinner


class OneCHostWidget(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("onecHostWidget")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.mode = "waiting_for_1c"
        self.content_frame = QFrame()
        self.content_frame.setObjectName("onecHostFrame")
        self.content_frame.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_frame, 1)
        self.set_waiting()

    def clear_embedded(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def set_waiting(self) -> None:
        self.mode = "waiting_for_1c"
        self.clear_embedded()
        self._add_message(UiStrings.HOME_PLACEHOLDER)

    def set_loading(self, text: str) -> None:
        self.mode = "loading"
        self.clear_embedded()
        spinner = LoadingSpinner(self.content_frame)
        spinner.setFixedSize(48, 48)
        spinner.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        self.content_layout.addStretch(1)
        self.content_layout.addWidget(spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(label)
        self.content_layout.addStretch(1)

    def set_embedded(self, widget: QWidget, base_hint: str) -> None:
        self.mode = "embedded"
        self.clear_embedded()
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.content_layout.addWidget(widget)
        widget.setFocus()

    def set_external(self, base_hint: str) -> None:
        self.mode = "external_attached"
        self.clear_embedded()
        self._add_message(UiStrings.HOME_PLACEHOLDER)

    def set_failed(self, message: str) -> None:
        self.mode = "launch_failed"
        self.clear_embedded()
        self._add_message(message)

    def set_stopped(self) -> None:
        self.mode = "stopped"
        self.clear_embedded()
        self._add_message(UiStrings.HOME_PLACEHOLDER)

    def set_crashed(self) -> None:
        self.mode = "crashed"
        self.clear_embedded()
        self._add_message(UiStrings.ERROR_GENERIC)

    def _add_message(self, text: str) -> None:
        self.content_layout.addStretch(1)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setObjectName("hostInlineMessage")
        self.content_layout.addWidget(label)
        self.content_layout.addStretch(1)
