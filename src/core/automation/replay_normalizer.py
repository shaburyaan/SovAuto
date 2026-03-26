from __future__ import annotations

from core.models.targets import RelativePoint


class ReplayNormalizer:
    def normalize_point(
        self,
        point: RelativePoint,
        bounds: tuple[int, int, int, int],
    ) -> tuple[int, int]:
        left, top, right, bottom = bounds
        width = right - left
        height = bottom - top
        return left + int(width * point.x), top + int(height * point.y)
