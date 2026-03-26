from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from ui.onboarding.onboarding_overlay import OnboardingOverlay, OnboardingStep


class OnboardingController(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, overlay: OnboardingOverlay, steps: list[OnboardingStep]) -> None:
        super().__init__()
        self.overlay = overlay
        self.steps = steps
        self.index = 0
        self.overlay.next_requested.connect(self.next_step)
        self.overlay.skip_requested.connect(self.skip)

    def start(self) -> None:
        self.index = 0
        if self.steps:
            self.overlay.show_step(self.steps[0], is_last=len(self.steps) == 1)

    def next_step(self) -> None:
        self.index += 1
        if self.index >= len(self.steps):
            self.overlay.hide()
            self.finished.emit(False)
            return
        self.overlay.show_step(self.steps[self.index], is_last=self.index == len(self.steps) - 1)

    def skip(self) -> None:
        self.overlay.hide()
        self.finished.emit(True)
