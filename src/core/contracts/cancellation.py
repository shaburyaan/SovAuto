from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from threading import Event


class CancellationReason(StrEnum):
    USER_STOP = "user_stop"
    TIMEOUT = "timeout"
    BOOTSTRAP_FAILURE = "bootstrap_failure"
    SHUTDOWN = "shutdown"
    OCR_FAILURE = "ocr_failure"


@dataclass(slots=True)
class CancellationToken:
    _event: Event
    reason: CancellationReason | None = None

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        return self._event.wait(timeout)


class CancellationTokenSource:
    def __init__(self) -> None:
        self._event = Event()
        self._token = CancellationToken(self._event)

    @property
    def token(self) -> CancellationToken:
        return self._token

    def cancel(self, reason: CancellationReason) -> None:
        self._token.reason = reason
        self._event.set()
