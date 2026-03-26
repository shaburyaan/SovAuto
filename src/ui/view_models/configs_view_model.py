from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ConfigsViewModel:
    configs: list[dict] = field(default_factory=list)
