from __future__ import annotations

import numpy as np
import mss

from core.models.ocr import OcrResult, ParsedValue
from ocr.engine_adapter import TesseractAdapter
from ocr.errors import OcrEmptyResultError
from ocr.normalizer import TextNormalizer
from ocr.parsers import DecimalParser
from ocr.preprocess import ImagePreprocessor


class OcrPipeline:
    def __init__(self) -> None:
        self.preprocessor = ImagePreprocessor()
        self.engine = TesseractAdapter()
        self.normalizer = TextNormalizer()
        self.parser = DecimalParser()

    def capture_and_read(self, region: dict[str, int]) -> OcrResult:
        with mss.mss() as sct:
            image = np.array(sct.grab(region))
        return self.read_image(image)

    def read_image(self, image) -> OcrResult:
        processed = self.preprocessor.process(image)
        text, confidence = self.engine.read(processed)
        normalized = self.normalizer.normalize(text)
        if not normalized:
            raise OcrEmptyResultError("OCR returned empty text")
        decimal_value = self.parser.parse(normalized)
        parsed = ParsedValue(text=normalized, decimal_value=decimal_value)
        return OcrResult(
            text=text,
            normalized_text=normalized,
            confidence=confidence,
            parsed_value=parsed,
        )
