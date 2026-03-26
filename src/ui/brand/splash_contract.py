from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SplashTimelineLock:
    skip_forbidden: bool = True
    runtime_adaptation_forbidden: bool = True
    fixed_min_ms: int = 10000
    fixed_max_ms: int = 12000


@dataclass(slots=True, frozen=True)
class SplashLogoAnimationContract:
    start_scale: float = 0.85
    end_scale: float = 1.0
    zoom_max: float = 1.05
    allow_linear_easing: bool = False


@dataclass(slots=True, frozen=True)
class SplashBackgroundContract:
    warm_milk_gradient: bool = True
    progress_bar_forbidden: bool = True
    loading_text_forbidden: bool = False


@dataclass(slots=True, frozen=True)
class SplashUxContract:
    timeline: SplashTimelineLock = SplashTimelineLock()
    logo: SplashLogoAnimationContract = SplashLogoAnimationContract()
    background: SplashBackgroundContract = SplashBackgroundContract()
