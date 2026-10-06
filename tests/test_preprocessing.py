"""Unit tests for Preprocessor and aspect-preserving letterboxing."""
from __future__ import annotations

import numpy as np

from config import PreprocessConfig
from cv.coordinates import BoundingBox, ResizeTransform, to_model, to_original
from cv.preprocessing import Preprocessor


def test_preprocessor_ready():
    assert Preprocessor().ready


def test_identity_transform():
    t = ResizeTransform.identity((100, 80))
    assert t.original_size == t.model_size == (100, 80)
    assert t.scale == 1.0
    assert t.pad_x == 0
    assert t.pad_y == 0


def test_original_image_never_mutated():
    """Rule: Preprocessing must never alter the original image in memory."""
    orig = np.full((512, 512), 100, dtype=np.uint8)
    orig_copy = orig.copy()

    preprocessor = Preprocessor()
    preprocessed = preprocessor.preprocess(orig)

    assert np.array_equal(orig, orig_copy)
    assert preprocessed.image is not orig


def test_letterbox_square_input():
    preprocessor = Preprocessor(PreprocessConfig(target_size=(640, 640)))
    img = np.full((1024, 1024), 120, dtype=np.uint8)
    prepped = preprocessor.preprocess(img)

    assert prepped.image.shape == (640, 640)
    assert prepped.transform.original_size == (1024, 1024)
    assert prepped.transform.model_size == (640, 640)
    assert prepped.transform.pad_x == 0
    assert prepped.transform.pad_y == 0
    assert np.isclose(prepped.transform.scale, 640 / 1024)


def test_letterbox_generic_non_square_wide():
    """Requirement 6: Preprocessing must handle non-square inputs generically."""
    # Wide image (width > height): 1000w x 500h -> 640w x 640h
    preprocessor = Preprocessor(PreprocessConfig(target_size=(640, 640)))
    img = np.full((500, 1000), 80, dtype=np.uint8)
    prepped = preprocessor.preprocess(img)

    assert prepped.image.shape == (640, 640)
    t = prepped.transform
    assert t.original_size == (1000, 500)
    assert t.scale == 640 / 1000
    assert t.pad_x == 0
    assert t.pad_y == (640 - int(round(500 * (640 / 1000)))) // 2

    # Verify coordinates round-trip
    orig_box = BoundingBox(x_min=100.0, y_min=50.0, x_max=500.0, y_max=400.0)
    model_box = to_model(orig_box, t)
    recovered_box = to_original(model_box, t)

    assert np.isclose(orig_box.x_min, recovered_box.x_min, atol=1e-3)
    assert np.isclose(orig_box.y_min, recovered_box.y_min, atol=1e-3)
    assert np.isclose(orig_box.x_max, recovered_box.x_max, atol=1e-3)
    assert np.isclose(orig_box.y_max, recovered_box.y_max, atol=1e-3)


def test_letterbox_generic_non_square_tall():
    # Tall image (height > width): 400w x 800h -> 640w x 640h
    preprocessor = Preprocessor(PreprocessConfig(target_size=(640, 640)))
    img = np.full((800, 400), 80, dtype=np.uint8)
    prepped = preprocessor.preprocess(img)

    assert prepped.image.shape == (640, 640)
    t = prepped.transform
    assert t.original_size == (400, 800)
    assert t.scale == 640 / 800
    assert t.pad_y == 0
    assert t.pad_x == (640 - int(round(400 * (640 / 800)))) // 2


def test_bgr_to_grayscale_conversion():
    # 3-channel input
    color_img = np.zeros((300, 300, 3), dtype=np.uint8)
    color_img[:, :, 0] = 50
    color_img[:, :, 1] = 100
    color_img[:, :, 2] = 150

    preprocessor = Preprocessor()
    prepped = preprocessor.preprocess(color_img)
    assert prepped.image.ndim == 2
    assert "to_8bit_grayscale" in prepped.steps


def test_clahe_enhances_contrast():
    # Low-contrast image with subtle structure
    img = np.full((512, 512), 100, dtype=np.uint8)
    img[150:350, 150:350] = 115

    p_with_clahe = Preprocessor(PreprocessConfig(apply_clahe=True))
    p_no_clahe = Preprocessor(PreprocessConfig(apply_clahe=False))

    res_clahe = p_with_clahe.preprocess(img)
    res_no_clahe = p_no_clahe.preprocess(img)

    # CLAHE must alter the image and increase local contrast/variance
    assert not np.array_equal(res_clahe.image, res_no_clahe.image)
    assert np.std(res_clahe.image) > np.std(res_no_clahe.image)



def test_toggles_work():
    img = np.full((300, 300), 100, dtype=np.uint8)
    # Enable denoise and sharpen, disable CLAHE
    custom_cfg = PreprocessConfig(apply_clahe=False, denoise=True, sharpen=True)
    preprocessor = Preprocessor(custom_cfg)
    prepped = preprocessor.preprocess(img)

    assert "denoise" in prepped.steps
    assert "sharpen" in prepped.steps
    assert not any("clahe" in s for s in prepped.steps)


def test_both_outputs_display_uint8_and_model_float32():
    img = np.full((512, 512), 120, dtype=np.uint8)
    preprocessor = Preprocessor(PreprocessConfig(normalize_float=True))
    prepped = preprocessor.preprocess(img)

    # 1. Display output: uint8 in [0, 255]
    assert prepped.image.dtype == np.uint8
    assert 0 <= prepped.image.min() <= prepped.image.max() <= 255

    # 2. Model input: float32 in [0.0, 1.0]
    assert prepped.model_input is not None
    assert prepped.model_input.dtype == np.float32
    assert 0.0 <= prepped.model_input.min() <= prepped.model_input.max() <= 1.0

