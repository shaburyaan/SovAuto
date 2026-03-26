from __future__ import annotations

from pynput.keyboard import Controller as KeyboardController

from core.automation.actions.click_executor import ClickExecutor


class InputExecutor:
    def __init__(self) -> None:
        self.click_executor = ClickExecutor()
        self.keyboard = KeyboardController()

    def execute(self, step: dict) -> None:
        click_step = {
            "window": step["window"],
            "target": step["target"],
            "anchor": step.get("anchor", {}),
            "offset": step.get("offset", {}),
            "button": "left",
        }
        self.click_executor.execute(click_step)
        self.keyboard.type(step["value"])
