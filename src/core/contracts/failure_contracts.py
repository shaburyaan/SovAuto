from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FailureType(StrEnum):
    BOOTSTRAP_ERROR = "bootstrap_error"
    ENGINE_ERROR = "engine_error"
    OCR_ERROR = "ocr_error"
    RUNTIME_ERROR = "runtime_error"
    INSTALL_ERROR = "install_error"


class FailureSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(slots=True, frozen=True)
class RecoveryPolicy:
    auto_recovery: bool
    user_visible: bool


@dataclass(slots=True, frozen=True)
class UserVisibilityPolicy:
    user_visible: bool = True
