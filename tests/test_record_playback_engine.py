from __future__ import annotations

import logging

from core.contracts.event_bus import GlobalEventBus
from core.automation.window_service import WindowInfo
from core.models.config import Config
from core.player.scenario_player import ScenarioPlayer
from core.recorder.action_recorder import ActionRecorder
from core.scenario.scenario_manager import ScenarioManager
from ui.app_controller import AppController
from ui.i18n.strings import UiStrings


def _window(hwnd: int = 100) -> WindowInfo:
    return WindowInfo(
        hwnd=hwnd,
        title="Управление торговлей, редакция 11",
        class_name="V8TopLevelFrameSDI",
        process_name="1cv8.exe",
        process_id=500,
        bounds=(100, 200, 900, 700),
        visible=True,
        parent_hwnd=0,
        owner_hwnd=0,
        style=0,
    )


class _DummyListener:
    def __init__(self, on_click) -> None:
        self.on_click = on_click
        self.stopped = False

    def start(self) -> None:
        return None

    def stop(self) -> None:
        self.stopped = True
        return None


class _DummyKeyboardListener:
    def __init__(self, on_press=None, on_release=None) -> None:
        self.on_press = on_press
        self.on_release = on_release
        self.stopped = False

    def start(self) -> None:
        return None

    def stop(self) -> None:
        self.stopped = True
        return None


class _FakeSettingsRepository:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def get(self, key: str, default=None):
        return self.values.get(key, default)

    def set(self, key: str, value) -> None:
        self.values[key] = value


class _FakeHotkeyManager:
    def __init__(self, *args, **kwargs) -> None:
        return None

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


def _make_controller(monkeypatch) -> AppController:
    monkeypatch.setattr("ui.app_controller.OverlayManager.create", lambda self: None)
    monkeypatch.setattr("ui.app_controller.HotkeyManager", _FakeHotkeyManager)
    return AppController(
        event_bus=GlobalEventBus(),
        logger=logging.getLogger("test-controller"),
        config_repository=_FakeRepo(),
        settings_repository=_FakeSettingsRepository(),
    )


class _FakeRepo:
    def __init__(self, items: list[Config] | None = None) -> None:
        self.items = {item.id: item for item in items or []}

    def get_all(self) -> list[Config]:
        return list(self.items.values())

    def get(self, config_id: str) -> Config | None:
        return self.items.get(config_id)

    def save(self, config: Config) -> None:
        self.items[config.id] = config

    def delete(self, config_id: str) -> None:
        self.items.pop(config_id, None)


def test_action_recorder_converts_screen_to_relative(monkeypatch) -> None:
    recorder = ActionRecorder()
    captured: list[tuple[int, int, str]] = []
    recorder.click_captured.connect(lambda x, y, mode: captured.append((x, y, mode)))
    monkeypatch.setattr("core.recorder.action_recorder.mouse.Listener", _DummyListener)
    monkeypatch.setattr("core.recorder.action_recorder.keyboard.Listener", _DummyKeyboardListener)
    monkeypatch.setattr(recorder.window_service, "is_window", lambda hwnd: hwnd == 100)
    monkeypatch.setattr(recorder.window_service, "get_window_info", lambda hwnd: _window(hwnd))

    assert recorder.start_recording(100, ActionRecorder.MODE_NAVIGATION) is True

    recorder.on_mouse_click(150, 260)

    assert captured == [(50, 60, ActionRecorder.MODE_NAVIGATION)]
    step = recorder.accept_pending_click()
    assert step["type"] == "click"
    assert step["x"] == 50
    assert step["y"] == 60


def test_action_recorder_ignores_left_and_right_clicks(monkeypatch) -> None:
    recorder = ActionRecorder()
    captured: list[tuple[int, int, str]] = []
    recorder.click_captured.connect(lambda x, y, mode: captured.append((x, y, mode)))
    monkeypatch.setattr("core.recorder.action_recorder.mouse.Listener", _DummyListener)
    monkeypatch.setattr("core.recorder.action_recorder.keyboard.Listener", _DummyKeyboardListener)
    monkeypatch.setattr(recorder.window_service, "is_window", lambda hwnd: hwnd == 100)

    assert recorder.start_recording(100, ActionRecorder.MODE_NAVIGATION) is True

    recorder._on_listener_click(150, 260, None, True)

    assert captured == []


