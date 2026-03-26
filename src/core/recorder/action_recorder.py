from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal
import win32api
from pynput import keyboard, mouse

from core.automation.window_service import WindowService


class ActionRecorder(QObject):
    MODE_NAVIGATION = "navigation"
    MODE_INPUT = "input"

    click_captured = pyqtSignal(int, int, str)
    error_occurred = pyqtSignal(str)
    state_changed = pyqtSignal(bool, str)
    stop_requested = pyqtSignal()

    def __init__(self, window_service: WindowService | None = None) -> None:
        super().__init__()
        self.window_service = window_service or WindowService()
        self._mouse_listener: mouse.Listener | None = None
        self._keyboard_listener: keyboard.Listener | None = None
        self._is_recording = False
        self._decision_pending = False
        self._alt_pressed = False
        self._stop_requested = False
        self._hwnd: int | None = None
        self._mode = self.MODE_NAVIGATION
        self._pending_relative: tuple[int, int] | None = None
        self._step_counter = 0

    def start_recording(self, hwnd: int, mode: str) -> bool:
        if not self.window_service.is_window(hwnd):
            self.error_occurred.emit("Окно 1С недоступно для записи.")
            return False
        self.stop_recording()
        self._hwnd = hwnd
        self._mode = mode
        self._pending_relative = None
        self._decision_pending = False
        self._alt_pressed = False
        self._stop_requested = False
        self._is_recording = True
        self._mouse_listener = mouse.Listener(on_click=self._on_listener_click)
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_listener_key_press,
            on_release=self._on_listener_key_release,
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()
        self.state_changed.emit(True, mode)
        return True

    def stop_recording(self) -> None:
        if self._mouse_listener is not None:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._keyboard_listener is not None:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        self._is_recording = False
        self._decision_pending = False
        self._alt_pressed = False
        self._stop_requested = False
        self._pending_relative = None
        self.state_changed.emit(False, self._mode)

    def on_mouse_click(self, x: int, y: int) -> None:
        if not self._is_recording or self._hwnd is None:
            return
        relative = self._screen_to_relative(self._hwnd, x, y)
        if relative is None or self._decision_pending:
            return
        self._pending_relative = relative
        self._decision_pending = True
        self.click_captured.emit(relative[0], relative[1], self._mode)

    def on_key_input(self, text: str) -> dict[str, Any]:
        if self._pending_relative is None:
            raise RuntimeError("Input capture requested without pending click.")
        x, y = self._pending_relative
        return self._build_step("input", x, y, text=text)

    def accept_pending_click(self, text: str = "") -> dict[str, Any]:
        if self._pending_relative is None:
            raise RuntimeError("No pending click to accept.")
        x, y = self._pending_relative
        if self._mode == self.MODE_INPUT:
            step = self._build_step("input", x, y, text=text)
        else:
            step = self._build_step("click", x, y)
        self._pending_relative = None
        self._decision_pending = False
        return step

    def reject_pending_click(self) -> None:
        self._pending_relative = None
        self._decision_pending = False

    def is_recording(self) -> bool:
        return self._is_recording

    def current_mode(self) -> str:
        return self._mode

    def current_hwnd(self) -> int | None:
        return self._hwnd

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        if self._is_recording:
            self.state_changed.emit(True, mode)

    def _on_listener_click(self, x: int, y: int, button, pressed: bool) -> None:
        return

    def _on_listener_key_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if not self._is_recording or self._stop_requested:
            return
        if key in {keyboard.Key.esc, keyboard.Key.f8}:
            self._stop_requested = True
            self.stop_requested.emit()
            return
        if key in {keyboard.Key.alt_l, keyboard.Key.alt_r}:
            if self._alt_pressed:
                return
            self._alt_pressed = True
            self.handle_record_trigger()

    def _on_listener_key_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if key in {keyboard.Key.alt_l, keyboard.Key.alt_r}:
            self._alt_pressed = False

    def handle_record_trigger(self) -> None:
        try:
            x, y = win32api.GetCursorPos()
        except Exception:  # noqa: BLE001
            self.error_occurred.emit("Не удалось получить позицию курсора для записи.")
            return
        self.on_mouse_click(x, y)

    def _screen_to_relative(self, hwnd: int, x: int, y: int) -> tuple[int, int] | None:
        if not self.window_service.is_window(hwnd):
            self.error_occurred.emit("Окно 1С было закрыто во время записи.")
            return None
        window = self.window_service.get_window_info(hwnd)
        left, top, right, bottom = window.bounds
        if not (left <= x <= right and top <= y <= bottom):
            return None
        return (x - left, y - top)

    def _build_step(self, step_type: str, x: int, y: int, text: str = "") -> dict[str, Any]:
        self._step_counter += 1
        step: dict[str, Any] = {
            "id": f"rec-{self._step_counter}",
            "type": step_type,
            "x": x,
            "y": y,
        }
        if step_type == "input":
            step["text"] = text
        return step
