from pathlib import Path

from core.launch.onec_launcher import OneCLauncherService
from core.launch.onec_profile import OneCLaunchProfile
from storage.db import DatabaseProvider
from storage.repositories.settings_repository import SettingsRepository


def test_onec_profile_roundtrip() -> None:
    profile = OneCLaunchProfile(
        exe_path=r"C:\Program Files\1cv8\common\1cv8.exe",
        profile_name="Бухгалтерия",
        launch_arguments=["/IBName", "Бухгалтерия"],
        last_base_hint="Бухгалтерия",
        last_window_title="1С:Предприятие - Бухгалтерия",
    )

    restored = OneCLaunchProfile.from_dict(profile.to_dict())

    assert restored.profile_name == "Бухгалтерия"
    assert restored.launch_arguments == ["/IBName", "Бухгалтерия"]
    assert restored.last_base_hint == "Бухгалтерия"


def test_launcher_prefers_manual_override(tmp_path: Path) -> None:
    exe_path = tmp_path / "1cv8.exe"
    exe_path.write_text("stub", encoding="utf-8")

    launcher = OneCLauncherService(str(exe_path))

    assert launcher.resolve_exe() == exe_path


def test_launcher_reads_ibases_with_bom(tmp_path: Path, monkeypatch) -> None:
    ibases_dir = tmp_path / "1C" / "1CEStart"
    ibases_dir.mkdir(parents=True)
    ibases_path = ibases_dir / "ibases.v8i"
    ibases_path.write_text("[SOVUT]\nConnect=File=\"C:/demo\"\n", encoding="utf-8-sig")
    monkeypatch.setenv("APPDATA", str(tmp_path))

    launcher = OneCLauncherService()

    assert launcher.list_known_bases() == {"SOVUT": 'File="C:/demo"'}
    assert launcher.build_launch_arguments_for_base("SOVUT") == ["/IBName", "SOVUT"]


def test_product_settings_store_profile_payload(tmp_path: Path) -> None:
    db_path = tmp_path / "settings.db"
    provider = DatabaseProvider(db_path)
    with provider.connect() as connection:
        connection.execute(
            """
            CREATE TABLE app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        connection.commit()

    repository = SettingsRepository(provider)
    profile = OneCLaunchProfile(
        exe_path=r"C:\Program Files\1cv8\common\1cv8.exe",
        profile_name="Тестовая база",
        last_base_hint="Тестовая база",
    )
    repository.set(
        "product_settings",
        {
            "profiles": [profile.to_dict()],
            "last_profile_id": profile.profile_id,
            "embed_enabled": True,
        },
    )

    stored = repository.get("product_settings")
    restored = OneCLaunchProfile.from_dict(stored["profiles"][0])

    assert stored["last_profile_id"] == profile.profile_id
    assert restored.last_base_hint == "Тестовая база"
