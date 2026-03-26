from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget

from ui.i18n.strings import UiStrings


class ConfirmClickDialog:
    @staticmethod
    def confirm(parent: QWidget) -> bool:
        result = QMessageBox.question(
            parent,
            "Подтверждение",
            UiStrings.RECORD_CONFIRM_ACTION,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return result == QMessageBox.StandardButton.Yes
