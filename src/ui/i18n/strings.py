from __future__ import annotations


class UiStrings:
    APP_TITLE = "SovAuto"
    SPLASH_LOADING = "Идёт загрузка..."
    SPLASH_SUBTITLE = "Подготавливаем рабочую среду Sovrano"

    NAV_HOME = "Главная"
    NAV_CONFIGS = "Сценарии"
    NAV_SETTINGS = "Настройки"
    NAV_ABOUT = "О приложении"
    BRAND_SHELL_SUBTITLE = "Ручной захват реального окна 1С"
    PANEL_STATUS_TITLE = "Статус и журнал"
    PANEL_STATUS_HINT = "Здесь отображаются действия пользователя, состояние 1С и ответы SovAuto."

    HOME_TITLE = "Рабочая зона 1С"
    HOME_SUBTITLE = "Откройте 1С вручную, затем захватите окно внутрь SovAuto."
    HOME_STATUS_READY = "Система готова к работе"
    HOME_STATUS_WAITING = "Ожидание ручного запуска 1С"
    HOME_STATUS_LOADING = "Подключение 1С"
    HOME_STATUS_EMBEDDED = "1С встроена в SovAuto"
    HOME_STATUS_FAILED = "Не удалось подключить 1С"
    HOME_PLACEHOLDER = "Сначала откройте 1С вручную, затем нажмите «Захватить 1С»."

    ACTION_LAUNCH_ONEC = "Откройте 1С вручную"
    ACTION_ATTACH_ONEC = "Захватить 1С"
    ACTION_RUN = "Запустить (F9)"
    ACTION_PAUSE = "Пауза"
    ACTION_RESUME = "Продолжить"
    ACTION_STOP = "Стоп (F8)"
    ACTION_RECORD = "Запись (F6)"
    ACTION_RECORD_ACTIVE = "Идет запись (F6)"
    ACTION_STOP_RECORDING = "Завершить запись"
    ACTION_LOGS = "Логи"
    ACTION_CREATE = "Создать сценарий"
    ACTION_DELETE = "Удалить сценарий"
    ACTION_SAVE = "Сохранить"
    ACTION_SKIP = "Пропустить"
    ACTION_NEXT = "Далее"
    ACTION_FINISH = "Завершить"
    ACTION_RETRY = "Повторить"

    CONFIGS_TITLE = "Сценарии автоматизации"
    CONFIGS_EMPTY = "Сценарии пока не созданы."
    CONFIGS_NEW_NAME = "Новый сценарий"
    CONFIGS_CONTEXT_RUN = "Запустить конфиг"

    SETTINGS_TITLE = "Настройки SovAuto"
    SETTINGS_ONEC_PATH = "Путь к 1С"
    SETTINGS_LOCK_MODE = "Режим блокировки"
    SETTINGS_DELAY = "Задержка между шагами"
    SETTINGS_RETRY = "Повторы шага"
    SETTINGS_ONBOARDING = "Повторно показать обучение"
    SETTINGS_EMBED = "Пытаться встроить окно 1С"
    SETTINGS_EMBED_HINT = "Если встраивание не сработает, SovAuto автоматически переключится во внешний режим."

    ABOUT_TITLE = "О приложении"
    ABOUT_VERSION = "Версия"
    ABOUT_RUNTIME = "Рабочие пути"
    ABOUT_BUILD = "Сборка"

    TOAST_OPEN_ONEC_MANUALLY = "Откройте 1С вручную, затем нажмите «Захватить 1С»."
    TOAST_ATTACH_SUCCESS = "Окно 1С подключено."
    TOAST_RECORDING_STARTED = "Запись запущена."
    TOAST_RECORDING_STEP_SAVED = "Шаг записи сохранён."
    TOAST_RECORDING_CANCELLED = "Запись отменена."
    TOAST_RECORDING_EMPTY = "Нет шагов для сохранения."
    TOAST_RECORDING_CONFIRM = "Подтвердите выбранное место."
    TOAST_RECORDING_ALT_HINT = "Наведи курсор и нажми ALT для записи шага"
    TOAST_SCENARIO_SAVED = "Сценарий сохранён."
    TOAST_SCENARIO_SAVED_OK = "Конфиг сохранен"
    TOAST_PLAYBACK_RUNNING = "Не трогайте мышь и клавиатуру"
    TOAST_PLAYBACK_COMPLETED = "Бот завершил работу"
    TOAST_PLAYBACK_STOPPED = "Воспроизведение остановлено."
    TOAST_PLAYBACK_PAUSE_UNAVAILABLE = "Пауза для playback пока недоступна."
    TOAST_CONFIG_CREATED = "Сценарий создан."
    TOAST_CONFIG_DELETED = "Сценарий удалён."
    TOAST_RUN_STARTED = "Выполнение сценария начато."
    TOAST_RUN_STOPPED = "Выполнение остановлено."
    TOAST_SETTINGS_SAVED = "Настройки сохранены."
    TOAST_ONBOARDING_SKIPPED = "Обучение пропущено."
    TOAST_RECORDING_SOON = "Режим записи будет расширен в следующем цикле."
    TOAST_LOGS_AVAILABLE = "Журнал уже доступен справа."

    ERROR_GENERIC = "Произошла ошибка. Попробуйте ещё раз."
    ERROR_CONFIG_NOT_FOUND = "Сценарий не найден."
    ERROR_ONEC_PATH_NOT_FOUND = "Не удалось найти установленную 1С."
    ERROR_ONEC_LAUNCH_FAILED = "Не удалось запустить 1С."
    ERROR_ONEC_ATTACH_FAILED = "Не удалось подключить окно 1С."
    ERROR_ONEC_PICK_PATH = "Укажите путь к файлу 1cv8.exe."
    ERROR_ONEC_EMBED_FAILED = "Не удалось встроить окно 1С."
    ERROR_RECORDING_REQUIRES_ONEC = "Сначала встроите рабочую 1С."
    ERROR_RECORDING_ALREADY_ACTIVE = "Запись уже идет."
    ERROR_RECORDING_BLOCKED_BY_PLAYBACK = "Сначала остановите playback."
    ERROR_PLAYBACK_REQUIRES_ONEC = "Для запуска сценария нужна встроенная 1С."
    ERROR_PLAYBACK_BLOCKED_BY_RECORDING = "Нельзя запускать playback во время записи."
    ERROR_SCENARIO_NAME_REQUIRED = "Введите имя сценария."
    ERROR_INPUT_TEXT_REQUIRED = "Введите текст для шага заполнения."
    RECORD_CONFIRM_ACTION = "Записать это действие?"

    PICKER_ONEC_TITLE = "Выберите 1cv8.exe"
    PICKER_ONEC_FILTER = "Исполняемый файл 1С (1cv8.exe);;Исполняемые файлы (*.exe)"

    ONBOARDING_WELCOME_TITLE = "Добро пожаловать в SovAuto"
    ONBOARDING_WELCOME_TEXT = "SovAuto помогает запускать 1С, запоминать последний рабочий профиль и управлять сценариями автоматизации."
    ONBOARDING_HOST_TITLE = "Рабочая зона 1С"
    ONBOARDING_HOST_TEXT = "Здесь отображается подключённая 1С: встроенно или во внешнем прикреплённом режиме."
    ONBOARDING_ACTIONS_TITLE = "Панель действий"
    ONBOARDING_ACTIONS_TEXT = "Отсюда запускаются 1С, сценарии, запись и просмотр логов."
    ONBOARDING_LOGS_TITLE = "Статус и журнал"
    ONBOARDING_LOGS_TEXT = "Здесь видны шаги пользователя, состояние системы и ответы SovAuto."

    LOCK_MODE_SOFT = "Мягкая блокировка"
    LOCK_MODE_HARD = "Жёсткая блокировка"

    @staticmethod
    def engine_state_label(state: str) -> str:
        mapping = {
            "idle": "Движок в режиме ожидания",
            "countdown": "Идёт обратный отсчёт",
            "running": "Сценарий выполняется",
            "paused": "Сценарий на паузе",
            "stopped": "Сценарий остановлен",
            "failed": "Сценарий завершился с ошибкой",
            "completed": "Сценарий завершён",
        }
        return mapping.get(state.lower(), f"Состояние: {state}")

    @staticmethod
    def recording_mode_label(mode: str) -> str:
        mapping = {
            "navigation": "Режим записи: Переход",
            "input": "Режим записи: Заполнение",
        }
        return mapping.get(mode, f"Режим записи: {mode}")

    @staticmethod
    def countdown_label(seconds: int) -> str:
        return str(seconds)

    @staticmethod
    def toast_payload(message: str, kind: str = "default", timeout_ms: int = 2600) -> dict[str, object]:
        return {
            "message": message,
            "kind": kind,
            "timeout_ms": timeout_ms,
        }

    @staticmethod
    def save_error_label(reason: str) -> str:
        normalized = reason.strip() or UiStrings.ERROR_GENERIC
        return f"Произошла ошибка: {normalized}"
