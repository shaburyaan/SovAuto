from __future__ import annotations

import win32gui
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.brand.theme import build_stylesheet
from ui.dialogs.confirm_click_dialog import ConfirmClickDialog
from ui.dialogs.error_dialog import ErrorDialog
from ui.dialogs.input_value_dialog import InputValueDialog
from ui.dialogs.scenario_name_dialog import ScenarioNameDialog
from ui.feedback.toast_manager import ToastManager
from ui.host.onec_embed_controller import OneCEmbedController
from ui.i18n.strings import UiStrings
from ui.onboarding.onboarding_controller import OnboardingController
from ui.onboarding.onboarding_overlay import OnboardingOverlay, OnboardingStep
from ui.pages.about_page import AboutPage
from ui.pages.configs_page import ConfigsPage
from ui.pages.home_page import HomePage
from ui.pages.settings_page import SettingsPage


class AppWindow(QMainWindow):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller
        self._runtime_started = False
        self._onboarding_started = False
        self.embed_controller = OneCEmbedController()
        self._log_drawer_open = False
        self._log_drawer_width = 340
        self.setWindowTitle(UiStrings.APP_TITLE)
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)
        self.setStyleSheet(build_stylesheet())
        self._build_ui()
        self._bind()
        self.refresh_configs()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(114)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 14, 12, 14)
        sidebar_layout.setSpacing(8)
        brand_title = QLabel(UiStrings.APP_TITLE)
        brand_title.setObjectName("sectionTitle")
        brand_subtitle = QLabel(UiStrings.BRAND_SHELL_SUBTITLE)
        brand_subtitle.setObjectName("sectionSubtitle")
        brand_subtitle.setWordWrap(True)
        sidebar_layout.addWidget(brand_title)
        sidebar_layout.addWidget(brand_subtitle)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_home = self._make_nav_button(UiStrings.NAV_HOME)
        self.nav_configs = self._make_nav_button(UiStrings.NAV_CONFIGS)
        self.nav_settings = self._make_nav_button(UiStrings.NAV_SETTINGS)
        self.nav_about = self._make_nav_button(UiStrings.NAV_ABOUT)
        for index, button in enumerate(
            [self.nav_home, self.nav_configs, self.nav_settings, self.nav_about]
        ):
            self.nav_group.addButton(button, index)
            sidebar_layout.addWidget(button)
        self.nav_home.setChecked(True)
        sidebar_layout.addStretch(1)

        center_layout = QVBoxLayout()
        center_layout.setSpacing(12)
        self.stack = QStackedWidget()
        self.home_page = HomePage()
        self.configs_page = ConfigsPage()
        self.settings_page = SettingsPage()
        self.about_page = AboutPage()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.configs_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.about_page)
        center_layout.addWidget(self.stack, 1)

        self.action_bar = QFrame()
        self.action_bar.setObjectName("actionBar")
        action_layout = QHBoxLayout(self.action_bar)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(10)
        self.launch_onec_button = QPushButton(UiStrings.ACTION_LAUNCH_ONEC)
        self.attach_onec_button = QPushButton(UiStrings.ACTION_ATTACH_ONEC)
        self.run_button = QPushButton(UiStrings.ACTION_RUN)
        self.pause_button = QPushButton(UiStrings.ACTION_PAUSE)
        self.stop_button = QPushButton(UiStrings.ACTION_STOP)
        self.record_button = QPushButton(UiStrings.ACTION_RECORD)
        self.record_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.logs_button = QPushButton(UiStrings.ACTION_LOGS)
        for button in [
            self.launch_onec_button,
            self.attach_onec_button,
            self.run_button,
            self.pause_button,
            self.stop_button,
            self.record_button,
        ]:
            action_layout.addWidget(button)
        action_layout.addStretch(1)
        action_layout.addWidget(self.logs_button)
        center_layout.addWidget(self.action_bar)
        center_widget = QWidget()
        center_widget.setLayout(center_layout)

        main_layout.addWidget(self.sidebar, 0)
        main_layout.addWidget(center_widget, 1)

        self.toast_manager = ToastManager(self)
        self.log_drawer = QFrame(self)
        self.log_drawer.setObjectName("rightPane")
        self.log_drawer.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.log_drawer.hide()
        drawer_layout = QVBoxLayout(self.log_drawer)
        drawer_layout.setContentsMargins(16, 16, 16, 16)
        drawer_layout.setSpacing(12)
        self.right_title = QLabel(UiStrings.PANEL_STATUS_TITLE)
        self.right_title.setObjectName("sectionTitle")
        self.right_status = QLabel(UiStrings.HOME_STATUS_READY)
        self.right_status.setObjectName("sectionSubtitle")
        self.right_hint = QLabel(UiStrings.PANEL_STATUS_HINT)
        self.right_hint.setObjectName("sectionSubtitle")
        self.right_hint.setWordWrap(True)
        self.log_list = QListWidget()
        drawer_layout.addWidget(self.right_title)
        drawer_layout.addWidget(self.right_status)
        drawer_layout.addWidget(self.right_hint)
        drawer_layout.addWidget(self.log_list, 1)
        self.onboarding_overlay = OnboardingOverlay(self)
        self.onboarding_controller = OnboardingController(
            self.onboarding_overlay,
            [
                OnboardingStep(
                    UiStrings.ONBOARDING_WELCOME_TITLE,
                    UiStrings.ONBOARDING_WELCOME_TEXT,
                    self.sidebar,
                ),
                OnboardingStep(
                    UiStrings.ONBOARDING_HOST_TITLE,
                    UiStrings.ONBOARDING_HOST_TEXT,
                    self.home_page.host_widget,
                ),
                OnboardingStep(
                    UiStrings.ONBOARDING_ACTIONS_TITLE,
                    UiStrings.ONBOARDING_ACTIONS_TEXT,
                    self.action_bar,
                ),
                OnboardingStep(
                    UiStrings.ONBOARDING_LOGS_TITLE,
                    UiStrings.ONBOARDING_LOGS_TEXT,
                    self.logs_button,
                ),
            ],
        )
        self._position_log_drawer()
        self.record_shortcut = QShortcut(QKeySequence("F6"), self)
        self.stop_shortcut = QShortcut(QKeySequence("F8"), self)
        self.run_shortcut = QShortcut(QKeySequence("F9"), self)

    def _make_nav_button(self, title: str) -> QPushButton:
        button = QPushButton(title)
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _bind(self) -> None:
        self.nav_group.idClicked.connect(self.stack.setCurrentIndex)
        self.nav_group.idClicked.connect(self._log_screen_transition)
        self.configs_page.delete_button.clicked.connect(self._delete_selected)
        self.configs_page.list_widget.customContextMenuRequested.connect(self._show_configs_context_menu)
        self.settings_page.save_button.clicked.connect(self._save_settings)
        self.settings_page.onboarding_button.clicked.connect(self._restart_onboarding)
        self.launch_onec_button.clicked.connect(self._launch_onec_clicked)
        self.attach_onec_button.clicked.connect(self.controller.attach_existing_onec)
        self.run_button.clicked.connect(self._run_selected)
        self.pause_button.clicked.connect(self.controller.pause_resume)
        self.stop_button.clicked.connect(self.controller.stop)
        self.record_button.clicked.connect(self._toggle_recording)
        self.record_button.customContextMenuRequested.connect(self._show_recording_mode_menu)
        self.record_shortcut.activated.connect(self._toggle_recording)
        self.stop_shortcut.activated.connect(self._handle_stop_shortcut)
        self.run_shortcut.activated.connect(self._run_selected)
        self.logs_button.clicked.connect(self._toggle_log_drawer)
        self.controller.configs_changed.connect(self.refresh_configs)
        self.controller.scenario_list_changed.connect(self.refresh_configs)
        self.controller.engine_state_changed.connect(self._update_engine_state)
        self.controller.error_occurred.connect(lambda text: ErrorDialog.show(self, "Ошибка", text))
        self.controller.toast_requested.connect(self.toast_manager.show_message)
        self.controller.activity_logged.connect(self._append_log)
        self.controller.onec_state_changed.connect(self._handle_onec_state)
        self.controller.record_click_pending.connect(self._handle_record_click_pending)
        self.controller.recording_state_changed.connect(self._handle_recording_state)
        self.controller.recording_finish_requested.connect(self._finish_recording_prompt)
        self.controller.playback_state_changed.connect(self._handle_playback_state)
        self.controller.about_info_changed.connect(self.about_page.info_label.setPlainText)
        self.onboarding_controller.finished.connect(self._finish_onboarding)

    def refresh_configs(self) -> None:
        self.configs_page.list_widget.clear()
        configs = self.controller.load_configs()
        for config in configs:
            self.configs_page.list_widget.addItem(f"{config.id}|{config.name}")
        self.configs_page.empty_label.setVisible(not bool(configs))
        self.about_page.info_label.setPlainText(self.controller.get_about_info())

        settings = self.controller.get_ui_settings()
        self.settings_page.path_edit.setText(settings["onec_manual_path"])
        self.settings_page.delay_box.setValue(settings["delay_between_steps"])
        self.settings_page.retry_box.setValue(settings["retry_count"])
        self.settings_page.embed_checkbox.setChecked(settings["embed_enabled"])
        lock_mode_display = (
            UiStrings.LOCK_MODE_HARD if settings["lock_mode"] == "hard" else UiStrings.LOCK_MODE_SOFT
        )
        index = self.settings_page.lock_mode.findText(lock_mode_display)
        self.settings_page.lock_mode.setCurrentIndex(max(index, 0))

    def _selected_config_id(self) -> str | None:
        item = self.configs_page.list_widget.currentItem()
        if item is None:
            return None
        return item.text().split("|", 1)[0]

    def _delete_selected(self) -> None:
        config_id = self._selected_config_id()
        if config_id:
            self.controller.delete_config(config_id)

    def _run_selected(self) -> None:
        config_id = self._selected_config_id()
        if config_id is None and self.configs_page.list_widget.count():
            self.configs_page.list_widget.setCurrentRow(0)
            config_id = self._selected_config_id()
        if config_id:
            self.controller.run_config(config_id)

    def show_home_page(self) -> None:
        self.nav_home.setChecked(True)
        self.stack.setCurrentWidget(self.home_page)

    def _save_settings(self) -> None:
        lock_mode = (
            "hard"
            if self.settings_page.lock_mode.currentText() == UiStrings.LOCK_MODE_HARD
            else "soft"
        )
        self.controller.save_ui_settings(
            self.settings_page.path_edit.text(),
            lock_mode,
            self.settings_page.delay_box.value(),
            self.settings_page.retry_box.value(),
            self.settings_page.embed_checkbox.isChecked(),
        )

    def _launch_onec_clicked(self) -> None:
        self.toast_manager.show_message(UiStrings.TOAST_OPEN_ONEC_MANUALLY)

    def _toggle_recording(self) -> None:
        if self.controller.is_recording():
            self._finish_recording_prompt()
            return
        self.controller.start_recording(self.controller.current_recording_mode())

    def _handle_stop_shortcut(self) -> None:
        if self.controller.is_recording() or self.controller.is_recording_finish_pending():
            if self.controller.is_recording():
                self.controller.request_finish_recording()
            return
        self.controller.stop()

    def _finish_recording_prompt(self) -> None:
        scenario_name, accepted = ScenarioNameDialog.get_name(self)
        if not accepted:
            self.controller.cancel_finish_recording()
            self.toast_manager.show_message(UiStrings.toast_payload(UiStrings.ERROR_SCENARIO_NAME_REQUIRED, kind="error"))
            return
        scenario = self.controller.finish_recording(scenario_name)
        if scenario is not None:
            self.stack.setCurrentWidget(self.configs_page)

    def _show_recording_mode_menu(self, pos) -> None:
        menu = QMenu(self)
        navigation_action = menu.addAction("Переход")
        input_action = menu.addAction("Заполнение")
        chosen = menu.exec(self.record_button.mapToGlobal(pos))
        if chosen is navigation_action and self.controller.is_recording():
            self.controller.switch_recording_mode("navigation")
        elif chosen is navigation_action:
            self.controller.start_recording("navigation")
        elif chosen is input_action and self.controller.is_recording():
            self.controller.switch_recording_mode("input")
        elif chosen is input_action:
            self.controller.start_recording("input")

    def _handle_record_click_pending(self, payload: object) -> None:
        data = dict(payload)
        self.controller.record_overlay.hide()
        if not ConfirmClickDialog.confirm(self):
            self.controller.reject_recorded_click()
            return
        if data.get("mode") == "input":
            text, accepted = InputValueDialog.get_text(self)
            if not accepted:
                self.toast_manager.show_message(UiStrings.toast_payload(UiStrings.ERROR_INPUT_TEXT_REQUIRED, kind="error"))
                self.controller.reject_recorded_click()
                return
            self.controller.accept_recorded_click(text)
            return
        self.controller.accept_recorded_click()

    def _handle_recording_state(self, payload: object) -> None:
        data = dict(payload)
        is_recording = bool(data.get("recording"))
        self.record_button.setText(UiStrings.ACTION_RECORD_ACTIVE if is_recording else UiStrings.ACTION_RECORD)
        self.run_button.setEnabled(not is_recording)

    def _handle_playback_state(self, payload: object) -> None:
        data = dict(payload)
        status = str(data.get("status", ""))
        is_busy = status in {"countdown", "running", "completed"}
        self.record_button.setEnabled(not is_busy)
        self.run_button.setEnabled(not is_busy and not self.controller.is_recording())
        if status == "finished":
            self.record_button.setEnabled(True)
            self.run_button.setEnabled(not self.controller.is_recording())

    def _show_configs_context_menu(self, pos) -> None:
        item = self.configs_page.list_widget.itemAt(pos)
        if item is None:
            return
        self.configs_page.list_widget.setCurrentItem(item)
        menu = QMenu(self)
        run_action = menu.addAction(UiStrings.CONFIGS_CONTEXT_RUN)
        delete_action = menu.addAction(UiStrings.ACTION_DELETE)
        chosen = menu.exec(self.configs_page.list_widget.mapToGlobal(pos))
        if chosen is run_action:
            self._run_selected()
        elif chosen is delete_action:
            self._delete_selected()

    def _update_engine_state(self, state: str) -> None:
        self.home_page.set_engine_state(state)
        self.right_status.setText(UiStrings.engine_state_label(state))
        self.pause_button.setText(UiStrings.ACTION_RESUME if state == "paused" else UiStrings.ACTION_PAUSE)

    def _handle_onec_state(self, state: object) -> None:
        data = dict(state)
        status = data.get("status", "")
        if status == "attached":
            base_hint = data.get("base_hint") or "Sovut"
            hwnd = int(data.get("hwnd", 0))
            current_hwnd = self.embed_controller.primary_hwnd()
            if current_hwnd is not None and current_hwnd != hwnd:
                self.embed_controller.lifecycle_cleanup()
            container = self.embed_controller.attach(hwnd, self.home_page.host_widget.content_frame)
            if container is not None:
                self.home_page.host_widget.set_embedded(container, base_hint)
                self.home_page.set_session_status(UiStrings.HOME_STATUS_EMBEDDED)
                self.right_status.setText(UiStrings.HOME_STATUS_EMBEDDED)
                self.toast_manager.show_message(UiStrings.TOAST_ATTACH_SUCCESS)
                return
            self.home_page.host_widget.set_failed(self.embed_controller.last_error or UiStrings.ERROR_ONEC_EMBED_FAILED)
            self.home_page.set_session_status(UiStrings.HOME_STATUS_FAILED)
            self.right_status.setText(UiStrings.HOME_STATUS_FAILED)
            return
        message = data.get("message", UiStrings.ERROR_GENERIC)
        self.embed_controller.lifecycle_cleanup()
        self.home_page.host_widget.set_failed(message)
        self.home_page.set_session_status(UiStrings.HOME_STATUS_FAILED)
        self.right_status.setText(UiStrings.HOME_STATUS_FAILED)

    def _append_log(self, line: str) -> None:
        if not line:
            return
        self.log_list.insertItem(0, line)
        while self.log_list.count() > 100:
            self.log_list.takeItem(self.log_list.count() - 1)

    def _log_screen_transition(self, index: int) -> None:
        screens = {
            0: UiStrings.NAV_HOME,
            1: UiStrings.NAV_CONFIGS,
            2: UiStrings.NAV_SETTINGS,
            3: UiStrings.NAV_ABOUT,
        }
        self.controller.telemetry.log_screen_transition(screens.get(index, "unknown"))

    def _restart_onboarding(self) -> None:
        self.controller.reset_onboarding()
        self._start_onboarding()

    def _start_onboarding(self) -> None:
        self.controller.telemetry.log_onboarding("start")
        self.onboarding_controller.start()

    def _finish_onboarding(self, skipped: bool) -> None:
        self.controller.mark_onboarding_completed(skipped=skipped)

    def _toggle_log_drawer(self) -> None:
        self._log_drawer_open = not self._log_drawer_open
        if self._log_drawer_open:
            self._position_log_drawer()
            self.log_drawer.show()
            self.log_drawer.raise_()
        else:
            self.log_drawer.hide()

    def _position_log_drawer(self) -> None:
        if not self._log_drawer_open:
            return
        frame = self.frameGeometry()
        available = self.screen().availableGeometry() if self.screen() is not None else frame
        x = min(frame.right() + 8, available.right() - self._log_drawer_width)
        y = max(available.top() + 12, frame.top() + 48)
        height = min(max(320, frame.height() - 72), available.bottom() - y)
        self.log_drawer.setGeometry(x, y, self._log_drawer_width, max(320, height))

    def resizeEvent(self, event) -> None:  # noqa: N802
        self.onboarding_overlay.setGeometry(self.rect())
        self._position_log_drawer()
        if self.home_page.host_widget.mode == "embedded":
            self.embed_controller.sync_geometry(self.home_page.host_widget.content_frame, force=True)
        super().resizeEvent(event)

    def moveEvent(self, event) -> None:  # noqa: N802
        self._position_log_drawer()
        super().moveEvent(event)

    def closeEvent(self, event) -> None:  # noqa: N802
        self.controller.telemetry.log_ui_action("window_close")
        self.log_drawer.hide()
        self.embed_controller.lifecycle_cleanup()
        self.controller.shutdown()
        super().closeEvent(event)

    def showEvent(self, event) -> None:  # noqa: N802
        if not self.isMaximized():
            self.showMaximized()
        if not self._runtime_started:
            self.controller.start_runtime_services()
            self._runtime_started = True
        if not self._onboarding_started and self.controller.should_show_onboarding():
            self._onboarding_started = True
            QTimer.singleShot(600, self._start_onboarding)
        super().showEvent(event)
