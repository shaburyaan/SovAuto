from __future__ import annotations

from core.contracts.splash_barrier import SplashLockBarrier


class SplashLockBarrierBridge:
    def __init__(self, barrier: SplashLockBarrier) -> None:
        self.barrier = barrier
