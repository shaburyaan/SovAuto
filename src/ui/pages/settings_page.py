from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.i18n.strings import UiStrings


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.title_label = QLabel(UiStrings.SETTINGS_TITLE)
        self.title_label.setObjectName("sectionTitle")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(r"C:\Program Files\1cv8\common\...\1cv8.exe")
        self.lock_mode = QComboBox()
        self.lock_mode.addItems([UiStrings.LOCK_MODE_SOFT, UiStrings.LOCK_MODE_HARD])
        self.delay_box = QSpinBox()
        self.delay_box.setRange(1, 30)
        self.delay_box.setValue(4)
        self.retry_box = QSpinBox()
        self.retry_box.setRange(0, 10)
        self.retry_box.setValue(3)
        self.embed_checkbox = QCheckBox(UiStrings.SETTINGS_EMBED)
        self.embed_checkbox.setChecked(True)
        self.embed_hint = QLabel(UiStrings.SETTINGS_EMBED_HINT)
        self.embed_hint.setObjectName("sectionSubtitle")
        self.embed_hint.setWordWrap(True)
        self.save_button = QPushButton(UiStrings.ACTION_SAVE)
        self.onboarding_button = QPushButton(UiStrings.SETTINGS_ONBOARDING)

        form = QFormLayout()
        form.addRow(UiStrings.SETTINGS_ONEC_PATH, self.path_edit)
        form.addRow(UiStrings.SETTINGS_LOCK_MODE, self.lock_mode)
        form.addRow(UiStrings.SETTINGS_DELAY, self.delay_box)
        form.addRow(UiStrings.SETTINGS_RETRY, self.retry_box)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addLayout(form)
        layout.addWidget(self.embed_checkbox)
        layout.addWidget(self.embed_hint)
        layout.addWidget(self.save_button)
        layout.addWidget(self.onboarding_button)
        layout.addStretch(1)
