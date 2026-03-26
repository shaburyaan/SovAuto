from __future__ import annotations

import cv2
import numpy as np


class ImagePreprocessor:
    def process(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY) if image.ndim == 3 else image
        contrast = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        threshold = cv2.adaptiveThreshold(
            contrast,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )
        return cv2.resize(threshold, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
