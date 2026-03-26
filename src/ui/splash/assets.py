from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QPixmap

from core.system.runtime_context import RuntimeContext


class SplashAssetProvider:
    def __init__(self) -> None:
        root_dir = RuntimeContext.detect().root_dir
        candidates = [
            root_dir / "sovauto-logo.png",
            root_dir / "_internal" / "sovauto-logo.png",
            root_dir / "Sovrano Main Logo 1.png",
            root_dir / "_internal" / "Sovrano Main Logo 1.png",
        ]
        self.logo_path = next((path for path in candidates if path.exists()), candidates[0])

    def load_logo(self) -> QPixmap:
        return QPixmap(str(self.logo_path))
