"""Unit tests for ResizeTransform and BoundingBox coordinate mappings."""
from __future__ import annotations

import random
import numpy as np

from cv.coordinates import BoundingBox, ResizeTransform, denormalize, normalize, to_model, to_original


def test_roundtrip_square_image():
    # Square image 1024x1024 -> 640x640 (scale = 640/1024, pad_x=0, pad_y=0)
    transform = ResizeTransform(
        original_size=(1024, 1024),
        model_size=(640, 640),
        scale=640 / 1024,
        pad_x=0,
        pad_y=0,
    )
    for _ in range(20):
        x1 = random.uniform(10, 500)
        y1 = random.uniform(10, 500)
        x2 = x1 + random.uniform(20, 400)
        y2 = y1 + random.uniform(20, 400)
        box = BoundingBox(x1, y1, x2, y2)

        model_b = to_model(box, transform)
        recovered_b = to_original(model_b, transform)

        assert abs(box.x_min - recovered_b.x_min) <= 1.0
        assert abs(box.y_min - recovered_b.y_min) <= 1.0
        assert abs(box.x_max - recovered_b.x_max) <= 1.0
        assert abs(box.y_max - recovered_b.y_max) <= 1.0


def test_roundtrip_landscape_with_vertical_padding():
    # Landscape 1200w x 600h -> 640w x 640h
    # scale = 640 / 1200 = 0.5333, new_h = 320, pad_y = (640 - 320) // 2 = 160
    scale = 640 / 1200
    new_h = int(round(600 * scale))
    pad_y = (640 - new_h) // 2
    transform = ResizeTransform(
        original_size=(1200, 600),
        model_size=(640, 640),
        scale=scale,
        pad_x=0,
        pad_y=pad_y,
    )
    for _ in range(20):
        x1 = random.uniform(10, 600)
        y1 = random.uniform(10, 300)
        x2 = x1 + random.uniform(20, 500)
        y2 = y1 + random.uniform(20, 250)
        box = BoundingBox(x1, y1, x2, y2)

        model_b = to_model(box, transform)
        recovered_b = to_original(model_b, transform)

        assert abs(box.x_min - recovered_b.x_min) <= 1.0
        assert abs(box.y_min - recovered_b.y_min) <= 1.0
        assert abs(box.x_max - recovered_b.x_max) <= 1.0
        assert abs(box.y_max - recovered_b.y_max) <= 1.0


def test_roundtrip_portrait_with_horizontal_padding():
    # Portrait 500w x 1000h -> 640w x 640h
    # scale = 640 / 1000 = 0.64, new_w = 320, pad_x = (640 - 320) // 2 = 160
    scale = 640 / 1000
    new_w = int(round(500 * scale))
    pad_x = (640 - new_w) // 2
    transform = ResizeTransform(
        original_size=(500, 1000),
        model_size=(640, 640),
        scale=scale,
        pad_x=pad_x,
        pad_y=0,
    )
    for _ in range(20):
        x1 = random.uniform(10, 250)
        y1 = random.uniform(10, 500)
        x2 = x1 + random.uniform(20, 200)
        y2 = y1 + random.uniform(20, 450)
        box = BoundingBox(x1, y1, x2, y2)

        model_b = to_model(box, transform)
        recovered_b = to_original(model_b, transform)

        assert abs(box.x_min - recovered_b.x_min) <= 1.0
        assert abs(box.y_min - recovered_b.y_min) <= 1.0
        assert abs(box.x_max - recovered_b.x_max) <= 1.0
        assert abs(box.y_max - recovered_b.y_max) <= 1.0


def test_normalize_and_denormalize():
    size = (1024, 768)
    box = BoundingBox(x_min=100.0, y_min=200.0, x_max=600.0, y_max=500.0)

    norm = normalize(box, size)
    assert 0.0 <= norm.x_min <= 1.0
    assert 0.0 <= norm.y_min <= 1.0
    assert 0.0 <= norm.x_max <= 1.0
    assert 0.0 <= norm.y_max <= 1.0

    denorm = denormalize(norm, size)
    assert abs(denorm.x_min - box.x_min) <= 1.0
    assert abs(denorm.y_min - box.y_min) <= 1.0
    assert abs(denorm.x_max - box.x_max) <= 1.0
    assert abs(denorm.y_max - box.y_max) <= 1.0