def test_action_recorder_ignores_click_outside_embedded_window(monkeypatch) -> None:
    recorder = ActionRecorder()
    captured: list[tuple[int, int, str]] = []
    recorder.click_captured.connect(lambda x, y, mode: captured.append((x, y, mode)))
    monkeypatch.setattr("core.recorder.action_recorder.mouse.Listener", _DummyListener)
    monkeypatch.setattr("core.recorder.action_recorder.keyboard.Listener", _DummyKeyboardListener)
    monkeypatch.setattr(recorder.window_service, "is_window", lambda hwnd: hwnd == 100)
    monkeypatch.setattr(recorder.window_service, "get_window_info", lambda hwnd: _window(hwnd))

    recorder.start_recording(100, ActionRecorder.MODE_INPUT)
    recorder.on_mouse_click(99, 260)

    assert captured == []


def test_action_recorder_alt_creates_pending_capture(monkeypatch) -> None:
    from pynput import keyboard

    recorder = ActionRecorder()
    captured: list[tuple[int, int, str]] = []
    recorder.click_captured.connect(lambda x, y, mode: captured.append((x, y, mode)))
    monkeypatch.setattr("core.recorder.action_recorder.mouse.Listener", _DummyListener)
    monkeypatch.setattr("core.recorder.action_recorder.keyboard.Listener", _DummyKeyboardListener)
    monkeypatch.setattr("core.recorder.action_recorder.win32api.GetCursorPos", lambda: (150, 260))
    monkeypatch.setattr(recorder.window_service, "is_window", lambda hwnd: hwnd == 100)
    monkeypatch.setattr(recorder.window_service, "get_window_info", lambda hwnd: _window(hwnd))

    assert recorder.start_recording(100, ActionRecorder.MODE_NAVIGATION) is True

    recorder._on_listener_key_press(keyboard.Key.alt_l)

    assert captured == [(50, 60, ActionRecorder.MODE_NAVIGATION)]


def test_action_recorder_alt_is_debounced_until_release(monkeypatch) -> None:
    from pynput import keyboard

    recorder = ActionRecorder()
    captured: list[tuple[int, int, str]] = []
    recorder.click_captured.connect(lambda x, y, mode: captured.append((x, y, mode)))
    monkeypatch.setattr("core.recorder.action_recorder.mouse.Listener", _DummyListener)
    monkeypatch.setattr("core.recorder.action_recorder.keyboard.Listener", _DummyKeyboardListener)
    monkeypatch.setattr("core.recorder.action_recorder.win32api.GetCursorPos", lambda: (150, 260))
    monkeypatch.setattr(recorder.window_service, "is_window", lambda hwnd: hwnd == 100)
    monkeypatch.setattr(recorder.window_service, "get_window_info", lambda hwnd: _window(hwnd))

    assert recorder.start_recording(100, ActionRecorder.MODE_NAVIGATION) is True

    recorder._on_listener_key_press(keyboard.Key.alt_l)
    recorder.reject_pending_click()
    recorder._on_listener_key_press(keyboard.Key.alt_l)
    recorder._on_listener_key_release(keyboard.Key.alt_l)
    recorder._on_listener_key_press(keyboard.Key.alt_l)

    assert captured == [
        (50, 60, ActionRecorder.MODE_NAVIGATION),
        (50, 60, ActionRecorder.MODE_NAVIGATION),
    ]


def test_action_recorder_emits_stop_requested_for_esc_and_f8(monkeypatch) -> None:
    from pynput import keyboard

    recorder = ActionRecorder()
    requests: list[str] = []
    monkeypatch.setattr("core.recorder.action_recorder.mouse.Listener", _DummyListener)
    monkeypatch.setattr("core.recorder.action_recorder.keyboard.Listener", _DummyKeyboardListener)
    monkeypatch.setattr(recorder.window_service, "is_window", lambda hwnd: hwnd == 100)
    recorder.stop_requested.connect(lambda: requests.append("stop"))

    assert recorder.start_recording(100, ActionRecorder.MODE_NAVIGATION) is True

    recorder._on_listener_key_press(keyboard.Key.f8)
    recorder._on_listener_key_press(keyboard.Key.esc)

    assert requests == ["stop"]


