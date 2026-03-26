from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QWidget

from ui.host.onec_host_widget import OneCHostWidget


class HomePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.host_widget = OneCHostWidget()
        self._engine_state = "idle"
        self._session_status = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.host_widget, 1)

    def set_engine_state(self, state: str) -> None:
        self._engine_state = state

    def set_session_status(self, text: str) -> None:
        self._session_status = text
