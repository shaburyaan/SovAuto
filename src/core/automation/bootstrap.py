from __future__ import annotations

from core.automation.actions.click_executor import ClickExecutor
from core.automation.actions.compare_executor import CompareExecutor
from core.automation.actions.drag_executor import DragExecutor
from core.automation.actions.input_executor import InputExecutor
from core.automation.waits import (
    WaitForColorExecutor,
    WaitForPixelExecutor,
    WaitForTextExecutor,
    WaitForWindowExecutor,
)
from core.execution.executor_registry import ExecutorRegistry


def register_default_executors(registry: ExecutorRegistry) -> None:
    registry.register("click", ClickExecutor())
    registry.register("input", InputExecutor())
    registry.register("drag", DragExecutor())
    registry.register("compare", CompareExecutor())
    registry.register("wait_for_window", WaitForWindowExecutor())
    registry.register("wait_for_pixel", WaitForPixelExecutor())
    registry.register("wait_for_color", WaitForColorExecutor())
    registry.register("wait_for_text", WaitForTextExecutor())
