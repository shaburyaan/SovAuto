from __future__ import annotations

from decimal import Decimal, InvalidOperation


class NumericParser:
    def parse(self, text: str) -> Decimal | None:
        cleaned = text.replace(" ", "").replace(",", ".")
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None


class DecimalParser(NumericParser):
    pass