def test_action_recorder_stop_recording_stops_mouse_and_keyboard(monkeypatch) -> None:
    recorder = ActionRecorder()
    mouse_listeners: list[_DummyListener] = []
    keyboard_listeners: list[_DummyKeyboardListener] = []

    def _make_mouse_listener(on_click):
        listener = _DummyListener(on_click)
        mouse_listeners.append(listener)
        return listener

    def _make_keyboard_listener(on_press=None, on_release=None):
        listener = _DummyKeyboardListener(on_press, on_release)
        keyboard_listeners.append(listener)
        return listener

    monkeypatch.setattr("core.recorder.action_recorder.mouse.Listener", _make_mouse_listener)
    monkeypatch.setattr("core.recorder.action_recorder.keyboard.Listener", _make_keyboard_listener)
    monkeypatch.setattr(recorder.window_service, "is_window", lambda hwnd: hwnd == 100)

    assert recorder.start_recording(100, ActionRecorder.MODE_NAVIGATION) is True

    recorder.stop_recording()

    assert mouse_listeners[0].stopped is True
    assert keyboard_listeners[0].stopped is True


def test_scenario_manager_filters_non_record_steps() -> None:
    recorded = Config(name="recorded", steps=[{"id": "1", "type": "click", "x": 1, "y": 2}])
    legacy = Config(
        name="legacy",
        steps=[{"id": "2", "type": "click", "window": {"process_name": "1cv8.exe"}, "target": {"x": 1, "y": 2}}],
    )
    manager = ScenarioManager(_FakeRepo([recorded, legacy]))

    scenarios = manager.list_scenarios()

    assert [item.name for item in scenarios] == ["recorded"]


def test_scenario_manager_rejects_empty_name() -> None:
    manager = ScenarioManager(_FakeRepo())

    try:
        manager.save_scenario("   ", [{"type": "click", "x": 1, "y": 2}])
    except ValueError as exc:
        assert str(exc) == "Имя сценария обязательно"
        return

    raise AssertionError("Expected ValueError for empty name")


def test_scenario_player_remaps_relative_coordinates(monkeypatch) -> None:
    player = ScenarioPlayer()
    window = _window(200)
    mouse_positions: list[tuple[int, int]] = []
    keyboard_inputs: list[str] = []
    activated: list[int] = []
    sleeps: list[float] = []
    previews: list[tuple[int, object]] = []
    player.step_started.connect(lambda index, step: previews.append((index, step)))
    monkeypatch.setattr(player.window_service, "is_window", lambda hwnd: hwnd == 200)
    monkeypatch.setattr(player.window_service, "get_window_info", lambda hwnd: window)
    monkeypatch.setattr(player.window_service, "activate_window", lambda hwnd: activated.append(hwnd))
    monkeypatch.setattr("core.player.scenario_player.time.sleep", lambda seconds: sleeps.append(seconds))
    monkeypatch.setattr("core.player.scenario_player.win32gui.GetWindowRect", lambda hwnd: window.bounds)
    monkeypatch.setattr("core.player.scenario_player.win32api.SetCursorPos", lambda pos: mouse_positions.append(pos))
    monkeypatch.setattr("core.player.scenario_player.win32api.mouse_event", lambda *args: None)
    monkeypatch.setattr(player.keyboard, "type", lambda text: keyboard_inputs.append(text))

    player.play(200, [{"type": "input", "x": 10, "y": 20, "text": "abc"}], countdown_seconds=0)
    player._play_next_step()
    assert mouse_positions == []
    assert previews == [(0, {"type": "input", "x": 10, "y": 20, "text": "abc"})]
    monkeypatch.setattr("core.player.scenario_player.QTimer.singleShot", lambda ms, fn: fn())
    player._execute_pending_step()

    assert mouse_positions == [(110, 220)]
    assert keyboard_inputs == ["abc"]
    assert activated == [200, 200]
    assert sleeps == [0.5, 0.05, 0.03]


def test_scenario_player_refuses_dead_window() -> None:
    player = ScenarioPlayer()
    errors: list[str] = []
    player.error_occurred.connect(errors.append)

    assert player.play(999, [{"type": "click", "x": 1, "y": 1}], countdown_seconds=0) is False
    assert errors == ["Окно 1С недоступно для воспроизведения."]


