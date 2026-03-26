from __future__ import annotations

from typing import Iterable

import mss
import numpy as np


class AnchorSearchService:
    def pixel_matches(self, x: int, y: int, color_hex: str) -> bool:
        with mss.mss() as sct:
            monitor = {"left": x, "top": y, "width": 1, "height": 1}
            shot = np.array(sct.grab(monitor))
        rgb = shot[0, 0, :3]
        expected = tuple(int(color_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
        return tuple(rgb[::-1]) == expected

    def local_search(self, x: int, y: int, color_hex: str, radius: int) -> tuple[int, int] | None:
        points: Iterable[tuple[int, int]] = (
            (x + dx, y + dy)
            for dx in range(-radius, radius + 1)
            for dy in range(-radius, radius + 1)
        )
        for px, py in points:
            if self.pixel_matches(px, py, color_hex):
                return px, py
        return None
