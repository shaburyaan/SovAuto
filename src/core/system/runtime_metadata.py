from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RuntimeMetadata:
    version: str
    config: dict[str, Any] = field(default_factory=dict)
    runtime_metadata: dict[str, Any] = field(default_factory=dict)


class RuntimeMetadataStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def save(self, metadata: RuntimeMetadata) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")

    def load(self) -> RuntimeMetadata | None:
        if not self.path.exists():
            return None
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return RuntimeMetadata(**raw)
