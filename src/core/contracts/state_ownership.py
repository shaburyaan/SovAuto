from __future__ import annotations

from dataclasses import dataclass

from core.contracts.threading_model import ThreadDomain


@dataclass(slots=True, frozen=True)
class StateOwnerRegistry:
    owners: dict[str, ThreadDomain]

    @classmethod
    def default(cls) -> "StateOwnerRegistry":
        return cls(
            owners={
                "app_state": ThreadDomain.UI,
                "engine_state": ThreadDomain.ENGINE,
                "overlay_state": ThreadDomain.OVERLAY,
                "recorder_state": ThreadDomain.RECORDER,
                "ocr_state": ThreadDomain.OCR,
            }
        )

    def owner_of(self, state_name: str) -> ThreadDomain:
        return self.owners[state_name]
