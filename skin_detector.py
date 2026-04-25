from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True)
class SkinDetectionResult:
    coverage_ratio: float
    status: str
    detail_text: str


class SkinDetector:
    """Highlights likely skin regions using combined HSV and YCrCb masking."""

    def process_frame(self, frame: cv2.typing.MatLike) -> tuple[cv2.typing.MatLike, cv2.typing.MatLike, SkinDetectionResult]:
        frame = cv2.flip(frame, 1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        hsv_mask = cv2.inRange(hsv, np.array([0, 30, 60]), np.array([25, 180, 255]))
        ycrcb_mask = cv2.inRange(ycrcb, np.array([0, 135, 85]), np.array([255, 180, 135]))
        mask = cv2.bitwise_and(hsv_mask, ycrcb_mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        preview = frame.copy()

        significant_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1800:
                continue
            significant_area += area
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(preview, (x, y), (x + w, y + h), (216, 166, 87), 2)

        total_area = frame.shape[0] * frame.shape[1]
        coverage_ratio = min(significant_area / max(total_area, 1), 1.0)

        if coverage_ratio > 0.18:
            status = "DETECTED"
        elif coverage_ratio > 0.06:
            status = "PARTIAL"
        else:
            status = "SCANNING"

        detail = (
            f"Skin coverage: {coverage_ratio * 100:.1f}% | "
            "Uses HSV + YCrCb thresholds with contour cleanup for stable local detection."
        )
        return preview, mask, SkinDetectionResult(
            coverage_ratio=coverage_ratio,
            status=status,
            detail_text=detail,
        )
