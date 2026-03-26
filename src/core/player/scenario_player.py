from __future__ import annotations

from collections.abc import Sequence
import time

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import win32api
import win32con
import win32gui
from pynput.keyboard import Controller as KeyboardController

from core.automation.window_service import WindowService


class ScenarioPlayer(QObject):
    state_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    countdown_changed = pyqtSignal(int)
    step_started = pyqtSignal(int, object)
    finished = pyqtSignal()

    def __init__(self, window_service: WindowService | None = None) -> None:
        super().__init__()
        self.window_service = window_service or WindowService()
        self.keyboard = KeyboardController()
        self.step_delay_seconds = 4.0
        self.step_preview_ms = 300
        self._hwnd: int | None = None
        self._steps: list[dict] = []
        self._pending_step: dict | None = None
        self._index = 0
        self._countdown_remaining = 0
        self._is_playing = False
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick_countdown)
        self._step_timer = QTimer(self)
        self._step_timer.setSingleShot(True)
        self._step_timer.timeout.connect(self._execute_pending_step)
        self._completion_timer = QTimer(self)
        self._completion_timer.setSingleShot(True)
        self._completion_timer.timeout.connect(self._finish_completed_playback)

    def set_delay(self, seconds: float) -> None:
        self.step_delay_seconds = max(0.5, float(seconds))

    def play(self, hwnd: int, scenario: Sequence[dict], countdown_seconds: int = 5) -> bool:
        if not self.window_service.is_window(hwnd):
            self.error_occurred.emit("Окно 1С недоступно для воспроизведения.")
            return False
        if self._is_playing:
            self.error_occurred.emit("Воспроизведение уже запущено.")
            return False
        self.window_service.activate_window(hwnd)
        time.sleep(0.5)
        self._hwnd = hwnd
        self._steps = list(scenario)
        self._pending_step = None
        self._index = 0
        self._countdown_remaining = max(countdown_seconds, 0)
        self._is_playing = True
        self.state_changed.emit("countdown")
        self.countdown_changed.emit(self._countdown_remaining)
        if self._countdown_remaining == 0:
            QTimer.singleShot(1, self._play_next_step)
        else:
            self._countdown_timer.start()
        return True

    def stop(self) -> None:
        self._countdown_timer.stop()
        self._step_timer.stop()
        self._completion_timer.stop()
        was_playing = self._is_playing
        self._is_playing = False
        self._hwnd = None
        self._steps = []
        self._pending_step = None
        self._index = 0
        if was_playing:
            self.state_changed.emit("stopped")
            self.finished.emit()

    def is_playing(self) -> bool:
        return self._is_playing

    def _tick_countdown(self) -> None:
        self._countdown_remaining -= 1
        self.countdown_changed.emit(max(self._countdown_remaining, 0))
        if self._countdown_remaining > 0:
            return
        self._countdown_timer.stop()
        QTimer.singleShot(1, self._play_next_step)

    def _play_next_step(self) -> None:
        if not self._is_playing or self._hwnd is None:
            return
        if not self.window_service.is_window(self._hwnd):
            self.error_occurred.emit("Окно 1С было закрыто во время воспроизведения.")
            self.stop()
            return
        if self._index >= len(self._steps):
            self.state_changed.emit("completed")
            self._completion_timer.start(1500)
            return
        step = self._steps[self._index]
        self.state_changed.emit("running")
        self.step_started.emit(self._index, step)
        self._pending_step = step
        self._step_timer.start(self.step_preview_ms)

    def _execute_pending_step(self) -> None:
        if self._pending_step is None:
            return
        step = self._pending_step
        self._pending_step = None
        try:
            self._execute_step(step)
        except Exception as exc:  # noqa: BLE001
            self.error_occurred.emit(str(exc))
            self.stop()
            return
        self._index += 1
        QTimer.singleShot(int(self.step_delay_seconds * 1000), self._play_next_step)

    def _execute_step(self, step: dict) -> None:
        if self._hwnd is None:
            raise RuntimeError("Playback window is not set.")
        if not self.window_service.is_window(self._hwnd):
            raise RuntimeError("Target window lost")
        self.window_service.activate_window(self._hwnd)
        time.sleep(0.05)
        x, y = self._resolve_screen_coordinates(self._hwnd, int(step["x"]), int(step["y"]))
        win32api.SetCursorPos((x, y))
        time.sleep(0.03)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        if step["type"] == "input":
            QTimer.singleShot(120, lambda value=str(step.get("text", "")): self.keyboard.type(value))

    def _finish_completed_playback(self) -> None:
        was_playing = self._is_playing
        self._is_playing = False
        self._hwnd = None
        self._steps = []
        self._pending_step = None
        self._index = 0
        if was_playing:
            self.finished.emit()

    def _to_screen_coordinates(self, hwnd: int, rel_x: int, rel_y: int) -> tuple[int, int]:
        left, top, right, bottom = self.window_service.get_window_info(hwnd).bounds
        width = max(1, right - left)
        height = max(1, bottom - top)
        return (
            max(left, min(left + rel_x, left + width - 1)),
            max(top, min(top + rel_y, top + height - 1)),
        )

    def _resolve_screen_coordinates(self, hwnd: int, rel_x: int, rel_y: int) -> tuple[int, int]:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        if width < 300 or height < 300:
            raise RuntimeError("Invalid window size")
        screen_x = left + rel_x
        screen_y = top + rel_y
        if not (left <= screen_x <= right and top <= screen_y <= bottom):
            raise RuntimeError("Step outside target window")
        return screen_x, screen_y
