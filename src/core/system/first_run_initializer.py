from __future__ import annotations

from core.models.config import Config
from core.system.runtime_metadata import RuntimeMetadata, RuntimeMetadataStore
from core.system.version_service import VersionService
from storage.bootstrap import StorageBootstrap
from storage.db import DatabaseProvider
from storage.first_run_guard import FirstRunBootstrapGuard
from storage.repositories.config_repository import ConfigRepository


class FirstRunInitializer:
    def __init__(
        self,
        storage_bootstrap: StorageBootstrap,
        version_service: VersionService,
        metadata_store: RuntimeMetadataStore,
        config_repository: ConfigRepository,
        guard: FirstRunBootstrapGuard,
    ) -> None:
        self.storage_bootstrap = storage_bootstrap
        self.version_service = version_service
        self.metadata_store = metadata_store
        self.config_repository = config_repository
        self.guard = guard

    def run(self) -> None:
        self.storage_bootstrap.ensure_directories()
        self.storage_bootstrap.ensure_database()
        if self.guard.is_first_run():
            default_config = Config(name="Default Scenario")
            self.config_repository.save(default_config)
        info = self.version_service.get_version_info()
        self.metadata_store.save(
            RuntimeMetadata(
                version=info.app_version,
                config={"configSchemaVersion": info.config_schema_version},
                runtime_metadata={"dbSchemaVersion": info.db_schema_version},
            )
        )
