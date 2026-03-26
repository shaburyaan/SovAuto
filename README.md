# SovAuto

## English

SovAuto is a Windows desktop application for working with live 1C:Enterprise sessions as a real production runtime, not just as a code prototype. The product is designed for teams that need a stable operator workflow around 1C: capture an already opened 1C window, keep the working area inside SovAuto, record user actions into reusable scenarios, and replay those scenarios with controlled timing and focus management.

The main product idea is simple: SovAuto should not fight the user. During recording, the operator must continue working inside 1C as usual, move across tabs, open forms, enter data, and only explicitly mark reusable steps when needed. During playback, SovAuto must return the application to the working 1C area, restore focus, wait between steps, and replay actions slowly and predictably so that the real 1C interface has enough time to react.

### What SovAuto does

- Captures an already opened 1C window and hosts it inside SovAuto.
- Preserves a dedicated 1C work area inside the application shell.
- Records user scenarios based on explicit interaction logic instead of aggressive interception.
- Saves scenarios to persistent storage so they survive restarts.
- Replays scenarios inside the 1C runtime with countdown, focus restoration, and configurable delays.
- Stores runtime data in `%APPDATA%\\SovAuto`, including configs, logs, cache, and the application database.

### Key capabilities

- Manual 1C capture for stable embedded work without endless reattach loops.
- Record and playback flow for repeatable operator actions.
- Configurable step delay for slower, production-safe playback.
- Overlay states for recording, countdown, playback, and completion.
- Desktop installer flow that produces a packaged SovAuto application instead of asking users to run `main.py`.
- Build automation through PowerShell commands such as `buildAuto` and publishing automation through `pushAuto`.

### Installer and build flow

The packaged release is built as `SovAuto.exe`, bundled with the runtime assets the application expects at startup. The installer is generated as `SovAuto-Setup-<version>.exe` and is intended to install a ready-to-run Windows application. The release flow also prepares a desktop folder containing the installer package for handoff and deployment.

### Runtime data

SovAuto writes user-specific runtime data to:

- `%APPDATA%\\SovAuto\\data`
- `%APPDATA%\\SovAuto\\configs`
- `%APPDATA%\\SovAuto\\logs`
- `%APPDATA%\\SovAuto\\cache`
- `%APPDATA%\\SovAuto\\backups`

This keeps the installed application clean while preserving scenarios, logs, and internal state across sessions.

## Русский

SovAuto — это Windows-приложение для работы с живыми сессиями 1С:Предприятие как с полноценным рабочим runtime, а не как с экспериментальным кодовым прототипом. Продукт рассчитан на сценарий, где пользователь уже работает в 1С, SovAuto захватывает это окно внутрь своего интерфейса, позволяет записывать повторяемые действия в сценарии и затем воспроизводить их внутри рабочего контура 1С с контролем фокуса, времени и стабильности.

Главная идея продукта: SovAuto не должен бороться с пользователем. Во время записи оператор должен продолжать работать в 1С как обычно — переходить по вкладкам, открывать формы, вводить данные, а SovAuto должен лишь наблюдать и сохранять те шаги, которые пользователь явно хочет сделать частью сценария. Во время воспроизведения SovAuto обязан вернуть интерфейс в рабочую зону 1С, восстановить фокус, выдерживать паузы между шагами и воспроизводить действия медленно и предсказуемо, чтобы реальная 1С успевала обработать каждое действие.

### Что делает SovAuto

- Захватывает уже открытое окно 1С и размещает его внутри SovAuto.
- Держит выделенную рабочую зону 1С внутри оболочки приложения.
- Записывает пользовательские сценарии на основе явной логики взаимодействия, а не за счет агрессивного перехвата UI.
- Сохраняет сценарии в постоянное хранилище, чтобы они не пропадали после перезапуска.
- Воспроизводит сценарии внутри runtime 1С с countdown, возвратом фокуса и настраиваемыми задержками.
- Хранит runtime-данные в `%APPDATA%\\SovAuto`, включая конфиги, логи, кэш и внутреннюю базу приложения.

### Ключевые возможности

- Ручной захват 1С для стабильной встроенной работы без бесконечных reattach-loop.
- Полноценный record/playback контур для повторяемых операторских действий.
- Настраиваемая задержка между шагами для медленного и безопасного playback.
- Отдельные overlay-состояния для записи, countdown, выполнения и завершения.
- Установщик, который собирает и ставит приложение SovAuto как готовый Windows-продукт, а не требует запускать `main.py`.
- Автоматизация сборки через PowerShell-команду `buildAuto` и публикации через `pushAuto`.

### Сборка и установка

Финальный релиз собирается в виде `SovAuto.exe` и включает runtime-ассеты, которые нужны приложению при запуске. Установщик формируется как `SovAuto-Setup-<version>.exe` и предназначен для установки готового Windows-приложения. Дополнительно release-flow создает на рабочем столе отдельную папку с установочным пакетом для передачи и развёртывания.

### Где лежат пользовательские данные

SovAuto сохраняет runtime-данные пользователя в:

- `%APPDATA%\\SovAuto\\data`
- `%APPDATA%\\SovAuto\\configs`
- `%APPDATA%\\SovAuto\\logs`
- `%APPDATA%\\SovAuto\\cache`
- `%APPDATA%\\SovAuto\\backups`

Это позволяет держать установленное приложение чистым, а сценарии, логи и внутреннее состояние — постоянными между сессиями.
