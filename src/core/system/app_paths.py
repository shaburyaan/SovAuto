from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from core.system.runtime_context import RuntimeContext


@dataclass(slots=True, frozen=True)
class AppPaths:
    runtime_context: RuntimeContext
    app_name: str = "SovAuto"

    @property
    def roaming_dir(self) -> Path:
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / self.app_name

    @property
    def bin_dir(self) -> Path:
        return self.runtime_context.root_dir

    @property
    def data_dir(self) -> Path:
        return self.roaming_dir / "data"

    @property
    def logs_dir(self) -> Path:
        return self.roaming_dir / "logs"

    @property
    def configs_dir(self) -> Path:
        return self.roaming_dir / "configs"

    @property
    def cache_dir(self) -> Path:
        return self.roaming_dir / "cache"

    @property
    def backups_dir(self) -> Path:
        return self.roaming_dir / "backups"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    @property
    def runtime_metadata_path(self) -> Path:
        return self.roaming_dir / "runtime_metadata.json"

    @property
    def log_path(self) -> Path:
        return self.logs_dir / "app.log"

    def all_dirs(self) -> list[Path]:
        return [
            self.roaming_dir,
            self.data_dir,
            self.logs_dir,
            self.configs_dir,
            self.cache_dir,
            self.backups_dir,
        ]


class PathBootstrap:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def ensure(self) -> None:
        for directory in self.paths.all_dirs():
            directory.mkdir(parents=True, exist_ok=True)
