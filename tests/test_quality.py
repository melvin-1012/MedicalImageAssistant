"""Unit tests for QualityAnalyzer."""
from __future__ import annotations

import cv2
import numpy as np

import config
from cv.quality import QualityAnalyzer
from cv.schemas import ImageQualityResult, QualityLevel


def _make_clean_reference() -> np.ndarray:
    y, x = np.ogrid[:512, :512]
    torso = ((x - 256)**2 / 200**2 + (y - 256)**2 / 230**2) <= 1.0
    lungs = (((x - 180)**2 / 60**2 + (y - 230)**2 / 120**2) <= 1.0) | \
            (((x - 332)**2 / 60**2 + (y - 230)**2 / 120**2) <= 1.0)
    img = np.full((512, 512), 30, dtype=np.uint8)
    img[torso] = 140
    img[lungs] = 55
    for ry in range(140, 380, 45):
        img[(np.abs(y - ry) < 4) & torso] = 190
    return img


def test_quality_ready():
    assert QualityAnalyzer().ready


def test_default_quality_unknown():
    assert ImageQualityResult().level == QualityLevel.UNKNOWN


def test_high_quality_image_classified_good():
    img = _make_clean_reference()
    analyzer = QualityAnalyzer()
    q = analyzer.assess(img)

    assert q.level == QualityLevel.GOOD
    assert q.score >= 0.75
    assert len(q.issues) == 0


def test_each_degradation_lowers_metric_and_score():
    """Verify that every degradation lowers its respective metric and reduces overall score."""
    clean = _make_clean_reference()
    analyzer = QualityAnalyzer()
    clean_q = analyzer.assess(clean)
    assert clean_q.level == QualityLevel.GOOD

    # 1. Blur
    blurred = cv2.GaussianBlur(clean, (25, 25), 9.0)
    blur_q = analyzer.assess(blurred)
    assert blur_q.blur < clean_q.blur
    assert blur_q.score < clean_q.score
    assert any("blurry" in issue.lower() for issue in blur_q.issues)

    # 2. Underexposure (Darken)
    darkened = np.clip(clean.astype(np.float32) * 0.25, 0, 255).astype(np.uint8)
    dark_q = analyzer.assess(darkened)
    assert dark_q.brightness < clean_q.brightness
    assert dark_q.score < clean_q.score
    assert any("underexposed" in issue.lower() for issue in dark_q.issues)

    # 3. Overexposure (Brighten)
    brightened = np.clip(clean.astype(np.float32) * 1.5 + 80, 0, 255).astype(np.uint8)
    bright_q = analyzer.assess(brightened)
    assert bright_q.brightness > clean_q.brightness
    assert bright_q.score < clean_q.score
    assert any("saturation" in issue.lower() or "overexposed" in issue.lower() for issue in bright_q.issues)

    # 4. Low contrast
    low_contrast = np.clip(clean.astype(np.float32) * 0.15 + 100, 0, 255).astype(np.uint8)
    contrast_q = analyzer.assess(low_contrast)
    assert contrast_q.contrast < clean_q.contrast
    assert contrast_q.score < clean_q.score
    assert any("contrast" in issue.lower() for issue in contrast_q.issues)

    # 5. Added noise
    noise_arr = np.random.normal(0, 30.0, clean.shape).astype(np.float32)
    noisy = np.clip(clean.astype(np.float32) + noise_arr, 0, 255).astype(np.uint8)
    noise_q = analyzer.assess(noisy)
    assert noise_q.noise > clean_q.noise
    assert noise_q.score < clean_q.score
    assert any("noise" in issue.lower() for issue in noise_q.issues)

    # 6. Low resolution
    small = cv2.resize(clean, (128, 128))
    res_q = analyzer.assess(small)
    assert res_q.level == QualityLevel.POOR
    assert any("resolution" in issue.lower() for issue in res_q.issues)


def test_level_mapping_boundaries():
    analyzer = QualityAnalyzer()

    # Flat black -> critical override to POOR
    flat_poor = np.zeros((512, 512), dtype=np.uint8)
    q_poor = analyzer.assess(flat_poor)
    assert q_poor.level == QualityLevel.POOR

    # Undersized -> POOR
    small = np.random.randint(50, 200, (100, 100), dtype=np.uint8)
    q_small = analyzer.assess(small)
    assert q_small.level == QualityLevel.POOR
