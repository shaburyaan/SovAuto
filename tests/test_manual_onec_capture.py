from __future__ import annotations

from PyQt6.QtWidgets import QWidget

from core.automation.window_service import WindowInfo, WindowService
from ui.host.onec_embed_controller import OneCEmbedController


def _window(
    hwnd: int,
    title: str,
    *,
    process_id: int = 100,
    bounds: tuple[int, int, int, int] = (0, 0, 900, 700),
    style: int = 0,
    process_path: str = r"C:\Program Files\1cv8\8.3.24.1548\bin\1cv8.exe",
) -> WindowInfo:
    return WindowInfo(
        hwnd=hwnd,
        title=title,
        class_name="V8TopLevelFrameSDI",
        process_name="1cv8.exe",
        process_id=process_id,
        bounds=bounds,
        visible=True,
        parent_hwnd=0,
        owner_hwnd=0,
        style=style,
        process_path=process_path,
    )


def test_find_existing_onec_window_prefers_working_window_over_transitional(monkeypatch) -> None:
    service = WindowService()
    primary = _window(101, "Продажа товаров и услуг", process_id=501, bounds=(0, 0, 1400, 900))
    login = _window(103, "1С:Предприятие", process_id=501, bounds=(0, 0, 1200, 800))
    other = _window(102, "Some other app", process_id=502, bounds=(0, 0, 800, 600))

    def fake_enum(callback, _: int) -> None:
        callback(other.hwnd, 0)
        callback(login.hwnd, 0)
        callback(primary.hwnd, 0)

    monkeypatch.setattr("core.automation.window_service.win32gui.EnumWindows", fake_enum)
    monkeypatch.setattr(service, "is_window", lambda hwnd: hwnd in {101, 102, 103})
    monkeypatch.setattr(
        service,
        "get_window_info",
        lambda hwnd, process_name="1cv8.exe": {101: primary, 102: other, 103: login}[hwnd],
    )
    primary.process_name = "1cv8.exe"
    login.process_name = "1cv8.exe"
    other.process_name = "notepad.exe"

    selected = service.find_existing_onec_window()

    assert selected is not None
    assert selected.hwnd == primary.hwnd


def test_find_existing_onec_window_filters_by_expected_executable_path(monkeypatch) -> None:
    service = WindowService()
    matching = _window(
        201,
        "Управление торговлей",
        process_id=601,
        process_path=r"C:\Program Files\1cv8\8.3.24.1548\bin\1cv8.exe",
    )
    other = _window(
        202,
        "Управление торговлей",
        process_id=602,
        process_path=r"D:\Portable1C\bin\1cv8.exe",
    )

    def fake_enum(callback, _: int) -> None:
        callback(other.hwnd, 0)
        callback(matching.hwnd, 0)

    monkeypatch.setattr("core.automation.window_service.win32gui.EnumWindows", fake_enum)
    monkeypatch.setattr(service, "is_window", lambda hwnd: hwnd in {201, 202})
    monkeypatch.setattr(
        service,
        "get_window_info",
        lambda hwnd, process_name="1cv8.exe": {201: matching, 202: other}[hwnd],
    )

    selected = service.find_existing_onec_window(
        executable_path=r"C:\Program Files\1cv8\8.3.24.1548\bin\1cv8.exe"
    )

    assert selected is not None
    assert selected.hwnd == matching.hwnd


def test_get_window_info_uses_normal_rect_for_minimized_window(monkeypatch) -> None:
    service = WindowService()
    monkeypatch.setattr("core.automation.window_service.win32process.GetWindowThreadProcessId", lambda hwnd: (1, 501))
    monkeypatch.setattr("core.automation.window_service.win32gui.GetWindowRect", lambda hwnd: (-32000, -32000, -31840, -31972))
    monkeypatch.setattr("core.automation.window_service.win32gui.GetWindowPlacement", lambda hwnd: (2, 2, (-32062, -32000), (-1, -1), (0, 1, 768, 785)))
    monkeypatch.setattr("core.automation.window_service.win32gui.GetParent", lambda hwnd: 0)
    monkeypatch.setattr("core.automation.window_service.win32gui.GetWindow", lambda hwnd, flag: 0)
    monkeypatch.setattr("core.automation.window_service.win32gui.GetWindowLong", lambda hwnd, flag: 0)
    monkeypatch.setattr("core.automation.window_service.win32gui.IsWindowVisible", lambda hwnd: 1)
    monkeypatch.setattr("core.automation.window_service.win32gui.IsIconic", lambda hwnd: 1)
    monkeypatch.setattr("core.automation.window_service.win32gui.IsWindow", lambda hwnd: 1)
    monkeypatch.setattr("core.automation.window_service.win32gui.GetWindowText", lambda hwnd: "Управление торговлей, редакция 11")
    monkeypatch.setattr("core.automation.window_service.win32gui.GetClassName", lambda hwnd: "V8TopLevelFrameSDI")
    monkeypatch.setattr(service, "_process_image_path", lambda process_id: r"C:\Program Files\1cv8\8.3.24.1548\bin\1cv8.exe")

    info = service.get_window_info(777)

    assert info.bounds == (0, 1, 768, 785)
    assert service.is_main_window(info) is True


def test_attach_is_one_time_for_new_hwnd(monkeypatch, qtbot) -> None:
    host = QWidget()
    host.resize(800, 600)
    host.show()
    qtbot.addWidget(host)

    controller = OneCEmbedController()
    container = QWidget(host)
    set_parent_calls: list[tuple[int, int]] = []
    apply_style_calls: list[int] = []

    monkeypatch.setattr("ui.host.onec_embed_controller.QWindow.fromWinId", lambda hwnd: object())
    monkeypatch.setattr(
        "ui.host.onec_embed_controller.QWidget.createWindowContainer",
        lambda foreign_window, parent: container,
    )
    monkeypatch.setattr(controller.window_service, "set_parent", lambda hwnd, parent: set_parent_calls.append((hwnd, parent)))
    monkeypatch.setattr(controller.window_service, "apply_embed_style", lambda hwnd: apply_style_calls.append(hwnd) or 0)
    monkeypatch.setattr(controller, "sync_geometry", lambda host_widget, force=False: None)

    first = controller.attach(111, host)
    second = controller.attach(222, host)

    assert first is container
    assert second is container
    assert controller.primary_hwnd() == 111
    assert set_parent_calls and set_parent_calls[0][0] == 111
    assert apply_style_calls == [111]
