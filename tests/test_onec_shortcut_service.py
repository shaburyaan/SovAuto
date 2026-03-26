from __future__ import annotations

from pathlib import Path

from core.launch.onec_shortcut_service import OneCShortcutService
from core.system.app_paths import AppPaths
from core.system.runtime_context import RuntimeContext


class _FakeSettingsRepository:
    def __init__(self, initial: dict | None = None) -> None:
        self.payload = initial or {}

    def get(self, key: str, default: dict | None = None) -> dict:
        return dict(self.payload.get(key, default or {}))

    def set(self, key: str, value: dict) -> None:
        self.payload[key] = dict(value)


def test_ensure_local_shortcut_creates_link_and_persists_detected_manual_path(monkeypatch, tmp_path) -> None:
    settings_repository = _FakeSettingsRepository()
    paths = AppPaths(RuntimeContext(root_dir=tmp_path, is_packaged=False))
    created: list[tuple[Path, Path, list[str]]] = []
    resolved_exe = tmp_path / "1cv8.exe"
    resolved_exe.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "core.launch.onec_shortcut_service.OneCLauncherService.resolve_exe",
        lambda self: resolved_exe,
    )
    monkeypatch.setattr(
        "core.launch.onec_shortcut_service.OneCLauncherService.list_known_bases",
        lambda self: {"SOVUT": "Connect=..."},
    )
    monkeypatch.setattr(
        "core.launch.onec_shortcut_service.OneCLauncherService.build_launch_arguments_for_base",
        lambda self, base_name: ["/IBName", base_name],
    )

    service = OneCShortcutService(paths, settings_repository)
    monkeypatch.setattr(
        service,
        "_create_shortcut",
        lambda shortcut_path, exe_path, launch_arguments: created.append((shortcut_path, exe_path, launch_arguments)),
    )

    shortcut = service.ensure_local_shortcut()

    assert shortcut == tmp_path / "SovAuto 1C.lnk"
    assert created == [(tmp_path / "SovAuto 1C.lnk", resolved_exe, ["/IBName", "SOVUT"])]
    assert settings_repository.payload["product_settings"]["onec_manual_path"] == str(resolved_exe)
    assert settings_repository.payload["product_settings"]["onec_shortcut_path"] == str(tmp_path / "SovAuto 1C.lnk")


def test_ensure_local_shortcut_respects_existing_manual_path(monkeypatch, tmp_path) -> None:
    manual_exe = tmp_path / "manual-1cv8.exe"
    manual_exe.write_text("", encoding="utf-8")
    settings_repository = _FakeSettingsRepository({"product_settings": {"onec_manual_path": str(manual_exe)}})
    paths = AppPaths(RuntimeContext(root_dir=tmp_path, is_packaged=False))
    created: list[tuple[Path, Path, list[str]]] = []

    monkeypatch.setattr(
        "core.launch.onec_shortcut_service.OneCLauncherService.resolve_exe",
        lambda self: None,
    )
    monkeypatch.setattr(
        "core.launch.onec_shortcut_service.OneCLauncherService.list_known_bases",
        lambda self: {},
    )

    service = OneCShortcutService(paths, settings_repository)
    monkeypatch.setattr(
        service,
        "_create_shortcut",
        lambda shortcut_path, exe_path, launch_arguments: created.append((shortcut_path, exe_path, launch_arguments)),
    )

    shortcut = service.ensure_local_shortcut()

    assert shortcut == tmp_path / "SovAuto 1C.lnk"
    assert created == [(tmp_path / "SovAuto 1C.lnk", manual_exe, [])]
    assert settings_repository.payload["product_settings"]["onec_manual_path"] == str(manual_exe)
