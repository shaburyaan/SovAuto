from __future__ import annotations

from PyQt6.QtWidgets import QInputDialog, QWidget


class ScenarioNameDialog:
    @staticmethod
    def get_name(parent: QWidget) -> tuple[str, bool]:
        value, accepted = QInputDialog.getText(parent, "Сохранение сценария", "Введите имя сценария")
        return value.strip(), accepted and bool(value.strip())
