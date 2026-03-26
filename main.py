from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from core.system.runtime_context import RuntimeContext
from core.system.startup_orchestrator import StartupOrchestrator


def main() -> int:
    app = QApplication(sys.argv)
    root_dir = RuntimeContext.detect().root_dir
    icon_candidates = [
        root_dir / "sovauto.ico",
        root_dir / "_internal" / "sovauto.ico",
        root_dir / "sovauto-logo.png",
        root_dir / "_internal" / "sovauto-logo.png",
        root_dir / "Sovrano Main Logo 1.png",
        root_dir / "_internal" / "Sovrano Main Logo 1.png",
    ]
    icon_path = next((path for path in icon_candidates if path.exists()), None)
    if icon_path is not None:
        app.setWindowIcon(QIcon(str(icon_path)))
    orchestrator = StartupOrchestrator(app)
    orchestrator.start()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
