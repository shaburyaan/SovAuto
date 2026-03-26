from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RetryPolicy:
    count: int = 3
    backoff_ms: int = 300


@dataclass(slots=True)
class TimeoutPolicy:
    timeout_ms: int = 5000
    on_timeout: str = "fail"


@dataclass(slots=True)
class LockMode:
    mode: str = "soft"


@dataclass(slots=True)
class ExecutionPolicy:
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    timeout: TimeoutPolicy = field(default_factory=TimeoutPolicy)
    on_error: str = "stop"
