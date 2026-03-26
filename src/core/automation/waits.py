from __future__ import annotations

from time import sleep

from core.automation.anchor_search import AnchorSearchService
from core.automation.window_guard import OneCWindowGuard
from ocr.pipeline import OcrPipeline


class WaitForWindowExecutor:
    def __init__(self) -> None:
        self.guard = OneCWindowGuard()

    def execute(self, step: dict) -> None:
        timeout = step.get("timeoutMs", 5000) / 1000
        elapsed = 0.0
        while elapsed <= timeout:
            if self.guard.ensure_window_ready(
                step["window"]["process_name"],
                step["window"]["title_pattern"],
            ).ok:
                return
            sleep(0.25)
            elapsed += 0.25
        raise TimeoutError("wait_for_window timeout")


class WaitForPixelExecutor:
    def __init__(self) -> None:
        self.search = AnchorSearchService()

    def execute(self, step: dict) -> None:
        timeout = step.get("timeoutMs", 5000) / 1000
        elapsed = 0.0
        while elapsed <= timeout:
            if self.search.pixel_matches(step["x"], step["y"], step["color"]):
                return
            sleep(0.25)
            elapsed += 0.25
        raise TimeoutError("wait_for_pixel timeout")


class WaitForColorExecutor(WaitForPixelExecutor):
    pass


class WaitForTextExecutor:
    def __init__(self) -> None:
        self.pipeline = OcrPipeline()

    def execute(self, step: dict) -> None:
        timeout = step.get("timeoutMs", 5000) / 1000
        elapsed = 0.0
        while elapsed <= timeout:
            result = self.pipeline.capture_and_read(step["region"])
            if step["expected"].lower() in result.normalized_text.lower():
                return
            sleep(0.5)
            elapsed += 0.5
        raise TimeoutError("wait_for_text timeout")
