from __future__ import annotations

from dataclasses import dataclass

from core.automation.anchor_search import AnchorSearchService
from core.automation.replay_normalizer import ReplayNormalizer
from core.automation.window_guard import OneCWindowGuard
from core.models.targets import AnchorOffset, AnchorTarget, RelativePoint, WindowTarget


@dataclass(slots=True)
class ResolvedTarget:
    x: int
    y: int
    method: str


class TargetResolver:
    def __init__(self) -> None:
        self.window_guard = OneCWindowGuard()
        self.normalizer = ReplayNormalizer()
        self.anchor_search = AnchorSearchService()

    def resolve(
        self,
        window: WindowTarget,
        point: RelativePoint,
        anchor: AnchorTarget | None = None,
        offset: AnchorOffset | None = None,
    ) -> ResolvedTarget:
        probe = self.window_guard.ensure_window_ready(window.process_name, window.title_pattern)
        if not probe.ok or probe.window is None:
            raise RuntimeError(probe.reason)
        x, y = self.normalizer.normalize_point(point, probe.window.bounds)
        if anchor and anchor.color:
            match = self.anchor_search.local_search(x, y, anchor.color, anchor.search_radius)
            if match:
                x, y = match
                method = "anchor"
            else:
                method = "relative"
        else:
            method = "relative"
        if offset:
            x += offset.x
            y += offset.y
        return ResolvedTarget(x=x, y=y, method=method)
