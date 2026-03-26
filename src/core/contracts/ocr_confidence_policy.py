from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ConfidenceDecision(StrEnum):
    ACCEPT = "accept"
    RETRY = "retry"
    FALLBACK = "fallback"


@dataclass(slots=True, frozen=True)
class OCRConfidencePolicy:
    min_accept_threshold: float = 0.75
    retry_limit: int = 3
    fallback_behavior: ConfidenceDecision = ConfidenceDecision.FALLBACK

    def decide(self, confidence: float | None, attempt: int = 1) -> ConfidenceDecision:
        if confidence is None:
            return self.fallback_behavior
        if confidence >= self.min_accept_threshold:
            return ConfidenceDecision.ACCEPT
        if attempt < self.retry_limit:
            return ConfidenceDecision.RETRY
        return self.fallback_behavior
