from __future__ import annotations

from pathlib import Path

import pythoncom
from win32com.client import Dispatch

from core.launch.onec_launcher import OneCLauncherService
from core.system.app_paths import AppPaths
from storage.repositories.settings_repository import SettingsRepository


class OneCShortcutService:
    SHORTCUT_NAME = "SovAuto 1C.lnk"

    def __init__(
        self,
        paths: AppPaths,
        settings_repository: SettingsRepository,
        base_hint: str = "SOVUT",
    ) -> None:
        self.paths = paths
        self.settings_repository = settings_repository
        self.base_hint = base_hint

    def ensure_local_shortcut(self) -> Path | None:
        exe_path = self._resolve_exe_path()
        if exe_path is None:
            return None
        shortcut_path = self.paths.bin_dir / self.SHORTCUT_NAME
        self._persist_manual_path(exe_path)
        try:
            self._create_shortcut(shortcut_path, exe_path, self._launch_arguments())
        except Exception:  # noqa: BLE001
            return None
        return shortcut_path

    def _resolve_exe_path(self) -> Path | None:
        settings = self.settings_repository.get("product_settings", {})
        manual_path = Path(str(settings.get("onec_manual_path", "")).strip()) if settings.get("onec_manual_path") else None
        if manual_path and manual_path.exists():
            return manual_path
        launcher = OneCLauncherService()
        return launcher.resolve_exe()

    def _launch_arguments(self) -> list[str]:
        launcher = OneCLauncherService()
        known_bases = launcher.list_known_bases()
        for base_name in known_bases:
            if base_name.lower() == self.base_hint.lower():
                return launcher.build_launch_arguments_for_base(base_name)
        return []

    def _create_shortcut(self, shortcut_path: Path, exe_path: Path, launch_arguments: list[str]) -> None:
        pythoncom.CoInitialize()
        try:
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.TargetPath = str(exe_path)
            shortcut.Arguments = " ".join(launch_arguments)
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.IconLocation = str(exe_path)
            shortcut.Description = "Локальный запуск 1С для SovAuto"
            shortcut.Save()
        finally:
            pythoncom.CoUninitialize()

    def _persist_manual_path(self, exe_path: Path) -> None:
        settings = self.settings_repository.get("product_settings", {})
        current_path = str(settings.get("onec_manual_path", "")).strip()
        if current_path and Path(current_path).exists():
            return
        settings["onec_manual_path"] = str(exe_path)
        settings["onec_shortcut_path"] = str(self.paths.bin_dir / self.SHORTCUT_NAME)
        self.settings_repository.set("product_settings", settings)
