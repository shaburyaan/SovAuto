from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from ui.i18n.strings import UiStrings


class AboutPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.title_label = QLabel(UiStrings.ABOUT_TITLE)
        self.title_label.setObjectName("sectionTitle")
        self.info_label = QTextEdit()
        self.info_label.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addWidget(self.info_label, 1)
