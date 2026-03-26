from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class OcrRequest:
    image: Any
    parse_mode: str = "text"


@dataclass(slots=True)
class ParsedValue:
    text: str
    decimal_value: Decimal | None = None


@dataclass(slots=True)
class OcrResult:
    text: str
    normalized_text: str
    confidence: float | None = None
    parsed_value: ParsedValue | None = None
