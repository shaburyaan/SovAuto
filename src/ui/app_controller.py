from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from core.automation.bootstrap import register_default_executors
from core.automation.window_service import WindowService
from core.contracts.app_lifecycle import AppLifecycleState
from core.contracts.event_bus import EventEnvelope, GlobalEventBus
from core.contracts.system_controller import SystemController
from core.execution.engine import ExecutionEngine
from core.execution.executor_registry import ExecutorRegistry
from core.models.config import Config
from core.player.scenario_player import ScenarioPlayer
from core.recorder.action_recorder import ActionRecorder
from core.scenario.scenario_manager import ScenarioManager
from core.system.app_paths import AppPaths
from core.system.version_service import VersionService
from hooks.hotkey_manager import HotkeyManager
from hooks.recording_session import RecordingSession
from storage.repositories.config_repository import ConfigRepository
from storage.repositories.settings_repository import SettingsRepository
from ui.i18n.strings import UiStrings
from ui.overlay.overlay_manager import OverlayManager
from ui.overlay.record_overlay import RecordOverlay
from ui.telemetry.ui_action_logger import UiActionLogger


DEFAULT_PRODUCT_SETTINGS = {
    "onec_manual_path": "",
    "onec_shortcut_path": "",
    "embed_enabled": True,
    "onboarding_completed": False,
    "profiles": [],
    "last_profile_id": None,
    "lock_mode": "soft",
    "delay_between_steps": 300,
    "retry_count": 3,
}


