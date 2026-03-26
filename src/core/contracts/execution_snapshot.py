from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ExecutionContextSnapshot:
    window_state: dict[str, Any] = field(default_factory=dict)
    screen_geometry: dict[str, Any] = field(default_factory=dict)
    active_config_version: str = "1.0"
    runtime_flags: dict[str, Any] = field(default_factory=dict)
    input_lock_state: str = "soft"
