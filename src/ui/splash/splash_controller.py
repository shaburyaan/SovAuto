from __future__ import annotations

from PyQt6.QtCore import QParallelAnimationGroup, QPropertyAnimation, QTimer, QEasingCurve

from core.contracts.splash_barrier import SplashLockBarrier
from ui.splash.splash_animation import SplashAnimationTimeline
from ui.splash.splash_screen import SplashScreen


class SplashController:
    def __init__(self, barrier: SplashLockBarrier, splash: SplashScreen, main_window) -> None:
        self.barrier = barrier
        self.splash = splash
        self.main_window = main_window
        self.timeline = SplashAnimationTimeline(splash, splash.logo_label).build()
        self.fade_in = QPropertyAnimation(self.main_window, b"windowOpacity")
        self.fade_in.setDuration(500)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.fade_out = QPropertyAnimation(self.splash, b"windowOpacity")
        self.fade_out.setDuration(420)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.handoff = QParallelAnimationGroup(self.splash)
        self.handoff.addAnimation(self.fade_in)
        self.handoff.addAnimation(self.fade_out)
        self.fade_out.finished.connect(self.splash.close)

    def start(self) -> None:
        self.main_window.setWindowOpacity(0.0)
        self.splash.show()
        self.timeline.start()

    def finish_when_ready(self) -> None:
        def _attempt_handoff() -> None:
            if self.barrier.wait(0):
                self.main_window.show()
                self.handoff.start()
            else:
                QTimer.singleShot(100, _attempt_handoff)

        _attempt_handoff()
