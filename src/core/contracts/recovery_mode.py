from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RecoveryMode(StrEnum):
    SOFT_ENGINE_RESTART = "soft_engine_restart"
    FULL_APP_RESTART = "full_app_restart"
    SAFE_MODE = "safe_mode"


@dataclass(slots=True)
class RecoveryCoordinator:
    current_mode: RecoveryMode = RecoveryMode.SOFT_ENGINE_RESTART
