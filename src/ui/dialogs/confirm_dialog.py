from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget


class ConfirmDialog:
    @staticmethod
    def ask(parent: QWidget, title: str, text: str) -> bool:
        return (
            QMessageBox.question(parent, title, text)
            == QMessageBox.StandardButton.Yes
        )
