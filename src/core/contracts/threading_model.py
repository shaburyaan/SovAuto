from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ThreadDomain(StrEnum):
    UI = "ui"
    ENGINE = "engine"
    RECORDER = "recorder"
    OCR = "ocr"
    OVERLAY = "overlay"


@dataclass(slots=True, frozen=True)
class ThreadOwnershipRules:
    domain: ThreadDomain
    owns_state: tuple[str, ...]
    may_publish_events: bool = True
    may_mutate_other_state: bool = False


@dataclass(slots=True, frozen=True)
class DispatchPolicy:
    event_type: str
    owner: ThreadDomain
    consumers: tuple[ThreadDomain, ...]
