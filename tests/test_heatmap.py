"""Unit tests for Phase 6 Heatmap and Model-Grounded Explainability."""
from __future__ import annotations

import numpy as np
import pytest

from cv.coordinates import ResizeTransform
from cv.heatmap import (
    BaseHeatmapGenerator,
    ModelHeatmapGenerator,
    NullHeatmapGenerator,
)
from cv.schemas import BoundingBox, Detection


def test_null_heatmap_generator() -> None:
    gen = NullHeatmapGenerator()
    assert not gen.is_available
    dummy_img = np.zeros((640, 640), dtype=np.uint8)
    assert gen.generate(dummy_img) is None


def test_model_heatmap_generator_no_detections() -> None:
    gen = ModelHeatmapGenerator(is_available=True)
    assert gen.is_available
    dummy_img = np.zeros((640, 640), dtype=np.uint8)
    # Zero detections -> must return None (never fabricate artificial heatmaps)
    assert gen.generate(dummy_img, detections=[]) is None


def test_model_heatmap_generator_with_detections() -> None:
    gen = ModelHeatmapGenerator(is_available=True)
    dummy_img = np.zeros((640, 640), dtype=np.uint8)

    det = Detection(
        label="Possible abnormal opacity",
        confidence=0.88,
        bbox=BoundingBox(x_min=100.0, y_min=100.0, x_max=300.0, y_max=300.0),
    )

    heatmap = gen.generate(dummy_img, detections=[det])
    assert heatmap is not None
    assert heatmap.shape == (640, 640)
    assert heatmap.dtype == np.float32

    # Peak activation must be normalized to 1.0 and located inside the detection region
    assert np.max(heatmap) == 1.0
    center_val = heatmap[200, 200]
    corner_val = heatmap[0, 0]
    assert center_val > 0.8
    assert corner_val == 0.0


def test_heatmap_align_to_original() -> None:
    # Model size: 640x640 with letterbox padding
    # Original: 1000x500 (landscape). Scale = 0.64. scaled_h = 320. pad_y = 160.
    transform = ResizeTransform(
        original_size=(1000, 500),
        model_size=(640, 640),
        scale=0.64,
        pad_x=0,
        pad_y=160,
    )

    # Synthetic heatmap with active area strictly inside valid image area
    model_heatmap = np.zeros((640, 640), dtype=np.float32)
    model_heatmap[160:480, 0:640] = 0.5
    model_heatmap[320, 320] = 1.0

    aligned = BaseHeatmapGenerator.align_to_original(
        model_heatmap, transform, original_size=(1000, 500)
    )

    # Must match original image dimensions (height=500, width=1000)
    assert aligned.shape == (500, 1000)
    assert aligned.dtype == np.float32
    assert 0.0 <= np.min(aligned) <= np.max(aligned) <= 1.0
    # Peak at center
    assert aligned[250, 500] == 1.0


def test_heatmap_create_overlay() -> None:
    orig = np.full((512, 512), 128, dtype=np.uint8)
    heatmap = np.zeros((512, 512), dtype=np.float32)
    heatmap[200:300, 200:300] = 1.0

    overlay = BaseHeatmapGenerator.create_overlay(orig, heatmap, alpha=0.4)

    assert overlay.shape == (512, 512, 3)
    assert overlay.dtype == np.uint8
    # Background (near-zero activation) remains unmodified grayscale in RGB
    bg_pixel = overlay[10, 10]
    assert bg_pixel[0] == bg_pixel[1] == bg_pixel[2] == 128
    # Activated region has color modulation
    act_pixel = overlay[250, 250]
    assert act_pixel[0] != act_pixel[2]
