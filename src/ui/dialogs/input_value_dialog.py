from __future__ import annotations

from PyQt6.QtWidgets import QInputDialog, QWidget


class InputValueDialog:
    @staticmethod
    def get_text(parent: QWidget) -> tuple[str, bool]:
        value, accepted = QInputDialog.getText(parent, "Заполнение", "Введите текст")
        return value, accepted and bool(value.strip())
