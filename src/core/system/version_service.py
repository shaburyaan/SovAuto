from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class VersionInfo:
    app_version: str
    config_schema_version: str
    db_schema_version: str


class VersionService:
    def __init__(self, version_file: Path | None = None) -> None:
        self._version_file = version_file

    def get_version_info(self) -> VersionInfo:
        app_version = "1.0.0"
        if self._version_file and self._version_file.exists():
            app_version = self._version_file.read_text(encoding="utf-8").strip() or app_version
        return VersionInfo(
            app_version=app_version,
            config_schema_version="1.0",
            db_schema_version="1.0",
        )

    def get_app_version(self) -> str:
        return self.get_version_info().app_version