def test_scenario_player_emits_completed_before_finish(monkeypatch) -> None:
    player = ScenarioPlayer()
    states: list[str] = []
    finished: list[str] = []
    player.state_changed.connect(states.append)
    player.finished.connect(lambda: finished.append("done"))
    monkeypatch.setattr(player.window_service, "is_window", lambda hwnd: hwnd == 200)
    monkeypatch.setattr(player.window_service, "get_window_info", lambda hwnd: _window(200))
    monkeypatch.setattr(player.window_service, "activate_window", lambda hwnd: None)
    monkeypatch.setattr("core.player.scenario_player.time.sleep", lambda seconds: None)
    monkeypatch.setattr("core.player.scenario_player.win32gui.GetWindowRect", lambda hwnd: _window(200).bounds)
    monkeypatch.setattr("core.player.scenario_player.win32api.SetCursorPos", lambda pos: None)
    monkeypatch.setattr("core.player.scenario_player.win32api.mouse_event", lambda *args: None)
    monkeypatch.setattr("core.player.scenario_player.QTimer.singleShot", lambda ms, fn: fn())
    monkeypatch.setattr(player._completion_timer, "start", lambda ms: player._finish_completed_playback())

    assert player.play(200, [{"type": "click", "x": 1, "y": 1}], countdown_seconds=0) is True

    player._play_next_step()
    player._execute_pending_step()
    player._play_next_step()

    assert "completed" in states
    assert finished == ["done"]


def test_scenario_player_rejects_invalid_window_size(monkeypatch) -> None:
    player = ScenarioPlayer()
    monkeypatch.setattr(player.window_service, "activate_window", lambda hwnd: None)
    monkeypatch.setattr(player.window_service, "is_window", lambda hwnd: True)
    monkeypatch.setattr("core.player.scenario_player.time.sleep", lambda seconds: None)
    monkeypatch.setattr("core.player.scenario_player.win32gui.GetWindowRect", lambda hwnd: (100, 200, 250, 320))
    player._hwnd = 200

    try:
        player._execute_step({"type": "click", "x": 10, "y": 20})
    except RuntimeError as exc:
        assert str(exc) == "Invalid window size"
        return

    raise AssertionError("Expected RuntimeError for invalid window size")


def test_scenario_player_rejects_step_outside_target_window(monkeypatch) -> None:
    player = ScenarioPlayer()
    monkeypatch.setattr(player.window_service, "activate_window", lambda hwnd: None)
    monkeypatch.setattr(player.window_service, "is_window", lambda hwnd: True)
    monkeypatch.setattr("core.player.scenario_player.time.sleep", lambda seconds: None)
    monkeypatch.setattr("core.player.scenario_player.win32gui.GetWindowRect", lambda hwnd: (100, 200, 500, 600))
    player._hwnd = 200

    try:
        player._execute_step({"type": "click", "x": 450, "y": 20})
    except RuntimeError as exc:
        assert str(exc) == "Step outside target window"
        return

    raise AssertionError("Expected RuntimeError for step outside window")


def test_scenario_player_uses_slow_step_delay(monkeypatch) -> None:
    player = ScenarioPlayer()
    scheduled: list[int] = []
    player.set_delay(4)
    player._hwnd = 200
    player._pending_step = {"type": "click", "x": 10, "y": 20}
    monkeypatch.setattr(player.window_service, "activate_window", lambda hwnd: None)
    monkeypatch.setattr(player.window_service, "is_window", lambda hwnd: True)
    monkeypatch.setattr("core.player.scenario_player.time.sleep", lambda seconds: None)
    monkeypatch.setattr("core.player.scenario_player.win32gui.GetWindowRect", lambda hwnd: (100, 200, 900, 700))
    monkeypatch.setattr("core.player.scenario_player.win32api.SetCursorPos", lambda pos: None)
    monkeypatch.setattr("core.player.scenario_player.win32api.mouse_event", lambda *args: None)
    monkeypatch.setattr("core.player.scenario_player.QTimer.singleShot", lambda ms, fn: scheduled.append(ms))

    player._execute_pending_step()

    assert scheduled == [4000]


def test_controller_blocks_playback_while_recording(monkeypatch) -> None:
    controller = _make_controller(monkeypatch)
    payloads: list[object] = []
    controller.toast_requested.connect(payloads.append)
    monkeypatch.setattr(controller.recorder, "is_recording", lambda: True)

    controller.play_scenario("missing")

    assert payloads == [UiStrings.toast_payload(UiStrings.ERROR_PLAYBACK_BLOCKED_BY_RECORDING, kind="error")]


