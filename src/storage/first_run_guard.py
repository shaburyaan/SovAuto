from __future__ import annotations

from pathlib import Path

from core.system.app_paths import AppPaths


class FirstRunBootstrapGuard:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def is_first_run(self) -> bool:
        return not self.paths.runtime_metadata_path.exists()

    def validate_runtime_environment(self) -> bool:
        return all(directory.exists() for directory in self.paths.all_dirs())

    def binaries_look_intact(self) -> bool:
        return Path(self.paths.bin_dir).exists()
