from __future__ import annotations

from enum import StrEnum


class AppLifecycleState(StrEnum):
    BOOTSTRAP = "BOOTSTRAP"
    SPLASH = "SPLASH"
    READY = "READY"
    RUNNING = "RUNNING"
    SHUTDOWN = "SHUTDOWN"
