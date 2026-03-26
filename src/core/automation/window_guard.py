from __future__ import annotations

from dataclasses import dataclass

from core.automation.window_service import WindowInfo, WindowService


@dataclass(slots=True)
class WindowProbeResult:
    ok: bool
    window: WindowInfo | None = None
    reason: str = ""


class OneCWindowGuard:
    def __init__(self, service: WindowService | None = None) -> None:
        self.service = service or WindowService()

    def ensure_window_ready(self, process_name: str, title_pattern: str) -> WindowProbeResult:
        window = self.service.find_window(process_name, title_pattern)
        if window is None:
            return WindowProbeResult(ok=False, reason="1C window not found")
        if not self.service.is_foreground(window.hwnd):
            try:
                self.service.restore_and_focus(window.hwnd)
            except Exception as exc:  # noqa: BLE001
                return WindowProbeResult(ok=False, reason=str(exc))
        return WindowProbeResult(ok=True, window=window)
