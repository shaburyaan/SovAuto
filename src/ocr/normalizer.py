from __future__ import annotations

import re


class TextNormalizer:
    def normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip().replace("O", "0")
