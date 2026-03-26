from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PerformanceBudget:
    ui_response_ms: int = 16
    ocr_min_ms: int = 300
    ocr_max_ms: int = 800
    step_execution_ms: int = 1000
    splash_min_ms: int = 10000
    splash_max_ms: int = 12000
    overlay_non_blocking: bool = True
