"""Image quality assessment: blur, exposure, contrast, resolution, and noise."""
from __future__ import annotations

from typing import List, Tuple
import cv2
import numpy as np

import config
from cv.image_loader import scale_to_8bit
from cv.schemas import ImageQualityResult, QualityLevel
from utils.logger import get_logger

logger = get_logger("quality")


def estimate_noise_immerkaer(gray: np.ndarray) -> float:
    """Estimate image noise standard deviation using Immerkaer's method.

    Fast, robust algorithm that zeroes out step edges and linear ramps,
    isolating true high-frequency uncorrelated noise.
    """
    h, w = gray.shape[:2]
    if h < 3 or w < 3:
        return 0.0
    kernel = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], dtype=np.float32)
    resp = cv2.filter2D(gray.astype(np.float32), -1, kernel)
    inner = resp[1:-1, 1:-1]
    sigma = float(np.sum(np.abs(inner)) * np.sqrt(0.5 * np.pi) / (6.0 * (w - 2) * (h - 2)))
    return float(round(sigma, 2))


class QualityAnalyzer:
    """Scores a medical image and classifies it into GOOD / MODERATE / POOR."""

    name = "Quality analyzer"

    def __init__(self, quality_config: config.QualityConfig | None = None) -> None:
        self.config = quality_config or config.QualityConfig()

    @property
    def ready(self) -> bool:
        return True

    def assess(self, image: np.ndarray) -> ImageQualityResult:
        """Compute comprehensive image quality metrics on the ORIGINAL image.

        IMPORTANT: Evaluated strictly on the 8-bit grayscale conversion of the original,
        never on CLAHE or preprocessed arrays.
        """
        if image is None or image.size == 0:
            return ImageQualityResult(
                level=QualityLevel.POOR,
                score=0.0,
                issues=["Image is empty or unreadable"],
            )

        # 1. Convert to 8-bit grayscale without altering the input array
        working = image.copy()
        if working.dtype != np.uint8:
            working = scale_to_8bit(working)

        if working.ndim == 3:
            if working.shape[2] == 3:
                gray = cv2.cvtColor(working, cv2.COLOR_RGB2GRAY)
            elif working.shape[2] == 4:
                gray = cv2.cvtColor(working[:, :, :3], cv2.COLOR_RGB2GRAY)
            else:
                gray = working[:, :, 0]
        else:
            gray = working

        h, w = gray.shape[:2]
        resolution: Tuple[int, int] = (w, h)
        issues: List[str] = []

        # 2. Resolution-invariant blur estimation
        # Resize to fixed reference size (e.g. 512x512) so threshold is resolution-independent
        ref_w, ref_h = self.config.reference_size
        if (w, h) != (ref_w, ref_h):
            ref_gray = cv2.resize(gray, (ref_w, ref_h), interpolation=cv2.INTER_AREA if (w > ref_w) else cv2.INTER_LINEAR)
        else:
            ref_gray = gray

        laplacian_var = float(cv2.Laplacian(ref_gray, cv2.CV_64F).var())

        # 3. Brightness / exposure & pixel clipping
        mean_brightness = float(np.mean(gray))
        clipped_dark = int(np.count_nonzero(gray <= 1))
        clipped_bright = int(np.count_nonzero(gray >= 254))
        clipped_fraction = float((clipped_dark + clipped_bright) / gray.size)

        # 4. Contrast: standard deviation and percentile dynamic range
        contrast_std = float(np.std(gray))
        p2, p98 = np.percentile(gray, [2, 98])
        dynamic_range = float(p98 - p2)

        # 5. Noise estimation (Immerkaer method)
        noise_sigma = estimate_noise_immerkaer(gray)

        # 6. Issue detection against calibrated thresholds
        if laplacian_var < self.config.blur_threshold:
            issues.append(
                f"Image appears blurry (Laplacian variance {laplacian_var:.1f} < threshold {self.config.blur_threshold:.1f})"
            )

        if mean_brightness < self.config.min_brightness:
            issues.append(
                f"Image is underexposed (mean brightness {mean_brightness:.1f} < {self.config.min_brightness:.1f})"
            )
        elif mean_brightness > self.config.max_brightness:
            issues.append(
                f"Image is overexposed (mean brightness {mean_brightness:.1f} > {self.config.max_brightness:.1f})"
            )

        if clipped_fraction > self.config.max_clipped_fraction:
            issues.append(
                f"High pixel clipping / saturation ({clipped_fraction * 100:.1f}% pixels saturated)"
            )

        if contrast_std < self.config.min_contrast:
            issues.append(
                f"Image has low contrast (std {contrast_std:.1f} < {self.config.min_contrast:.1f})"
            )

        min_w, min_h = self.config.min_resolution
        if w < min_w or h < min_h:
            issues.append(
                f"Image resolution ({w}x{h}) is below minimum ({min_w}x{min_h})"
            )

        if noise_sigma > self.config.max_noise:
            issues.append(
                f"Elevated high-frequency noise (sigma {noise_sigma:.1f} > {self.config.max_noise:.1f})"
            )

        # 7. Sub-scores computation (each normalized to 0.0 .. 1.0)
        # Sharpness sub-score
        s_blur = min(1.0, max(0.1, laplacian_var / self.config.blur_threshold))

        # Brightness sub-score: optimal [60, 180]
        if 60.0 <= mean_brightness <= 180.0:
            s_bright = 1.0
        elif mean_brightness < 60.0:
            s_bright = max(0.1, mean_brightness / 60.0)
        else:
            s_bright = max(0.1, 1.0 - (mean_brightness - 180.0) / (255.0 - 180.0))

        # Contrast sub-score: target std >= 35.0
        s_contrast = min(1.0, max(0.1, contrast_std / 35.0))

        # Resolution sub-score: ideal >= 512x512
        s_res = min(1.0, max(0.2, (w * h) / (512 * 512)))

        # Penalties
        clip_penalty = min(0.20, max(0.0, (clipped_fraction - self.config.max_clipped_fraction) * 0.8))
        noise_penalty = min(0.20, max(0.0, (noise_sigma - 12.0) / 30.0)) if noise_sigma > 12.0 else 0.0

        raw_score = (
            0.30 * s_blur
            + 0.25 * s_contrast
            + 0.25 * s_bright
            + 0.20 * s_res
        ) - clip_penalty - noise_penalty

        score = float(np.clip(round(raw_score, 3), 0.0, 1.0))

        # 8. Level classification
        if score >= self.config.good_score and len(issues) == 0:
            level = QualityLevel.GOOD
        elif score >= self.config.moderate_score:
            level = QualityLevel.MODERATE
        else:
            level = QualityLevel.POOR

        # Critical failure overrides to POOR
        if w < min_w or h < min_h or contrast_std < 10.0 or dynamic_range < 20.0:
            level = QualityLevel.POOR

        logger.info(
            "Quality assessment: %s (score %.2f) — blur=%.1f, brightness=%.1f, contrast=%.1f, noise=%.1f",
            level.value,
            score,
            laplacian_var,
            mean_brightness,
            contrast_std,
            noise_sigma,
        )

        return ImageQualityResult(
            level=level,
            score=score,
            blur=round(laplacian_var, 2),
            brightness=round(mean_brightness, 2),
            contrast=round(contrast_std, 2),
            noise=round(noise_sigma, 2),
            resolution=resolution,
            issues=issues,
        )
