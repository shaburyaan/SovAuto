from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtGui import QWindow
from PyQt6.QtWidgets import QWidget

import win32con

from core.automation.window_service import WindowService


@dataclass(slots=True)
class EmbeddedAuxWindow:
    hwnd: int
    original_style: int
    width: int
    height: int
    style_applied: bool


class OneCEmbedController:
    def __init__(self) -> None:
        self.window_service = WindowService()
        self._foreign_window: QWindow | None = None
        self._container: QWidget | None = None
        self._hwnd: int | None = None
        self._host_widget: QWidget | None = None
        self._original_styles: dict[int, int] = {}
        self._auxiliary_windows: dict[int, EmbeddedAuxWindow] = {}
        self._last_host_rect: tuple[int, int, int, int] | None = None
        self._is_attached = False
        self.last_error = ""

    def attach(self, hwnd: int, host_widget: QWidget) -> QWidget | None:
        self.last_error = ""
        if self._hwnd == hwnd and self._container is not None and self._host_widget is host_widget:
            return self._container
        if self._hwnd is not None:
            return self._container
        self._host_widget = host_widget
        try:
            self._foreign_window = QWindow.fromWinId(hwnd)
            self._container = QWidget.createWindowContainer(self._foreign_window, host_widget)
            self._container.setObjectName("onecPrimaryContainer")
            self._container.setFocusPolicy(host_widget.focusPolicy())
            self._hwnd = hwnd
            self._container.setGeometry(host_widget.rect())
            parent_hwnd = int(self._container.winId())
            self.window_service.set_parent(hwnd, parent_hwnd)
            self._original_styles[hwnd] = self.window_service.apply_embed_style(hwnd)
            self._is_attached = True
            self.sync_geometry(host_widget, force=True)
            return self._container
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            self.detach()
            return None

    def sync_geometry(self, host_widget: QWidget, force: bool = False) -> None:
        if self._hwnd is None or not host_widget.isVisible():
            return
        rect = host_widget.rect()
        current_rect = (rect.x(), rect.y(), rect.width(), rect.height())
        if not force and current_rect == self._last_host_rect:
            return
        self._last_host_rect = current_rect
        self.window_service.sync_embedded_window(
            self._hwnd,
            (
                0,
                0,
                rect.width(),
                rect.height(),
            ),
        )
        if self._container is not None:
            self._container.setGeometry(host_widget.rect())
        self._sync_auxiliary_windows(host_widget, force=force)

    def ensure_embedded(self, tracked_process_ids: list[int], host_widget: QWidget) -> bool:
        if self._hwnd is None or self._host_widget is None or not self._is_attached:
            return False
        primary_alive = self.window_service.is_window(self._hwnd)
        for process_id in tracked_process_ids:
            self._capture_process_windows(process_id, host_widget)
        if not primary_alive:
            self.last_error = "Primary 1C window switched during login/runtime transition."
            return False
        valid_parents = set()
        if self._container is not None:
            valid_parents.add(int(self._container.winId()))
        valid_parents.add(int(host_widget.winId()))
        if self.window_service.get_parent_hwnd(self._hwnd) not in valid_parents or self.window_service.is_top_level(self._hwnd):
            self.last_error = "Primary 1C window detached from host container."
            return False
        return True

    def _capture_process_windows(self, process_id: int, host_widget: QWidget) -> None:
        parent_hwnd = int(self._container.winId()) if self._container is not None else int(host_widget.winId())
        current_hwnds = set()
        excluded = {self._hwnd} if self._hwnd is not None else set()
        for window in self.window_service.enumerate_owned_windows(
            process_id,
            excluded_hwnds=excluded,
            owner_hwnd=self._hwnd,
        ):
            current_hwnds.add(window.hwnd)
            if not self.window_service.is_window(window.hwnd):
                continue
            if window.hwnd not in self._auxiliary_windows:
                self.window_service.set_parent(window.hwnd, parent_hwnd)
                width = max(320, window.bounds[2] - window.bounds[0])
                height = max(220, window.bounds[3] - window.bounds[1])
                self._auxiliary_windows[window.hwnd] = EmbeddedAuxWindow(
                    hwnd=window.hwnd,
                    original_style=window.style,
                    width=width,
                    height=height,
                    style_applied=False,
                )
                self._place_auxiliary_window(self._auxiliary_windows[window.hwnd], host_widget)
                continue
            if self.window_service.get_parent_hwnd(window.hwnd) != parent_hwnd:
                self.window_service.set_parent(window.hwnd, parent_hwnd)
                self._place_auxiliary_window(self._auxiliary_windows[window.hwnd], host_widget)
        stale_hwnds = [hwnd for hwnd in self._auxiliary_windows if hwnd not in current_hwnds]
        for hwnd in stale_hwnds:
            window = self._auxiliary_windows.pop(hwnd, None)
            if window is None or not self.window_service.is_window(hwnd):
                continue
            if window.style_applied:
                self.window_service.restore_style(hwnd, window.original_style)
            try:
                self.window_service.set_parent(hwnd, 0)
            except Exception:  # noqa: BLE001
                pass

    def _place_auxiliary_window(self, window: EmbeddedAuxWindow, host_widget: QWidget) -> None:
        if not self.window_service.is_window(window.hwnd):
            return
        rect = host_widget.rect()
        modal_width = min(window.width, max(320, rect.width() - 32))
        modal_height = min(window.height, max(220, rect.height() - 32))
        left = max(16, (rect.width() - modal_width) // 2)
        top = max(16, (rect.height() - modal_height) // 2)
        self.window_service.sync_embedded_window(
            window.hwnd,
            (left, top, left + modal_width, top + modal_height),
        )

    def _sync_auxiliary_windows(self, host_widget: QWidget, force: bool = False) -> None:
        if not self._auxiliary_windows:
            return
        for window in list(self._auxiliary_windows.values()):
            if not self.window_service.is_window(window.hwnd):
                self._auxiliary_windows.pop(window.hwnd, None)
                continue
            if force:
                self._place_auxiliary_window(window, host_widget)

    def lifecycle_cleanup(self) -> None:
        self.detach()

    def has_auxiliary_windows(self) -> bool:
        return any(self.window_service.is_window(hwnd) for hwnd in self._auxiliary_windows)

    def primary_hwnd(self) -> int | None:
        return self._hwnd

    def activate_primary(self) -> None:
        if self._hwnd is None:
            return
        self.window_service.activate_window(self._hwnd)

    def detach(self) -> None:
        if self._hwnd is not None and self._hwnd in self._original_styles:
            self.window_service.restore_style(self._hwnd, self._original_styles[self._hwnd])
            try:
                self.window_service.set_parent(self._hwnd, 0)
            except Exception:  # noqa: BLE001
                pass
        for window in list(self._auxiliary_windows.values()):
            if not self.window_service.is_window(window.hwnd):
                continue
            if window.style_applied:
                self.window_service.restore_style(window.hwnd, window.original_style)
            try:
                self.window_service.set_parent(window.hwnd, 0)
            except Exception:  # noqa: BLE001
                pass
        if self._container is not None:
            self._container.setParent(None)
            self._container.deleteLater()
        self._foreign_window = None
        self._container = None
        self._auxiliary_windows = {}
        self._original_styles = {}
        self._last_host_rect = None
        self._is_attached = False
        self._host_widget = None
        self._hwnd = None
