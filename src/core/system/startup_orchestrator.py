from __future__ import annotations

import logging
from pathlib import Path
import sys
import threading

from PyQt6.QtCore import QTimer

from core.contracts.app_lifecycle import AppLifecycleState
from core.contracts.event_bus import GlobalEventBus
from core.contracts.splash_barrier import SplashLockBarrier
from core.contracts.system_controller import SystemController
from core.launch.onec_shortcut_service import OneCShortcutService
from core.system.app_paths import AppPaths
from core.system.first_run_initializer import FirstRunInitializer
from core.system.runtime_context import RuntimeContext
from core.system.runtime_metadata import RuntimeMetadataStore
from core.system.version_service import VersionService
from storage.bootstrap import StorageBootstrap
from storage.db import DatabaseProvider
from storage.first_run_guard import FirstRunBootstrapGuard
from storage.repositories.config_repository import ConfigRepository
from storage.repositories.settings_repository import SettingsRepository
from ui.app_controller import AppController
from ui.app_preloader import AppPreloader
from ui.splash.splash_controller import SplashController
from ui.splash.splash_screen import SplashScreen
from utils.logger import LoggerFactory


class StartupOrchestrator:
    def __init__(self, app) -> None:
        self.app = app
        self.runtime_context = RuntimeContext.detect()
        self.paths = AppPaths(self.runtime_context)
        self.event_bus = GlobalEventBus()
        self.system_controller = SystemController(self.event_bus)
        self.logger = LoggerFactory.create_app_logger(self.paths.log_path)
        self._install_global_exception_hooks()
        self.version_service = VersionService(Path("build/version/version.txt"))
        self.storage_bootstrap = StorageBootstrap(self.paths)
        self.storage_bootstrap.ensure_directories()
        self.storage_bootstrap.ensure_database()
        self.provider = DatabaseProvider(self.paths.db_path)
        self.config_repository = ConfigRepository(self.provider, self.paths.configs_dir)
        self.settings_repository = SettingsRepository(self.provider)
        self.metadata_store = RuntimeMetadataStore(self.paths.runtime_metadata_path)
        self.onec_shortcut_service = OneCShortcutService(self.paths, self.settings_repository)
        self.first_run_initializer = FirstRunInitializer(
            self.storage_bootstrap,
            self.version_service,
            self.metadata_store,
            self.config_repository,
            FirstRunBootstrapGuard(self.paths),
        )
        self.controller = AppController(
            self.event_bus,
            self.logger,
            self.config_repository,
            self.settings_repository,
            self.system_controller,
            self.paths,
            self.version_service,
        )
        self.barrier = SplashLockBarrier.create()
        self.preloader = AppPreloader(self.controller)
        self.splash = SplashScreen()
        self.splash_controller = SplashController(self.barrier, self.splash, self.preloader.preload())

    def start(self) -> None:
        self.logger.info("SovAuto startup initiated")
        self.app.aboutToQuit.connect(lambda: self.logger.info("Qt aboutToQuit emitted"))
        self.system_controller.transition_to(AppLifecycleState.BOOTSTRAP)
        self.splash_controller.start()
        self.system_controller.transition_to(AppLifecycleState.SPLASH)
        QTimer.singleShot(10000, lambda: self.barrier.mark_min_duration_elapsed())
        QTimer.singleShot(50, lambda: self._bootstrap_runtime())
        self.splash_controller.finish_when_ready()

    def _bootstrap_runtime(self) -> None:
        try:
            self.first_run_initializer.run()
            shortcut_path = self.onec_shortcut_service.ensure_local_shortcut()
            if shortcut_path is not None:
                self.logger.info("1C shortcut ensured at %s", shortcut_path)
            self.logger.info("Bootstrap complete")
            self.barrier.mark_bootstrap_complete()
            self.system_controller.transition_to(AppLifecycleState.READY)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Bootstrap failed")
            self.barrier.mark_fallback()

    def _install_global_exception_hooks(self) -> None:
        def _log_exception(exc_type, exc_value, exc_traceback) -> None:
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            self.logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        def _thread_exception(args: threading.ExceptHookArgs) -> None:
            self.logger.critical(
                "Uncaught thread exception",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
            )

        sys.excepthook = _log_exception
        threading.excepthook = _thread_exception
