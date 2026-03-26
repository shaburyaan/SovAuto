from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SettingsViewModel:
    lock_mode: str = "soft"
    delay_between_steps: int = 300
    retry_count: int = 3
