from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass(slots=True)
class StabilityScore:
    value: int = 100


@dataclass(slots=True)
class ConfigReliabilityMetadata:
    stability_score: StabilityScore = field(default_factory=StabilityScore)
    last_success_at: str | None = None
    last_failure_at: str | None = None
    notes: str = ""

    @staticmethod
    def now() -> str:
        return datetime.now(UTC).isoformat()
