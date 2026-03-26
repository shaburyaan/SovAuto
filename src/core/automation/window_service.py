from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import re
from pathlib import Path

import win32api
import win32con
import win32gui
import win32process


@dataclass(slots=True)
class WindowInfo:
    hwnd: int
    title: str
    class_name: str
    process_name: str
    process_id: int
    bounds: tuple[int, int, int, int]
    visible: bool
    parent_hwnd: int
    owner_hwnd: int
    style: int
    process_path: str = ""


class WindowService:
    MIN_MAIN_WIDTH = 300
    MIN_MAIN_HEIGHT = 300
    EMBED_REMOVE_STYLES = (
        win32con.WS_POPUP
        | win32con.WS_CAPTION
        | win32con.WS_THICKFRAME
        | win32con.WS_SYSMENU
        | win32con.WS_MINIMIZEBOX
        | win32con.WS_MAXIMIZEBOX
    )
    EMBED_ADD_STYLES = (
        win32con.WS_CHILD
        | win32con.WS_VISIBLE
        | win32con.WS_CLIPSIBLINGS
        | win32con.WS_CLIPCHILDREN
    )

    def __init__(self) -> None:
        self._stable_candidates: dict[int, tuple[int, int]] = {}
        self._kernel32 = ctypes.windll.kernel32

    def find_window(self, process_name: str, title_pattern: str) -> WindowInfo | None:
        result: WindowInfo | None = None

        def callback(hwnd: int, _: int) -> None:
            nonlocal result
            if result is not None or not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not re.search(title_pattern, title, re.IGNORECASE):
                return
            info = self.get_window_info(hwnd, process_name)
            if self.is_embed_candidate(info):
                result = info

        win32gui.EnumWindows(callback, 0)
        return result

    def find_existing_onec_window(
        self,
        process_name: str = "1cv8.exe",
        executable_path: str | None = None,
    ) -> WindowInfo | None:
        candidates: list[WindowInfo] = []
        expected_name = process_name.lower()
        expected_path = self._normalize_path(executable_path)

        def callback(hwnd: int, _: int) -> None:
            if not self.is_window(hwnd):
                return
            info = self.get_window_info(hwnd, process_name)
            if not self.is_main_window(info):
                return
            if info.process_name.lower() != expected_name:
                return
            if expected_path and self._normalize_path(info.process_path) != expected_path:
                return
            candidates.append(info)

        win32gui.EnumWindows(callback, 0)
        if not candidates:
            return None
        candidates.sort(
            key=lambda item: (
                self.is_working_window(item),
                item.owner_hwnd == 0,
                self.runtime_priority(item),
                self.window_area(item),
                len(item.title),
            ),
            reverse=True,
        )
        return candidates[0]

    def get_window_info(self, hwnd: int, process_name: str = "1cv8.exe") -> WindowInfo:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        left, top, right, bottom = self._window_bounds(hwnd)
        parent_hwnd = win32gui.GetParent(hwnd)
        owner_hwnd = win32gui.GetWindow(hwnd, win32con.GW_OWNER)
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        actual_process_path = self._process_image_path(pid)
        actual_process_name = Path(actual_process_path).name.lower() if actual_process_path else process_name
        return WindowInfo(
            hwnd=hwnd,
            title=win32gui.GetWindowText(hwnd),
            class_name=win32gui.GetClassName(hwnd),
            process_name=actual_process_name,
            process_id=pid,
            bounds=(left, top, right, bottom),
            visible=bool(win32gui.IsWindowVisible(hwnd)),
            parent_hwnd=parent_hwnd,
            owner_hwnd=owner_hwnd,
            style=style,
            process_path=actual_process_path,
        )

    def enumerate_child_windows(self, hwnd: int, process_name: str = "1cv8.exe") -> list[WindowInfo]:
        windows: dict[int, WindowInfo] = {}

        def callback(child_hwnd: int, _: int) -> None:
            if child_hwnd in windows:
                return
            try:
                windows[child_hwnd] = self.get_window_info(child_hwnd, process_name)
            except Exception:  # noqa: BLE001
                return

        if not self.is_window(hwnd):
            return []
        win32gui.EnumChildWindows(hwnd, callback, 0)
        return list(windows.values())

    def is_foreground(self, hwnd: int) -> bool:
        return win32gui.GetForegroundWindow() == hwnd

    def restore_and_focus(self, hwnd: int) -> None:
        if not self.is_window(hwnd):
            return
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:  # noqa: BLE001
            return

    def activate_window(self, hwnd: int) -> None:
        if not self.is_window(hwnd):
            return
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except Exception:  # noqa: BLE001
            pass
        try:
            win32gui.BringWindowToTop(hwnd)
        except Exception:  # noqa: BLE001
            pass
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:  # noqa: BLE001
            pass
        try:
            win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        except Exception:  # noqa: BLE001
            pass
        try:
            win32gui.SetActiveWindow(hwnd)
        except Exception:  # noqa: BLE001
            pass
        try:
            win32gui.SetFocus(hwnd)
        except Exception:  # noqa: BLE001
            pass

    def focus_target(self, hwnd: int, process_name: str = "1cv8.exe") -> int:
        return hwnd

    def enumerate_process_windows(self, process_id: int, process_name: str = "1cv8.exe") -> list[WindowInfo]:
        windows: dict[int, WindowInfo] = {}

        def collect(hwnd: int) -> None:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
            except Exception:  # noqa: BLE001
                return
            if pid != process_id:
                return
            windows[hwnd] = self.get_window_info(hwnd, process_name)

        def top_callback(hwnd: int, _: int) -> None:
            collect(hwnd)

        win32gui.EnumWindows(top_callback, 0)
        return list(windows.values())

    def enumerate_owned_windows(
        self,
        process_id: int,
        process_name: str = "1cv8.exe",
        excluded_hwnds: set[int] | None = None,
        owner_hwnd: int | None = None,
    ) -> list[WindowInfo]:
        excluded = excluded_hwnds or set()
        return [
            window
            for window in self.enumerate_process_windows(process_id, process_name)
            if window.hwnd not in excluded
            and self.should_track_owned_window(window)
            and (owner_hwnd is None or window.owner_hwnd == owner_hwnd)
        ]

    def find_main_window_by_pid(self, process_id: int, process_name: str = "1cv8.exe") -> WindowInfo | None:
        candidates = [
            window
            for window in self.enumerate_process_windows(process_id, process_name)
            if self.is_main_window(window)
        ]
        if not candidates:
            self._stable_candidates.pop(process_id, None)
            return None
        candidates.sort(
            key=lambda item: (
                self.runtime_priority(item),
                self.window_area(item),
                len(item.title),
            ),
            reverse=True,
        )
        candidate = candidates[0]
        last_hwnd, stable_count = self._stable_candidates.get(process_id, (0, 0))
        stable_count = stable_count + 1 if last_hwnd == candidate.hwnd else 1
        self._stable_candidates[process_id] = (candidate.hwnd, stable_count)
        if stable_count < 2:
            return None
        return candidate

    def window_area(self, window: WindowInfo) -> int:
        left, top, right, bottom = window.bounds
        return max(0, right - left) * max(0, bottom - top)

    def is_embed_candidate(self, window: WindowInfo) -> bool:
        return self.is_main_frame_candidate(window)

    def is_main_window(self, window: WindowInfo) -> bool:
        left, top, right, bottom = window.bounds
        width = right - left
        height = bottom - top
        return (
            window.visible
            and window.parent_hwnd == 0
            and not bool(window.style & win32con.WS_CHILD)
            and width > self.MIN_MAIN_WIDTH
            and height > self.MIN_MAIN_HEIGHT
            and not self.is_noise_window(window)
        )

    def is_runtime_candidate(self, window: WindowInfo) -> bool:
        return self.is_main_window(window)

    def is_main_frame_candidate(self, window: WindowInfo) -> bool:
        return self.is_main_window(window) and window.owner_hwnd == 0

    def is_launcher_window(self, window: WindowInfo) -> bool:
        normalized = window.title.strip().lower()
        return normalized.startswith("запуск 1с")

    def is_loading_window(self, window: WindowInfo) -> bool:
        return window.title.strip().lower().startswith("загрузка конфигурационной информации")

    def is_access_window(self, window: WindowInfo) -> bool:
        return window.title.strip().lower().startswith("доступ к информационной базе")

    def is_login_window(self, window: WindowInfo) -> bool:
        return window.title.strip().lower() == "1с:предприятие"

    def is_transitional_window(self, window: WindowInfo) -> bool:
        return self.is_loading_window(window) or self.is_access_window(window) or self.is_login_window(window)

    def runtime_priority(self, window: WindowInfo) -> int:
        if self.is_working_window(window):
            return 4
        if self.is_transitional_window(window):
            return 3
        if self.is_launcher_window(window):
            return 2
        return 1

    def is_working_window(self, window: WindowInfo) -> bool:
        return self.is_main_window(window) and not self.is_launcher_window(window) and not self.is_transitional_window(window)

    def is_noise_window(self, window: WindowInfo) -> bool:
        class_name = window.class_name.strip()
        return class_name in {
            "V8ToolTipWindow",
            "V8ValidationMessageWnd",
            "V8ConfirmationWindowTaxi",
            "V8CloseAllButton",
            "V8EMSGServer",
            "IME",
            "MSCTFIME UI",
        }

    def should_track_owned_window(self, window: WindowInfo) -> bool:
        return (
            window.visible
            and window.owner_hwnd != 0
            and not bool(window.style & win32con.WS_CHILD)
            and self.window_area(window) > 0
            and not self.is_noise_window(window)
        )

    def get_parent_hwnd(self, hwnd: int) -> int:
        if not self.is_window(hwnd):
            return 0
        try:
            return win32gui.GetParent(hwnd)
        except Exception:  # noqa: BLE001
            return 0

    def is_window(self, hwnd: int) -> bool:
        return bool(win32gui.IsWindow(hwnd))

    def is_minimized(self, hwnd: int) -> bool:
        if not self.is_window(hwnd):
            return False
        try:
            return bool(win32gui.IsIconic(hwnd))
        except Exception:  # noqa: BLE001
            return False

    def is_top_level(self, hwnd: int) -> bool:
        if not self.is_window(hwnd):
            return False
        return self.get_parent_hwnd(hwnd) == 0 and not bool(
            win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE) & win32con.WS_CHILD
        )

    def set_parent(self, hwnd: int, parent_hwnd: int) -> None:
        win32gui.SetParent(hwnd, parent_hwnd)

    def apply_embed_style(self, hwnd: int) -> int:
        current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        updated_style = (current_style & ~self.EMBED_REMOVE_STYLES) | self.EMBED_ADD_STYLES
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, updated_style)
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            0,
            0,
            0,
            0,
            win32con.SWP_FRAMECHANGED
            | win32con.SWP_NOMOVE
            | win32con.SWP_NOSIZE
            | win32con.SWP_NOACTIVATE,
        )
        return current_style

    def restore_style(self, hwnd: int, style: int) -> None:
        if not self.is_window(hwnd):
            return
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            0,
            0,
            0,
            0,
            win32con.SWP_FRAMECHANGED
            | win32con.SWP_NOMOVE
            | win32con.SWP_NOSIZE
            | win32con.SWP_NOACTIVATE,
        )

    def sync_embedded_window(self, hwnd: int, bounds: tuple[int, int, int, int]) -> None:
        left, top, right, bottom = bounds
        width = max(1, right - left)
        height = max(1, bottom - top)
        win32gui.SetWindowPos(
            hwnd,
            0,
            left,
            top,
            width,
            height,
            win32con.SWP_NOACTIVATE | win32con.SWP_NOOWNERZORDER | win32con.SWP_NOZORDER,
        )

    def bring_to_front(self, hwnd: int) -> None:
        if not self.is_window(hwnd):
            return
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
        )


    def get_process_exit_code(self, process_id: int) -> int | None:
        handle = None
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
            return int(win32process.GetExitCodeProcess(handle))
        except Exception:  # noqa: BLE001
            return None
        finally:
            if handle is not None:
                win32api.CloseHandle(handle)

    def _process_basename(self, process_id: int) -> str:
        image_path = self._process_image_path(process_id)
        return Path(image_path).name.lower() if image_path else ""

    def _process_image_path(self, process_id: int) -> str:
        handle = self._kernel32.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
        if not handle:
            return ""
        try:
            buffer_size = wintypes.DWORD(1024)
            image_path = ctypes.create_unicode_buffer(buffer_size.value)
            result = self._kernel32.QueryFullProcessImageNameW(
                wintypes.HANDLE(handle),
                0,
                image_path,
                ctypes.byref(buffer_size),
            )
            if not result:
                return ""
            return image_path.value
        finally:
            self._kernel32.CloseHandle(handle)

    def _normalize_path(self, value: str | None) -> str:
        if not value:
            return ""
        try:
            return str(Path(value).resolve()).lower()
        except OSError:
            return str(Path(value)).lower()

    def _window_bounds(self, hwnd: int) -> tuple[int, int, int, int]:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        if not self.is_minimized(hwnd):
            return left, top, right, bottom
        try:
            placement = win32gui.GetWindowPlacement(hwnd)
            normal_left, normal_top, normal_right, normal_bottom = placement[4]
            if normal_right > normal_left and normal_bottom > normal_top:
                return normal_left, normal_top, normal_right, normal_bottom
        except Exception:  # noqa: BLE001
            pass
        return left, top, right, bottom
