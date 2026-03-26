from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget

from ui.i18n.strings import UiStrings


class ConfigsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.title_label = QLabel(UiStrings.CONFIGS_TITLE)
        self.title_label.setObjectName("sectionTitle")
        self.empty_label = QLabel(UiStrings.CONFIGS_EMPTY)
        self.empty_label.setObjectName("sectionSubtitle")
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.delete_button = QPushButton(UiStrings.ACTION_DELETE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.list_widget, 1)
        layout.addWidget(self.delete_button)
