from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import configparser
import os
from pathlib import Path
import shlex
import subprocess

import pythoncom
from pywinauto.application import Application
from win32com.client import Dispatch, GetObject

from core.launch.onec_profile import OneCLaunchProfile


@dataclass(slots=True)
class LaunchResult:
    success: bool
    process: subprocess.Popen | None = None
    process_id: int | None = None
    exe_path: str = ""
    launch_arguments: list[str] | None = None
    command_line: str = ""
    baseline_process_ids: list[int] | None = None
    launched_at: str = ""
    message: str = ""


@dataclass(slots=True)
class OneCProcessInfo:
    process_id: int
    executable_path: str
    command_line: str
    created_at: str

    @property
    def launch_arguments(self) -> list[str]:
        if not self.command_line:
            return []
        parts = shlex.split(self.command_line, posix=False)
        if len(parts) <= 1:
            return []
        return parts[1:]


class OneCLauncherService:
    def __init__(self, manual_override: str | None = None) -> None:
        self.manual_override = manual_override

    def ibases_path(self) -> Path:
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "1C" / "1CEStart" / "ibases.v8i"

    def list_known_bases(self) -> dict[str, str]:
        path = self.ibases_path()
        if not path.exists():
            return {}
        for encoding in ("utf-8-sig", "utf-8"):
            try:
                content = path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
            parser = configparser.ConfigParser(interpolation=None)
            parser.optionxform = str
            try:
                parser.read_string(content)
            except configparser.Error:
                continue
            bases: dict[str, str] = {}
            for section in parser.sections():
                connect = parser.get(section, "Connect", fallback="")
                bases[section] = connect
            return bases
        return {}

    def build_launch_arguments_for_base(self, base_name: str) -> list[str]:
        normalized = base_name.strip()
        if not normalized:
            return []
        if normalized not in self.list_known_bases():
            return []
        return ["/IBName", normalized]

    def resolve_runtime_base_name(self, hwnd: int) -> str | None:
        if hwnd <= 0:
            return None
        known_names = sorted(self.list_known_bases(), key=len, reverse=True)
        if not known_names:
            return None
        try:
            app = Application(backend="uia").connect(handle=hwnd)
            window = app.window(handle=hwnd)
            texts = {window.window_text().strip()}
            for descendant in window.descendants():
                try:
                    text = descendant.window_text().strip()
                except Exception:  # noqa: BLE001
                    continue
                if text:
                    texts.add(text)
            for base_name in known_names:
                if base_name in texts:
                    return base_name
        except Exception:  # noqa: BLE001
            return None
        return None

    def search_candidates(self) -> list[Path]:
        candidates: list[Path] = []
        if self.manual_override:
            override_path = Path(self.manual_override)
            if override_path.exists():
                return [override_path]
        candidates.extend(self.resolve_shortcut_candidates())

        typical_roots = [
            Path(r"C:\Program Files\1cv8\common"),
            Path(r"C:\Program Files\1cv8"),
            Path(r"C:\Program Files (x86)\1cv8\common"),
            Path(r"C:\Program Files (x86)\1cv8"),
        ]
        for root in typical_roots:
            if not root.exists():
                continue
            if root.is_file() and root.name.lower() == "1cv8.exe":
                candidates.append(root)
                continue
            for match in root.rglob("1cv8.exe"):
                candidates.append(match)
        deduplicated: dict[str, Path] = {}
        for candidate in candidates:
            deduplicated[str(candidate).lower()] = candidate
        return list(deduplicated.values())

    def resolve_exe(self) -> Path | None:
        candidates = self.search_candidates()
        return candidates[0] if candidates else None

    def launch(
        self,
        profile: OneCLaunchProfile | None = None,
        explicit_path: str | None = None,
    ) -> LaunchResult:
        exe_path = Path(explicit_path) if explicit_path else Path(profile.exe_path) if profile else self.resolve_exe()
        if exe_path is None or not exe_path.exists():
            return LaunchResult(success=False, message="Файл 1cv8.exe не найден.")
        args = [str(exe_path)]
        if profile:
            args.extend(profile.launch_arguments)
        baseline = self.list_processes()
        try:
            process = subprocess.Popen(args)
        except OSError as exc:
            return LaunchResult(success=False, exe_path=str(exe_path), message=str(exc))
        return LaunchResult(
            success=True,
            process=process,
            process_id=process.pid,
            exe_path=str(exe_path),
            launch_arguments=args[1:],
            command_line=subprocess.list2cmdline(args),
            baseline_process_ids=[item.process_id for item in baseline],
            launched_at=datetime.now(UTC).isoformat(),
            message="1С запущена.",
        )

    def list_processes(self) -> list[OneCProcessInfo]:
        processes: list[OneCProcessInfo] = []
        pythoncom.CoInitialize()
        try:
            service = GetObject("winmgmts:")
            for process in service.ExecQuery("SELECT ProcessId, ExecutablePath, CommandLine, CreationDate, Name FROM Win32_Process WHERE Name='1cv8.exe'"):
                processes.append(
                    OneCProcessInfo(
                        process_id=int(process.ProcessId),
                        executable_path=str(process.ExecutablePath or ""),
                        command_line=str(process.CommandLine or ""),
                        created_at=str(process.CreationDate or ""),
                    )
                )
        except Exception:  # noqa: BLE001
            return []
        finally:
            pythoncom.CoUninitialize()
        return processes

    def get_process_info(self, process_id: int) -> OneCProcessInfo | None:
        for process in self.list_processes():
            if process.process_id == process_id:
                return process
        return None

    def resolve_shortcut_candidates(self) -> list[Path]:
        desktop_roots = [
            Path.home() / "Desktop",
            Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop",
        ]
        candidates: list[Path] = []
        com_initialized = False
        try:
            pythoncom.CoInitialize()
            com_initialized = True
            shell = Dispatch("WScript.Shell")
            for root in desktop_roots:
                if not root.exists():
                    continue
                for shortcut_path in root.glob("*.lnk"):
                    if "1с" not in shortcut_path.stem.lower() and "1c" not in shortcut_path.stem.lower():
                        continue
                    try:
                        shortcut = shell.CreateShortcut(str(shortcut_path))
                    except Exception:  # noqa: BLE001
                        continue
                    target_path = Path(str(shortcut.Targetpath or ""))
                    if target_path.exists() and target_path.name.lower() == "1cv8.exe":
                        candidates.append(target_path)
        except Exception:  # noqa: BLE001
            return []
        finally:
            if com_initialized:
                pythoncom.CoUninitialize()
        return candidates
