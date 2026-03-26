from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, UTC


@dataclass(slots=True, frozen=True)
class BuildFingerprint:
    git_commit_hash: str = "local"
    build_timestamp: str = datetime.now(UTC).isoformat()
    installer_version: str = "1.0.0"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
