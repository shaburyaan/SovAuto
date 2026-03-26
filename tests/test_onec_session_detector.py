from dataclasses import dataclass

from core.automation.window_service import WindowInfo, WindowService
from core.launch.onec_session_detector import OneCSessionDetector


@dataclass
class FakeProcessInfo:
    process_id: int
    executable_path: str
    command_line: str
    created_at: str

    @property
    def launch_arguments(self) -> list[str]:
        return self.command_line.split()[1:]


class FakeWindowService:
    def __init__(self, windows_by_pid: dict[int, WindowInfo]) -> None:
        self.windows_by_pid = windows_by_pid

    def find_main_window_by_pid(self, process_id: int, process_name: str = "1cv8.exe") -> WindowInfo | None:
        return self.windows_by_pid.get(process_id)

    @staticmethod
    def window_area(window: WindowInfo) -> int:
        left, top, right, bottom = window.bounds
        return max(0, right - left) * max(0, bottom - top)

    @staticmethod
    def is_launcher_window(window: WindowInfo) -> bool:
        return window.title.strip().lower().startswith("запуск 1с")

    @staticmethod
    def is_loading_window(window: WindowInfo) -> bool:
        return window.title.strip().lower().startswith("загрузка конфигурационной информации")

    @staticmethod
    def is_access_window(window: WindowInfo) -> bool:
        return window.title.strip().lower().startswith("доступ к информационной базе")

    def is_transitional_window(self, window: WindowInfo) -> bool:
        return self.is_loading_window(window) or self.is_access_window(window) or window.title.strip().lower() == "1с:предприятие"

    def is_main_window(self, window: WindowInfo) -> bool:
        return self.window_area(window) > 0

    def is_working_window(self, window: WindowInfo) -> bool:
        return self.is_main_window(window) and not self.is_launcher_window(window) and not self.is_transitional_window(window)

    def runtime_priority(self, window: WindowInfo) -> int:
        if self.is_working_window(window):
            return 4
        if self.is_transitional_window(window):
            return 3
        if self.is_launcher_window(window):
            return 2
        return 1


class FakeLauncherService:
    def __init__(self, processes: list[FakeProcessInfo]) -> None:
        self.processes = processes

    def list_processes(self) -> list[FakeProcessInfo]:
        return list(self.processes)


def _window(
    hwnd: int,
    title: str,
    *,
    process_id: int = 100,
    owner_hwnd: int = 0,
    bounds: tuple[int, int, int, int] = (0, 0, 900, 700),
) -> WindowInfo:
    return WindowInfo(
        hwnd=hwnd,
        title=title,
        class_name="V8Window",
        process_name="1cv8.exe",
        process_id=process_id,
        bounds=bounds,
        visible=True,
        parent_hwnd=0,
        owner_hwnd=owner_hwnd,
        style=0,
    )


def test_find_main_window_prefers_login_window_over_launcher(monkeypatch) -> None:
    service = WindowService()
    launcher_window = _window(1001, "Запуск 1С:Предприятия", bounds=(0, 0, 800, 600))
    login_window = _window(1002, "1С:Предприятие", owner_hwnd=1001, bounds=(0, 0, 820, 620))
    monkeypatch.setattr(service, "enumerate_process_windows", lambda process_id, process_name="1cv8.exe": [launcher_window, login_window])

    selected = service.find_main_window_by_pid(100)
    assert selected is None

    selected = service.find_main_window_by_pid(100)

    assert selected is not None
    assert selected.hwnd == login_window.hwnd


def test_probe_main_window_tracks_spawned_onec_processes() -> None:
    anchor_window = _window(2001, "Запуск 1С:Предприятия", process_id=200, bounds=(0, 0, 800, 600))
    runtime_window = _window(2002, "1С:Предприятие", process_id=201, owner_hwnd=2001, bounds=(0, 0, 1200, 800))
    detector = OneCSessionDetector(
        window_service=FakeWindowService({200: anchor_window, 201: runtime_window}),
        launcher_service=FakeLauncherService(
            [
                FakeProcessInfo(199, r"C:\Program Files\1cv8\bin\1cv8.exe", '"1cv8.exe" /IBName OLD', "20260325090000.000000+000"),
                FakeProcessInfo(200, r"C:\Program Files\1cv8\bin\1cv8.exe", '"1cv8.exe"', "20260325090100.000000+000"),
                FakeProcessInfo(201, r"C:\Program Files\1cv8\bin\1cv8.exe", '"1cv8.exe" /IBName SOVUT', "20260325090200.000000+000"),
            ]
        ),
    )

    session = detector.probe_main_window(process_id=200, baseline_process_ids=[199])

    assert session is not None
    assert session.process_id == 201
    assert session.window.hwnd == 2002
    assert session.tracked_process_ids == [200, 201]


def test_focus_target_prefers_deepest_titled_runtime_frame(monkeypatch) -> None:
    service = WindowService()
    root = _window(3001, "Доступ к информационной базе", bounds=(0, 0, 900, 700))
    root.class_name = "V8TopLevelFrameSDI"
    child = _window(3002, "1С:Предприятие", owner_hwnd=3001, bounds=(100, 100, 600, 420))
    child.class_name = "V8TopLevelFrameTaxiStarter"
    child.parent_hwnd = 3001
    monkeypatch.setattr(service, "is_window", lambda hwnd: hwnd in {3001, 3002})
    monkeypatch.setattr(service, "get_window_info", lambda hwnd, process_name="1cv8.exe": {3001: root, 3002: child}[hwnd])
    monkeypatch.setattr(service, "enumerate_child_windows", lambda hwnd, process_name="1cv8.exe": [child])
    monkeypatch.setattr(service, "get_parent_hwnd", lambda hwnd: {3001: 0, 3002: 3001}.get(hwnd, 0))

    assert service.focus_target(3001) == 3001
