from __future__ import annotations

from pathlib import Path

from core.system.app_paths import AppPaths, PathBootstrap
from storage.db import DatabaseProvider


class StorageBootstrap:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def ensure_directories(self) -> None:
        PathBootstrap(self.paths).ensure()

    def ensure_database(self) -> None:
        provider = DatabaseProvider(self.paths.db_path)
        with provider.connect() as connection:
            migrations_dir = Path(__file__).parent / "migrations"
            for sql_file in sorted(migrations_dir.glob("*.sql")):
                connection.executescript(sql_file.read_text(encoding="utf-8"))
            connection.commit()
