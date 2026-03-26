from __future__ import annotations

import os
from pathlib import Path
import sys

import pytesseract


class TesseractAdapter:
    def __init__(self) -> None:
        self._configure_runtime()

    def _configure_runtime(self) -> None:
        if getattr(sys, "frozen", False):
            app_root = Path(sys.executable).resolve().parent
        else:
            app_root = Path.cwd()
        candidates = [
            app_root / "tesseract" / "tesseract.exe",
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
        ]
        for candidate in candidates:
            if not candidate.exists():
                continue
            pytesseract.pytesseract.tesseract_cmd = str(candidate)
            tessdata_dir = candidate.parent / "tessdata"
            if tessdata_dir.exists():
                os.environ.setdefault("TESSDATA_PREFIX", str(tessdata_dir))
            return

    def read(self, image) -> tuple[str, float | None]:
        text = pytesseract.image_to_string(image, config="--psm 6")
        return text, None
