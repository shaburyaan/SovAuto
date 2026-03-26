from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class WindowTarget:
    process_name: str = "1cv8.exe"
    title_pattern: str = "1С"


@dataclass(slots=True)
class RelativePoint:
    x: float
    y: float


@dataclass(slots=True)
class AnchorTarget:
    mode: str = "pixel"
    color: str | None = None
    search_radius: int = 24


@dataclass(slots=True)
class AnchorOffset:
    x: int = 0
    y: int = 0
