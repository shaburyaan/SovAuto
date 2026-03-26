from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class FirstImpressionRules:
    onboarding_over_splash_forbidden: bool = True
    splash_always_full_sequence: bool = True


@dataclass(slots=True, frozen=True)
class ExecutionTrustRules:
    countdown_visible: bool = True
    minimum_countdown_seconds: int = 5
    lock_warning_visible: bool = True


@dataclass(slots=True, frozen=True)
class ErrorUxRules:
    human_readable_only: bool = True
    technical_dump_forbidden: bool = True


@dataclass(slots=True, frozen=True)
class UxContract:
    first_impression: FirstImpressionRules = FirstImpressionRules()
    execution_trust: ExecutionTrustRules = ExecutionTrustRules()
    errors: ErrorUxRules = ErrorUxRules()
