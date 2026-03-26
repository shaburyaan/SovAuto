from __future__ import annotations

from ui.overlay.overlay_state import OverlayViewState


class OverlayPresenter:
    def present(self, state: OverlayViewState) -> str:
        return f"{state.state} | steps: {state.step_count}"
