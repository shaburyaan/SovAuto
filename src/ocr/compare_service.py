from __future__ import annotations

from decimal import Decimal

from ocr.pipeline import OcrPipeline


class CompareService:
    def __init__(self) -> None:
        self.pipeline = OcrPipeline()

    def compare(self, region_a: dict[str, int], region_b: dict[str, int]) -> int:
        result_a = self.pipeline.capture_and_read(region_a)
        result_b = self.pipeline.capture_and_read(region_b)
        value_a = result_a.parsed_value.decimal_value if result_a.parsed_value else None
        value_b = result_b.parsed_value.decimal_value if result_b.parsed_value else None
        if isinstance(value_a, Decimal) and isinstance(value_b, Decimal):
            return (value_a > value_b) - (value_a < value_b)
        return (result_a.normalized_text > result_b.normalized_text) - (
            result_a.normalized_text < result_b.normalized_text
        )
