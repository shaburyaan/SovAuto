from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(slots=True, frozen=True)
class RuntimeContext:
    root_dir: Path
    is_packaged: bool

    @classmethod
    def detect(cls) -> "RuntimeContext":
        if getattr(sys, "frozen", False):
            root_dir = Path(sys.executable).resolve().parent
            return cls(root_dir=root_dir, is_packaged=True)
        return cls(root_dir=Path.cwd(), is_packaged=False)
