"""Unit tests for Phase 5 Bounding-Box Localization and Coordinate Restoration."""
from __future__ import annotations

import pytest

from cv.coordinates import ResizeTransform, to_model, to_original
from cv.localization import Localizer
from cv.schemas import BoundingBox, Detection


def test_localizer_ready() -> None:
    localizer = Localizer()
    assert localizer.ready
    assert localizer.name == "Localizer"


def test_localize_coordinate_restoration() -> None:
    # Original image: 1024x1024. Model input: 640x640 letterboxed.
    # Scale = 640 / 1024 = 0.625. pad_x = 0, pad_y = 0.
    transform = ResizeTransform(
        original_size=(1024, 1024),
        model_size=(640, 640),
        scale=0.625,
        pad_x=0,
        pad_y=0,
    )

    # Box in model space: [100, 150, 300, 400]
    model_box = BoundingBox(x_min=100.0, y_min=150.0, x_max=300.0, y_max=400.0)
    det = Detection(label="Possible abnormal opacity", confidence=0.85, bbox=model_box)

    localizer = Localizer()
    localized = localizer.localize([det], transform, original_size=(1024, 1024))

    assert len(localized) == 1
    assert localized[0].label == "Possible abnormal opacity"
    assert localized[0].confidence == 0.85

    restored_box = localized[0].bbox
    assert restored_box is not None
    # 100 / 0.625 = 160.0, 150 / 0.625 = 240.0, 300 / 0.625 = 480.0, 400 / 0.625 = 640.0
    assert pytest.approx(restored_box.x_min, abs=0.1) == 160.0
    assert pytest.approx(restored_box.y_min, abs=0.1) == 240.0
    assert pytest.approx(restored_box.x_max, abs=0.1) == 480.0
    assert pytest.approx(restored_box.y_max, abs=0.1) == 640.0


def test_localize_with_letterbox_padding() -> None:
    # Landscape original image: 1000x500. Model size: 640x640.
    # Scale = 640 / 1000 = 0.64. scaled_h = 500 * 0.64 = 320. pad_y = (640 - 320) // 2 = 160.
    transform = ResizeTransform(
        original_size=(1000, 500),
        model_size=(640, 640),
        scale=0.64,
        pad_x=0,
        pad_y=160,
    )

    # Box in model space located inside active image area:
    # x in [64, 320], y in [160 + 32, 160 + 160] = [192, 320]
    model_box = BoundingBox(x_min=64.0, y_min=192.0, x_max=320.0, y_max=320.0)
    det = Detection(label="Possible abnormal opacity", confidence=0.9, bbox=model_box)

    localizer = Localizer()
    localized = localizer.localize([det], transform, original_size=(1000, 500))

    assert len(localized) == 1
    restored = localized[0].bbox
    assert restored is not None
    # x: 64 / 0.64 = 100.0, 320 / 0.64 = 500.0
    # y: (192 - 160) / 0.64 = 50.0, (320 - 160) / 0.64 = 250.0
    assert pytest.approx(restored.x_min, abs=0.1) == 100.0
    assert pytest.approx(restored.y_min, abs=0.1) == 50.0
    assert pytest.approx(restored.x_max, abs=0.1) == 500.0
    assert pytest.approx(restored.y_max, abs=0.1) == 250.0


def test_localize_boundary_clipping() -> None:
    transform = ResizeTransform.identity((1000, 1000))
    # Box protruding outside image boundary
    out_of_bounds = BoundingBox(x_min=-50.0, y_min=200.0, x_max=1200.0, y_max=800.0)
    det = Detection(label="Possible abnormal opacity", confidence=0.75, bbox=out_of_bounds)

    localizer = Localizer()
    localized = localizer.localize([det], transform, original_size=(1000, 1000))

    assert len(localized) == 1
    clipped = localized[0].bbox
    assert clipped is not None
    assert clipped.x_min == 0.0
    assert clipped.y_min == 200.0
    assert clipped.x_max == 1000.0
    assert clipped.y_max == 800.0


def test_localize_drops_degenerate_boxes() -> None:
    transform = ResizeTransform.identity((500, 500))
    # Box entirely outside image (e.g. x_min=-200, x_max=-100)
    outside_box = BoundingBox(x_min=-200.0, y_min=10.0, x_max=-100.0, y_max=100.0)
    det = Detection(label="Possible abnormal opacity", confidence=0.5, bbox=outside_box)

    localizer = Localizer()
    localized = localizer.localize([det], transform, original_size=(500, 500))
    assert len(localized) == 0


def test_coordinate_roundtrip_precision() -> None:
    transform = ResizeTransform(
        original_size=(1024, 1024),
        model_size=(640, 640),
        scale=640 / 1024,
        pad_x=0,
        pad_y=0,
    )
    orig_box = BoundingBox(x_min=215.3, y_min=180.7, x_max=450.9, y_max=620.4)

    # Forward: original -> model
    model_box = to_model(orig_box, transform)
    # Inverse: model -> original
    restored_box = to_original(model_box, transform)

    # Error must be < 0.1 pixel
    assert abs(orig_box.x_min - restored_box.x_min) < 0.1
    assert abs(orig_box.y_min - restored_box.y_min) < 0.1
    assert abs(orig_box.x_max - restored_box.x_max) < 0.1
    assert abs(orig_box.y_max - restored_box.y_max) < 0.1


def test_localizer_area_and_iou() -> None:
    box1 = BoundingBox(x_min=10.0, y_min=10.0, x_max=110.0, y_max=110.0)  # 100x100 = 10000
    box2 = BoundingBox(x_min=60.0, y_min=10.0, x_max=160.0, y_max=110.0)  # overlap 50x100 = 5000

    assert Localizer.area(box1) == 10000.0
    assert Localizer.area(box2) == 10000.0

    # Union = 10000 + 10000 - 5000 = 15000; IoU = 5000 / 15000 = 1/3
    iou = Localizer.box_iou(box1, box2)
    assert pytest.approx(iou, abs=0.01) == 1.0 / 3.0
