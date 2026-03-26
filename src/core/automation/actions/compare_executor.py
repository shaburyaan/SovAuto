from __future__ import annotations

from ocr.compare_service import CompareService


class CompareExecutor:
    def __init__(self) -> None:
        self.compare_service = CompareService()

    def execute(self, step: dict) -> int:
        return self.compare_service.compare(step["regionA"], step["regionB"])
