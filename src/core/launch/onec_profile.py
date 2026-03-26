from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from uuid import uuid4


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(slots=True)
class OneCLaunchProfile:
    exe_path: str
    profile_name: str
    profile_id: str = field(default_factory=lambda: uuid4().hex)
    launch_arguments: list[str] = field(default_factory=list)
    last_base_hint: str = ""
    last_window_title: str = "1С"
    last_command_line: str = ""
    embed_enabled: bool = True
    last_started_at: str | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def mark_started(self) -> None:
        now = _now()
        self.last_started_at = now
        self.updated_at = now

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict) -> "OneCLaunchProfile":
        migrated = dict(raw)
        if "base_hint" in migrated and "last_base_hint" not in migrated:
            migrated["last_base_hint"] = migrated.pop("base_hint")
        if "window_title_pattern" in migrated and "last_window_title" not in migrated:
            migrated["last_window_title"] = migrated.pop("window_title_pattern")
        migrated.setdefault("last_base_hint", "")
        migrated.setdefault("last_window_title", "1С")
        migrated.setdefault("last_command_line", "")
        return cls(**migrated)
