from __future__ import annotations

import json
from pathlib import Path

from core.models.config import Config, ConfigMetadata, ConfigSettings
from core.models.config_metadata import ConfigReliabilityMetadata, StabilityScore


class ConfigSerializer:
    def dump(self, config: Config, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")

    def load(self, path: Path) -> Config:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return self.from_dict(raw)

    def from_dict(self, raw: dict) -> Config:
        settings = ConfigSettings(**raw.get("settings", {}))
        metadata = ConfigMetadata(**raw.get("metadata", {}))
        reliability_raw = raw.get("reliability", {})
        score_raw = reliability_raw.get("stability_score", {"value": 100})
        reliability = ConfigReliabilityMetadata(
            stability_score=StabilityScore(**score_raw),
            last_success_at=reliability_raw.get("last_success_at"),
            last_failure_at=reliability_raw.get("last_failure_at"),
            notes=reliability_raw.get("notes", ""),
        )
        return Config(
            id=raw["id"],
            name=raw["name"],
            steps=raw.get("steps", []),
            settings=settings,
            metadata=metadata,
            reliability=reliability,
        )
