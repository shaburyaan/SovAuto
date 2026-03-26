from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BrandVisualRules:
    consistent_radius: bool = True
    consistent_spacing: bool = True
    mixed_native_custom_ui_forbidden: bool = True


@dataclass(slots=True, frozen=True)
class BrandMotionRules:
    allow_linear_easing: bool = False
    smooth_curves_only: bool = True
    gpu_accelerated_only: bool = True


@dataclass(slots=True, frozen=True)
class BrandContract:
    visual: BrandVisualRules = BrandVisualRules()
    motion: BrandMotionRules = BrandMotionRules()