def test_controller_blocks_duplicate_recording_start(monkeypatch) -> None:
    controller = _make_controller(monkeypatch)
    payloads: list[object] = []
    controller.toast_requested.connect(payloads.append)
    monkeypatch.setattr(controller.recorder, "is_recording", lambda: True)

    controller.start_recording(ActionRecorder.MODE_NAVIGATION)

    assert payloads == [UiStrings.toast_payload(UiStrings.ERROR_RECORDING_ALREADY_ACTIVE, kind="error")]


def test_controller_finish_recording_emits_success_toast(monkeypatch) -> None:
    controller = _make_controller(monkeypatch)
    payloads: list[object] = []
    controller.toast_requested.connect(payloads.append)
    monkeypatch.setattr(controller.recorder, "stop_recording", lambda: None)
    monkeypatch.setattr(controller.record_overlay, "hide", lambda: None)
    controller.recording_session.append_step({"id": "1", "type": "click", "x": 10, "y": 20})

    scenario = controller.finish_recording("Smoke")

    assert scenario is not None
    assert scenario.name == "Smoke"
    assert payloads[-1] == UiStrings.toast_payload(UiStrings.TOAST_SCENARIO_SAVED_OK, kind="success")


def test_controller_finish_recording_emits_error_toast_on_save_failure(monkeypatch) -> None:
    controller = _make_controller(monkeypatch)
    payloads: list[object] = []
    controller.toast_requested.connect(payloads.append)
    monkeypatch.setattr(controller.recorder, "stop_recording", lambda: None)
    monkeypatch.setattr(controller.record_overlay, "hide", lambda: None)
    monkeypatch.setattr(
        controller.scenario_manager,
        "save_scenario",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("disk full")),
    )
    controller.recording_session.append_step({"id": "1", "type": "click", "x": 10, "y": 20})

    scenario = controller.finish_recording("Smoke")

    assert scenario is None
    assert payloads[-1] == UiStrings.toast_payload("Произошла ошибка: disk full", kind="error", timeout_ms=4200)


def test_controller_playback_returns_to_home_page(monkeypatch) -> None:
    controller = _make_controller(monkeypatch)
    controller.active_onec_hwnd = 200
    controller.app_window = type("WindowStub", (), {"show_home_page": lambda self: calls.append("home")})()
    scenario = Config(name="Recorded", steps=[{"type": "click", "x": 10, "y": 20}])
    scenario.settings.countdownSeconds = 0
    calls: list[str] = []
    monkeypatch.setattr(controller.recorder, "is_recording", lambda: False)
    monkeypatch.setattr(controller.window_service, "is_window", lambda hwnd: hwnd == 200)
    monkeypatch.setattr(controller.scenario_manager, "load_scenario", lambda config_id: scenario)
    monkeypatch.setattr(controller.player, "play", lambda hwnd, steps, countdown: calls.append(f"play:{hwnd}:{countdown}"))

    controller.play_scenario("cfg-1")

    assert calls == ["home", "play:200:0"]


def test_controller_normalizes_legacy_delay_setting(monkeypatch) -> None:
    controller = _make_controller(monkeypatch)
    controller.settings_repository.values["product_settings"] = {"delay_between_steps": 300}

    settings = controller.get_ui_settings()

    assert settings["delay_between_steps"] == 4


def test_controller_playback_restores_existing_onec_after_restart(monkeypatch) -> None:
    controller = _make_controller(monkeypatch)
    controller.app_window = type("WindowStub", (), {"show_home_page": lambda self: None})()
    scenario = Config(name="Recorded", steps=[{"type": "click", "x": 10, "y": 20}])
    scenario.settings.countdownSeconds = 0
    calls: list[str] = []
    monkeypatch.setattr(controller.recorder, "is_recording", lambda: False)
    monkeypatch.setattr(controller.scenario_manager, "load_scenario", lambda config_id: scenario)
    monkeypatch.setattr(controller.window_service, "is_window", lambda hwnd: hwnd == 200)
    monkeypatch.setattr(controller.window_service, "find_existing_onec_window", lambda executable_path=None: _window(200))
    monkeypatch.setattr(controller.window_service, "is_minimized", lambda hwnd: False)
    monkeypatch.setattr(controller.player, "play", lambda hwnd, steps, countdown: calls.append(f"play:{hwnd}:{countdown}"))

    controller.play_scenario("cfg-1")

    assert controller.active_onec_hwnd == 200
    assert calls == ["play:200:0"]
