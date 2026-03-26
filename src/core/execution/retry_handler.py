from __future__ import annotations

from core.contracts.cancellation import CancellationToken


class RetryHandler:
    def sleep_interruptible(
        self,
        cancellation_token: CancellationToken,
        delay_ms: int,
    ) -> bool:
        return cancellation_token.wait(delay_ms / 1000)
