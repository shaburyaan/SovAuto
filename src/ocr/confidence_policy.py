from __future__ import annotations

from core.contracts.ocr_confidence_policy import ConfidenceDecision, OCRConfidencePolicy


class ConfidenceEvaluator:
    def __init__(self, policy: OCRConfidencePolicy | None = None) -> None:
        self.policy = policy or OCRConfidencePolicy()

    def evaluate(self, confidence: float | None, attempt: int = 1) -> ConfidenceDecision:
        return self.policy.decide(confidence, attempt)
