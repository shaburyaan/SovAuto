from __future__ import annotations

from core.automation.window_guard import OneCWindowGuard


class UiReadinessProbe:
    def __init__(self) -> None:
        self.guard = OneCWindowGuard()

    def check(self, process_name: str, title_pattern: str) -> bool:
        return self.guard.ensure_window_ready(process_name, title_pattern).ok
