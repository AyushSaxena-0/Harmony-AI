from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


@dataclass(slots=True)
class SkinConcern:
    name: str
    summary: str
    score: float


@dataclass(slots=True)
class SkinAnalysisResult:
    concerns: list[SkinConcern]
    overview: str
    disclaimer: str


class SkinConditionAnalyzer:
    """Non-diagnostic image screener for common visible skin concern categories."""

    def analyze_image(self, image_path: str) -> tuple[Image.Image, SkinAnalysisResult]:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not open the selected image.")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        metrics = self._extract_metrics(rgb, hsv, lab, gray)
        concerns = self._rank_concerns(metrics)
        annotated = self._build_preview(rgb, metrics)

        overview = (
            f"Visible redness {metrics['redness'] * 100:.1f}% | "
            f"texture {metrics['texture'] * 100:.1f}% | "
            f"patchiness {metrics['patchiness'] * 100:.1f}%"
        )
        disclaimer = (
            "This is only a visual skin concern screener, not a medical diagnosis. "
            "Image quality, lighting, and skin tone can change the ranking. "
            "Please use this as a shortlist to discuss with a qualified clinician."
        )
        return Image.fromarray(annotated), SkinAnalysisResult(
            concerns=concerns,
            overview=overview,
            disclaimer=disclaimer,
        )

    def _extract_metrics(self, rgb, hsv, lab, gray) -> dict[str, float]:
        r = rgb[:, :, 0].astype(np.float32)
        g = rgb[:, :, 1].astype(np.float32)
        b = rgb[:, :, 2].astype(np.float32)
        hsv_h = hsv[:, :, 0].astype(np.float32)
        hsv_s = hsv[:, :, 1].astype(np.float32) / 255.0
        hsv_v = hsv[:, :, 2].astype(np.float32) / 255.0
        a_channel = lab[:, :, 1].astype(np.float32)

        redness_map = np.clip((r - (g * 0.6 + b * 0.4)) / 255.0, 0.0, 1.0)
        redness = float(np.mean(redness_map))
        saturation = float(np.mean(hsv_s))
        brightness = float(np.mean(hsv_v))
        warm_hue_ratio = float(np.mean((hsv_h <= 25) | (hsv_h >= 170)))
        patchiness = float(min(np.std(a_channel) / 40.0, 1.0))
        texture = float(min(cv2.Laplacian(gray, cv2.CV_32F).var() / 1800.0, 1.0))
        dry_edge_ratio = float(min(np.mean(cv2.Canny(gray, 80, 160) > 0) * 4.5, 1.0))
        redness_focus = float(min(np.mean(redness_map > 0.22) * 3.5, 1.0))

        return {
            "redness": redness,
            "saturation": saturation,
            "brightness": brightness,
            "warm_hue_ratio": warm_hue_ratio,
            "patchiness": patchiness,
            "texture": texture,
            "dry_edge_ratio": dry_edge_ratio,
            "redness_focus": redness_focus,
        }

    def _rank_concerns(self, metrics: dict[str, float]) -> list[SkinConcern]:
        redness = metrics["redness"]
        saturation = metrics["saturation"]
        patchiness = metrics["patchiness"]
        texture = metrics["texture"]
        dry_edge_ratio = metrics["dry_edge_ratio"]
        brightness = metrics["brightness"]
        redness_focus = metrics["redness_focus"]

        scored = [
            SkinConcern(
                "Allergic Contact Dermatitis",
                "Often appears as a red, irritated, patchy rash after contact with something that triggered the skin.",
                self._clamp(0.38 + redness * 0.9 + patchiness * 0.6 + redness_focus * 0.4),
            ),
            SkinConcern(
                "Eczema / Dermatitis Flare",
                "Commonly linked with dry, inflamed, uneven skin that can look rough or irritated.",
                self._clamp(0.34 + texture * 0.8 + dry_edge_ratio * 0.7 + patchiness * 0.5),
            ),
            SkinConcern(
                "Urticaria / Hives",
                "Usually looks more like raised, blotchy, quickly changing red areas than a dry scaly patch.",
                self._clamp(0.28 + redness * 0.7 + brightness * 0.35 + saturation * 0.45),
            ),
            SkinConcern(
                "Heat Rash / Irritation",
                "Can show as clustered red irritated areas, especially if the image shows diffuse warm redness.",
                self._clamp(0.22 + warm_hue_ratio * 0.5 + saturation * 0.55 + redness * 0.55),
            ),
            SkinConcern(
                "Fungal Rash",
                "Some fungal rashes look patchy with clearer borders, though a photo alone is not enough to tell reliably.",
                self._clamp(0.20 + patchiness * 0.65 + dry_edge_ratio * 0.55 + texture * 0.35),
            ),
            SkinConcern(
                "Psoriasis-like Plaque",
                "Plaque-type eruptions can appear more textured and sharply bordered than a simple irritation.",
                self._clamp(0.16 + texture * 0.7 + dry_edge_ratio * 0.7 + redness_focus * 0.25),
            ),
            SkinConcern(
                "Acne / Follicular Inflammation",
                "This is more likely when the image shows localized inflamed spots rather than one broad rash area.",
                self._clamp(0.14 + redness_focus * 0.55 + saturation * 0.3 + texture * 0.35),
            ),
        ]
        return sorted(scored, key=lambda item: item.score, reverse=True)[:5]

    def _build_preview(self, rgb_image, metrics: dict[str, float]) -> np.ndarray:
        preview = rgb_image.copy()
        height, width = preview.shape[:2]
        overlay_h = 88
        preview[:overlay_h, :, :] = (preview[:overlay_h, :, :] * 0.35).astype(np.uint8)

        lines = [
            "Skin Concern Screener",
            f"Redness: {metrics['redness'] * 100:.1f}%   Patchiness: {metrics['patchiness'] * 100:.1f}%",
            f"Texture: {metrics['texture'] * 100:.1f}%   Dry edges: {metrics['dry_edge_ratio'] * 100:.1f}%",
        ]
        y = 28
        for line in lines:
            cv2.putText(
                preview,
                line,
                (18, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72 if y == 28 else 0.58,
                (241, 226, 199),
                2 if y == 28 else 1,
                cv2.LINE_AA,
            )
            y += 26

        max_dim = max(height, width)
        if max_dim > 1100:
            scale = 1100 / max_dim
            preview = cv2.resize(preview, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return preview

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(0.99, value))

    @staticmethod
    def supported_image(path: str) -> bool:
        return Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
