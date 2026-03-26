from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget


class ErrorDialog:
    @staticmethod
    def show(parent: QWidget, title: str, text: str) -> None:
        QMessageBox.critical(parent, title, text)