class AppController(QObject):
    configs_changed = pyqtSignal()
    engine_state_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    toast_requested = pyqtSignal(object)
    activity_logged = pyqtSignal(str)
    onec_state_changed = pyqtSignal(object)
    about_info_changed = pyqtSignal(str)
    onec_path_selection_requested = pyqtSignal()
    recording_state_changed = pyqtSignal(object)
    playback_state_changed = pyqtSignal(object)
    scenario_list_changed = pyqtSignal()
    record_click_pending = pyqtSignal(object)
    recording_finish_requested = pyqtSignal()

    def __init__(
        self,
        event_bus: GlobalEventBus,
        logger: logging.Logger,
        config_repository: ConfigRepository,
        settings_repository: SettingsRepository,
        system_controller: SystemController | None = None,
        paths: AppPaths | None = None,
        version_service: VersionService | None = None,
    ) -> None:
        super().__init__()
        self.event_bus = event_bus
        self.logger = logger
        self.config_repository = config_repository
        self.settings_repository = settings_repository
        self.system_controller = system_controller
        self.paths = paths
        self.version_service = version_service
        self._about_info = ""
        self.recording_session = RecordingSession()
        self.overlay_manager = OverlayManager()
        self.overlay_manager.create()
        self.record_overlay = RecordOverlay(self.overlay_manager)
        self.window_service = WindowService()
        self.hotkeys = HotkeyManager(self.stop, self.pause_resume, self.recording_session.undo_last)
        self.telemetry = UiActionLogger(event_bus, logger)
        self.scenario_manager = ScenarioManager(config_repository)
        self.recorder = ActionRecorder(self.window_service)
        self.player = ScenarioPlayer(self.window_service)
        registry = ExecutorRegistry()
        register_default_executors(registry)
        self.engine = ExecutionEngine(event_bus, logger, registry)
        self.active_onec_pid: int | None = None
        self.active_onec_hwnd: int | None = None
        self.active_onec_process_ids: list[int] = []
        self.app_window = None
        self._recording_mode = ActionRecorder.MODE_NAVIGATION
        self._recording_finish_pending = False
        self.recorder.click_captured.connect(self._on_record_click_captured)
        self.recorder.error_occurred.connect(self.error_occurred.emit)
        self.recorder.state_changed.connect(self._on_recorder_state_changed)
        self.recorder.stop_requested.connect(self._on_recorder_stop_requested)
        self.player.error_occurred.connect(self._on_player_error)
        self.player.countdown_changed.connect(self._on_player_countdown_changed)
        self.player.state_changed.connect(self._on_player_state_changed)
        self.player.step_started.connect(self._on_player_step_started)
        self.player.finished.connect(self._on_player_finished)
        self.event_bus.subscribe("APP_STATE_CHANGED", self._on_app_event)
        self.event_bus.subscribe("*", self._on_any_event)
        self._apply_player_settings()
        self._emit_about_info()

    def _on_app_event(self, envelope: EventEnvelope) -> None:
        engine_state = envelope.payload.get("engine_state")
        if engine_state:
            self.engine_state_changed.emit(str(engine_state))

    def _on_any_event(self, envelope: EventEnvelope) -> None:
        payload = ", ".join(f"{key}={value}" for key, value in envelope.payload.items())
        line = f"{envelope.event_type} | {payload}".strip()
        self.activity_logged.emit(line)

    def load_configs(self) -> list[Config]:
        return self.scenario_manager.list_scenarios()

    def save_config(self, config: Config) -> None:
        self.config_repository.save(config)
        self.telemetry.log_ui_action("save_config", {"config_id": config.id, "name": config.name})
        self.configs_changed.emit()

    def create_config(self, name: str) -> Config:
        config = Config(name=name)
        self.save_config(config)
        self.toast_requested.emit(UiStrings.TOAST_CONFIG_CREATED)
        return config

    def delete_config(self, config_id: str) -> None:
        self.scenario_manager.delete_scenario(config_id)
        self.telemetry.log_ui_action("delete_config", {"config_id": config_id})
        self.toast_requested.emit(UiStrings.TOAST_CONFIG_DELETED)
        self.configs_changed.emit()
        self.scenario_list_changed.emit()

    def run_config(self, config_id: str) -> None:
        self.play_scenario(config_id)

    def pause_resume(self) -> None:
        if self.player.is_playing():
            self.toast_requested.emit(UiStrings.TOAST_PLAYBACK_PAUSE_UNAVAILABLE)
            return
        status = self.engine.state_machine.state.status
        if str(status) == "paused":
            self.telemetry.log_ui_action("resume_execution")
            self.engine.resume()
            self.toast_requested.emit(UiStrings.ACTION_RESUME)
        else:
            self.telemetry.log_ui_action("pause_execution")
            self.engine.pause()
            self.toast_requested.emit(UiStrings.ACTION_PAUSE)

    def stop(self) -> None:
        if self.recorder.is_recording():
            self.request_finish_recording()
            return
        if self.player.is_playing():
            self.player.stop()
            self.toast_requested.emit(UiStrings.TOAST_PLAYBACK_STOPPED)
            return
        self.telemetry.log_ui_action("stop_execution")
        self.engine.stop()
        self.toast_requested.emit(UiStrings.TOAST_RUN_STOPPED)

    def shutdown(self) -> None:
        try:
            self.hotkeys.stop()
        except Exception:  # noqa: BLE001
            self.logger.warning("Hotkeys stop failed", exc_info=True)
        self.recorder.stop_recording()
        self.player.stop()
        self._clear_active_onec_runtime()
        if self.system_controller:
            self.system_controller.transition_to(AppLifecycleState.SHUTDOWN)

    def start_runtime_services(self) -> None:
        self.logger.info("Runtime services ready; global hotkeys kept disabled for product stability.")

    def load_product_settings(self) -> dict:
        stored = self.settings_repository.get("product_settings", DEFAULT_PRODUCT_SETTINGS)
        merged = dict(DEFAULT_PRODUCT_SETTINGS)
        merged.update(stored)
        return merged

    def _normalize_delay_setting(self, raw_value: object) -> float:
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            return 4.0
        if value == 300:
            return 4.0
        if value > 50:
            return max(0.5, value / 1000.0)
        return max(0.5, value)

    def _apply_player_settings(self) -> None:
        settings = self.load_product_settings()
        self.player.set_delay(self._normalize_delay_setting(settings.get("delay_between_steps", 4)))

    def save_product_settings(self, settings: dict) -> None:
        merged = dict(DEFAULT_PRODUCT_SETTINGS)
        merged.update(settings)
        self.settings_repository.set("product_settings", merged)
        self._emit_about_info()

    def get_ui_settings(self) -> dict:
        settings = self.load_product_settings()
        return {
            "onec_manual_path": settings.get("onec_manual_path", ""),
            "embed_enabled": settings.get("embed_enabled", True),
            "lock_mode": settings.get("lock_mode", "soft"),
            "delay_between_steps": int(round(self._normalize_delay_setting(settings.get("delay_between_steps", 4)))),
            "retry_count": settings.get("retry_count", 3),
            "onboarding_completed": settings.get("onboarding_completed", False),
        }

    def save_ui_settings(
        self,
        onec_manual_path: str,
        lock_mode: str,
        delay_between_steps: int,
        retry_count: int,
        embed_enabled: bool,
    ) -> None:
        settings = self.load_product_settings()
        settings.update(
            {
                "onec_manual_path": onec_manual_path.strip(),
                "lock_mode": lock_mode,
                "delay_between_steps": delay_between_steps,
                "retry_count": retry_count,
                "embed_enabled": embed_enabled,
            }
        )
        self.save_product_settings(settings)
        self._apply_player_settings()
        self.telemetry.log_ui_action("save_settings", settings)
        self.toast_requested.emit(UiStrings.TOAST_SETTINGS_SAVED)

    def should_show_onboarding(self) -> bool:
        settings = self.load_product_settings()
        return not settings.get("onboarding_completed", False)

    def mark_onboarding_completed(self, skipped: bool = False) -> None:
        settings = self.load_product_settings()
        settings["onboarding_completed"] = True
        self.save_product_settings(settings)
        self.telemetry.log_onboarding("completed", skipped=skipped)
        if skipped:
            self.toast_requested.emit(UiStrings.TOAST_ONBOARDING_SKIPPED)

    def reset_onboarding(self) -> None:
        settings = self.load_product_settings()
        settings["onboarding_completed"] = False
        self.save_product_settings(settings)
        self.telemetry.log_ui_action("reset_onboarding")

    def _emit_attached_state(
        self,
        hwnd: int,
        process_id: int,
        title: str,
        base_hint: str,
        command_line: str,
    ) -> None:
        self.onec_state_changed.emit(
            {
                "status": "attached",
                "hwnd": hwnd,
                "pid": process_id,
                "process_ids": list(self.active_onec_process_ids),
                "title": title,
                "base_hint": base_hint,
                "command_line": command_line,
                "embed_enabled": self.load_product_settings().get("embed_enabled", True),
            }
        )

    def attach_existing_onec(self) -> None:
        self._restore_existing_onec_runtime(emit_errors=True)

    def _restore_existing_onec_runtime(self, emit_errors: bool = False) -> bool:
        settings = self.load_product_settings()
        expected_exe = settings.get("onec_manual_path", "").strip() or None
        window = self.window_service.find_existing_onec_window(executable_path=expected_exe)
        if window is None:
            if emit_errors:
                self.error_occurred.emit(UiStrings.ERROR_ONEC_ATTACH_FAILED)
            return False
        if self.window_service.is_minimized(window.hwnd):
            self.window_service.restore_and_focus(window.hwnd)
            window = self.window_service.get_window_info(window.hwnd)
        self.active_onec_hwnd = window.hwnd
        self.active_onec_pid = window.process_id
        self.active_onec_process_ids = [window.process_id]
        self.telemetry.log_ui_action("attach_existing_onec", {"pid": window.process_id, "hwnd": window.hwnd})
        self.onec_state_changed.emit(
            {
                "status": "attached",
                "hwnd": window.hwnd,
                "pid": window.process_id,
                "process_ids": [window.process_id],
                "title": window.title or "1С",
                "base_hint": "Sovut",
                "command_line": "",
                "embed_enabled": settings.get("embed_enabled", True),
            }
        )
        return True

    def start_recording(self, mode: str) -> None:
        if self.recorder.is_recording():
            self.toast_requested.emit(UiStrings.toast_payload(UiStrings.ERROR_RECORDING_ALREADY_ACTIVE, kind="error"))
            return
        if self.player.is_playing():
            self.toast_requested.emit(UiStrings.toast_payload(UiStrings.ERROR_RECORDING_BLOCKED_BY_PLAYBACK, kind="error"))
            return
        if self.active_onec_hwnd is None or not self.window_service.is_window(self.active_onec_hwnd):
            self._restore_existing_onec_runtime()
        if self.active_onec_hwnd is None or not self.window_service.is_window(self.active_onec_hwnd):
            self.error_occurred.emit(UiStrings.ERROR_RECORDING_REQUIRES_ONEC)
            return
        self.recording_session.reset()
        self._recording_mode = mode
        self._recording_finish_pending = False
        if not self.recorder.start_recording(self.active_onec_hwnd, mode):
            return
        self.record_overlay.show(UiStrings.recording_mode_label(mode))
        self.toast_requested.emit(UiStrings.TOAST_RECORDING_STARTED)

    def accept_recorded_click(self, text: str = "") -> None:
        step = self.recorder.accept_pending_click(text)
        self.recording_session.append_step(step)
        screen_x, screen_y = self._to_screen_coordinates(int(step["x"]), int(step["y"]))
        self.record_overlay.trigger_marker(screen_x, screen_y)
        self.record_overlay.update_status(UiStrings.recording_mode_label(self._recording_mode))
        self.toast_requested.emit(UiStrings.TOAST_RECORDING_STEP_SAVED)

    def reject_recorded_click(self) -> None:
        self.recorder.reject_pending_click()
        self.record_overlay.update_status(UiStrings.recording_mode_label(self._recording_mode))

    def finish_recording(self, scenario_name: str) -> Config | None:
        self._recording_finish_pending = False
        steps = self.recording_session.steps()
        self.recorder.stop_recording()
        self.record_overlay.hide()
        if not steps:
            self.toast_requested.emit(UiStrings.toast_payload(UiStrings.TOAST_RECORDING_EMPTY, kind="error"))
            return None
        try:
            scenario = self.scenario_manager.save_scenario(scenario_name, steps)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Scenario save failed")
            self.toast_requested.emit(UiStrings.toast_payload(UiStrings.save_error_label(str(exc)), kind="error", timeout_ms=4200))
            return None
        self.telemetry.log_ui_action("save_recorded_scenario", {"config_id": scenario.id, "steps": len(steps)})
        self.toast_requested.emit(UiStrings.toast_payload(UiStrings.TOAST_SCENARIO_SAVED_OK, kind="success"))
        self.configs_changed.emit()
        self.scenario_list_changed.emit()
        return scenario

    def cancel_recording(self) -> None:
        self._recording_finish_pending = False
        self.recording_session.reset()
        self.recorder.stop_recording()
        self.record_overlay.hide()
        self.toast_requested.emit(UiStrings.toast_payload(UiStrings.TOAST_RECORDING_CANCELLED, kind="error"))

    def is_recording(self) -> bool:
        return self.recorder.is_recording()

    def current_recording_mode(self) -> str:
        return self._recording_mode

    def is_recording_finish_pending(self) -> bool:
        return self._recording_finish_pending

    def cancel_finish_recording(self) -> None:
        self._recording_finish_pending = False

    def switch_recording_mode(self, mode: str) -> None:
        if not self.recorder.is_recording():
            return
        self._recording_mode = mode
        self.recorder.set_mode(mode)
        self.record_overlay.update_status(UiStrings.recording_mode_label(mode))
        self.toast_requested.emit(UiStrings.recording_mode_label(mode))

    def play_scenario(self, config_id: str) -> None:
        if self.recorder.is_recording():
            self.toast_requested.emit(UiStrings.toast_payload(UiStrings.ERROR_PLAYBACK_BLOCKED_BY_RECORDING, kind="error"))
            return
        scenario = self.scenario_manager.load_scenario(config_id)
        if scenario is None:
            self.error_occurred.emit(UiStrings.ERROR_CONFIG_NOT_FOUND)
            return
        self._apply_player_settings()
        if self.active_onec_hwnd is None or not self.window_service.is_window(self.active_onec_hwnd):
            self._restore_existing_onec_runtime()
        if self.active_onec_hwnd is None or not self.window_service.is_window(self.active_onec_hwnd):
            self.error_occurred.emit(UiStrings.ERROR_PLAYBACK_REQUIRES_ONEC)
            return
        self._ensure_work_area_active()
        if self.system_controller:
            self.system_controller.transition_to(AppLifecycleState.RUNNING)
        self.telemetry.log_ui_action("play_scenario", {"config_id": scenario.id, "steps": len(scenario.steps)})
        self.toast_requested.emit(UiStrings.TOAST_RUN_STARTED)
        self.player.play(self.active_onec_hwnd, scenario.steps, scenario.settings.countdownSeconds)

    def get_scenario(self, config_id: str) -> Config | None:
        return self.scenario_manager.load_scenario(config_id)

    def register_embed_attempt(self, attempt: int, success: bool, reason: str = "") -> None:
        self.telemetry.log_onec_event(
            "embed_attempt",
            {
                "attempt": attempt,
                "success": success,
                "reason": reason,
                "pid": self.active_onec_pid,
                "hwnd": self.active_onec_hwnd,
            },
        )

    def register_fallback(self, reason: str) -> None:
        self.telemetry.log_onec_event(
            "embed_fallback",
            {
                "pid": self.active_onec_pid,
                "hwnd": self.active_onec_hwnd,
                "reason": reason,
            },
        )

    def _clear_active_onec_runtime(self) -> None:
        self.active_onec_pid = None
        self.active_onec_hwnd = None
        self.active_onec_process_ids = []

    def _on_record_click_captured(self, x: int, y: int, mode: str) -> None:
        self.record_overlay.update_status(UiStrings.TOAST_RECORDING_CONFIRM)
        self.record_click_pending.emit({"x": x, "y": y, "mode": mode})

    def _on_recorder_state_changed(self, is_recording: bool, mode: str) -> None:
        self.recording_state_changed.emit({"recording": is_recording, "mode": mode})

    def _on_recorder_stop_requested(self) -> None:
        self.request_finish_recording()

    def _on_player_countdown_changed(self, seconds: int) -> None:
        self.overlay_manager.show(
            UiStrings.TOAST_PLAYBACK_RUNNING,
            click_through=True,
            presentation="countdown",
            secondary_text=UiStrings.countdown_label(seconds),
        )
        self.playback_state_changed.emit({"status": "countdown", "seconds": seconds})

    def _on_player_state_changed(self, status: str) -> None:
        if status == "running":
            self.overlay_manager.show(UiStrings.TOAST_PLAYBACK_RUNNING, click_through=True, presentation="playback")
        elif status == "completed":
            self.overlay_manager.show(
                UiStrings.TOAST_PLAYBACK_COMPLETED,
                click_through=True,
                presentation="completion",
                secondary_text="✓",
            )
        self.playback_state_changed.emit({"status": status})

    def _on_player_step_started(self, index: int, step: Any) -> None:
        try:
            x, y = self._to_screen_coordinates(int(step["x"]), int(step["y"]))
            self.record_overlay.show_click_indicator(x, y)
        except Exception:  # noqa: BLE001
            pass

    def _on_player_finished(self) -> None:
        self.overlay_manager.clear_ripple()
        self.overlay_manager.hide()
        if self.system_controller:
            self.system_controller.transition_to(AppLifecycleState.READY)
        self.playback_state_changed.emit({"status": "finished"})

    def _on_player_error(self, text: str) -> None:
        self.overlay_manager.clear_ripple()
        self.overlay_manager.hide()
        if self.system_controller:
            self.system_controller.transition_to(AppLifecycleState.READY)
        self.error_occurred.emit(text)

    def request_finish_recording(self) -> None:
        if self._recording_finish_pending or not self.recorder.is_recording():
            return
        self._recording_finish_pending = True
        self.recorder.stop_recording()
        self.record_overlay.hide()
        self.recording_finish_requested.emit()

    def _to_screen_coordinates(self, rel_x: int, rel_y: int) -> tuple[int, int]:
        if self.active_onec_hwnd is None:
            return rel_x, rel_y
        left, top, _, _ = self.window_service.get_window_info(self.active_onec_hwnd).bounds
        return left + rel_x, top + rel_y

    def _ensure_work_area_active(self) -> None:
        if self.app_window is not None and hasattr(self.app_window, "show_home_page"):
            self.app_window.show_home_page()

    def _emit_about_info(self) -> None:
        version = self.version_service.get_app_version() if self.version_service else "1.0.0"
        info_lines = [f"{UiStrings.ABOUT_VERSION}: {version}"]
        if self.paths is not None:
            info_lines.extend(
                [
                    "",
                    f"{UiStrings.ABOUT_RUNTIME}:",
                    f"  Бинарии: {self.paths.bin_dir}",
                    f"  Конфиги: {self.paths.configs_dir}",
                    f"  Логи: {self.paths.logs_dir}",
                    f"  База данных: {self.paths.db_path}",
                ]
            )
        self._about_info = "\n".join(info_lines)
        self.about_info_changed.emit(self._about_info)

    def get_about_info(self) -> str:
        return self._about_info
