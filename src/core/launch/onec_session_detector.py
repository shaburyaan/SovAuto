from __future__ import annotations

from dataclasses import dataclass
from time import sleep

from core.automation.window_service import WindowInfo, WindowService
from core.launch.onec_launcher import OneCLauncherService


@dataclass(slots=True)
class DetectedOneCSession:
    window: WindowInfo
    base_hint: str
    process_id: int
    launch_arguments: list[str]
    command_line: str
    tracked_process_ids: list[int]


class OneCSessionDetector:
    def __init__(
        self,
        window_service: WindowService | None = None,
        launcher_service: OneCLauncherService | None = None,
    ) -> None:
        self.window_service = window_service or WindowService()
        self.launcher_service = launcher_service or OneCLauncherService()

    def wait_for_main_window(
        self,
        process_id: int,
        baseline_process_ids: list[int] | None = None,
        timeout_seconds: int = 60,
    ) -> DetectedOneCSession | None:
        baseline = set(baseline_process_ids or [])
        baseline.discard(process_id)
        elapsed = 0.0
        stable_cycles = 0
        last_candidate_key: tuple[int, int, str] | None = None
        best_session: DetectedOneCSession | None = None
        while elapsed <= timeout_seconds:
            candidate_session = self.probe_main_window(process_id, list(baseline))
            if candidate_session is not None:
                best_session = self._choose_stronger_session(best_session, candidate_session)
                candidate_key = (
                    candidate_session.process_id,
                    candidate_session.window.hwnd,
                    candidate_session.window.title,
                )
                if candidate_key == last_candidate_key:
                    stable_cycles += 1
                else:
                    stable_cycles = 1
                    last_candidate_key = candidate_key
                if stable_cycles >= 2 and self.is_mature_session(candidate_session):
                    return candidate_session
                if elapsed >= 10.0 and best_session is not None and self.is_mature_session(best_session):
                    return best_session
            sleep(0.5)
            elapsed += 0.5
        if best_session is not None and self.is_mature_session(best_session):
            return best_session
        return None

    def probe_main_window(
        self,
        process_id: int,
        baseline_process_ids: list[int] | None = None,
    ) -> DetectedOneCSession | None:
        baseline = set(baseline_process_ids or [])
        baseline.discard(process_id)
        process_map = {item.process_id: item for item in self.launcher_service.list_processes()}
        candidate_pids = self._candidate_process_ids(process_id, baseline, process_map)

        strongest_window: WindowInfo | None = None
        strongest_pid: int | None = None
        for candidate_pid in candidate_pids:
            window = self.window_service.find_main_window_by_pid(candidate_pid)
            if window is None:
                continue
            if strongest_window is None:
                strongest_window = window
                strongest_pid = candidate_pid
                continue
            current_score = (
                self.window_service.runtime_priority(strongest_window),
                self.window_service.window_area(strongest_window),
            )
            candidate_score = (
                self.window_service.runtime_priority(window),
                self.window_service.window_area(window),
            )
            if candidate_score > current_score:
                strongest_window = window
                strongest_pid = candidate_pid

        if strongest_window is None or strongest_pid is None:
            return None

        process_info = process_map.get(strongest_pid)
        command_line = process_info.command_line if process_info is not None else ""
        launch_arguments = process_info.launch_arguments if process_info is not None else []
        base_hint = self._extract_base_hint(strongest_window.title, launch_arguments)
        tracked_process_ids = list(candidate_pids)
        return DetectedOneCSession(
            window=strongest_window,
            base_hint=base_hint,
            process_id=strongest_pid,
            launch_arguments=launch_arguments,
            command_line=command_line,
            tracked_process_ids=tracked_process_ids,
        )

    @staticmethod
    def _extract_base_hint(window_title: str, launch_arguments: list[str]) -> str:
        for index, arg in enumerate(launch_arguments):
            normalized = arg.lower()
            if normalized in {"/f", "/s", "/ibname"} and index + 1 < len(launch_arguments):
                return launch_arguments[index + 1].strip().strip('"')
        parts = [part.strip() for part in window_title.split("-") if part.strip()]
        if len(parts) >= 2:
            return parts[0]
        return window_title.strip()

    def is_mature_session(self, session: DetectedOneCSession) -> bool:
        area = self.window_service.window_area(session.window)
        if self.window_service.is_launcher_window(session.window):
            return area >= 250000
        return area >= 80000

    def _choose_stronger_session(
        self,
        current: DetectedOneCSession | None,
        candidate: DetectedOneCSession,
    ) -> DetectedOneCSession:
        if current is None:
            return candidate
        if self.window_service.runtime_priority(candidate.window) > self.window_service.runtime_priority(current.window):
            return candidate
        if self.window_service.runtime_priority(candidate.window) < self.window_service.runtime_priority(current.window):
            return current
        current_score = self.window_service.window_area(current.window)
        candidate_score = self.window_service.window_area(candidate.window)
        if candidate_score > current_score:
            return candidate
        return current

    def choose_stronger_session(
        self,
        current: DetectedOneCSession | None,
        candidate: DetectedOneCSession,
    ) -> DetectedOneCSession:
        return self._choose_stronger_session(current, candidate)

    @staticmethod
    def _candidate_process_ids(
        process_id: int,
        baseline: set[int],
        process_map: dict[int, object],
    ) -> list[int]:
        anchor_process = process_map.get(process_id)
        candidate_pids = [process_id]
        anchor_path = str(getattr(anchor_process, "executable_path", "") or "").lower()
        anchor_created_at = str(getattr(anchor_process, "created_at", "") or "")
        anchor_args = tuple(str(arg).lower() for arg in getattr(anchor_process, "launch_arguments", []) or [])
        for pid, process_info in process_map.items():
            if pid in baseline or pid in candidate_pids:
                continue
            if anchor_path and str(getattr(process_info, "executable_path", "") or "").lower() != anchor_path:
                continue
            created_at = str(getattr(process_info, "created_at", "") or "")
            if anchor_created_at and created_at and created_at < anchor_created_at:
                continue
            candidate_args = tuple(str(arg).lower() for arg in getattr(process_info, "launch_arguments", []) or [])
            if anchor_args and candidate_args and candidate_args != anchor_args:
                continue
            candidate_pids.append(pid)
        return candidate_pids
