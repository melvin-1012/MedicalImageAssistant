"""Unit tests for ImageValidator."""
from __future__ import annotations

import numpy as np

from config import ValidationConfig
from cv.schemas import ImageMetadata, LoadedImage
from cv.validator import ImageValidator


def _make_loaded(image: np.ndarray, channels: int = 1) -> LoadedImage:
    h = int(image.shape[0]) if image.ndim >= 1 and image.shape[0] > 0 else 0
    w = int(image.shape[1]) if image.ndim >= 2 else 0
    meta = ImageMetadata(
        path="dummy.dcm",
        format="dcm",
        width=w,
        height=h,
        channels=channels,
        dtype="uint8",
    )
    return LoadedImage(image=image, metadata=meta)



def test_validator_ready():
    assert ImageValidator().ready


def test_valid_image_passes():
    # Normal image with variance and valid dimensions
    arr = (np.random.rand(512, 512) * 200 + 20).astype(np.uint8)
    loaded = _make_loaded(arr)
    validator = ImageValidator()
    result = validator.validate(loaded)

    assert result.is_valid is True
    assert len(result.reasons) == 0


def test_undersized_image_rejected():
    arr = (np.random.rand(64, 64) * 255).astype(np.uint8)
    loaded = _make_loaded(arr)
    validator = ImageValidator(ValidationConfig(min_width=128, min_height=128))
    result = validator.validate(loaded)

    assert result.is_valid is False
    assert any("below minimum" in r for r in result.reasons)


def test_oversized_image_rejected():
    arr = (np.random.rand(200, 200) * 255).astype(np.uint8)
    loaded = _make_loaded(arr)
    validator = ImageValidator(ValidationConfig(max_width=150, max_height=150))
    result = validator.validate(loaded)

    assert result.is_valid is False
    assert any("exceeds maximum" in r for r in result.reasons)


def test_invalid_channels_rejected():
    # 4 channels RGBA
    arr = np.zeros((200, 200, 4), dtype=np.uint8)
    arr[:, :, 0] = 50
    loaded = _make_loaded(arr, channels=4)
    validator = ImageValidator()
    result = validator.validate(loaded)

    assert result.is_valid is False
    assert any("channels" in r for r in result.reasons)


def test_blank_flat_image_rejected():
    # Flat image with zero standard deviation
    arr = np.full((512, 512), 128, dtype=np.uint8)
    loaded = _make_loaded(arr)
    validator = ImageValidator(ValidationConfig(blank_std_threshold=2.0))
    result = validator.validate(loaded)

    assert result.is_valid is False
    assert any("blank" in r for r in result.reasons)


def test_empty_image_rejected():
    arr = np.array([], dtype=np.uint8)
    loaded = _make_loaded(arr)
    validator = ImageValidator()
    result = validator.validate(loaded)

    assert result.is_valid is False
    assert any("empty or unreadable" in r for r in result.reasons)


def test_empty_file_rejected_via_path(tmp_path):
    empty_file = tmp_path / "zero.png"
    empty_file.write_bytes(b"")

    validator = ImageValidator()
    result = validator.validate_path(empty_file)
    assert result.is_valid is False
    assert any("empty (0 bytes)" in r for r in result.reasons)


def test_saturated_black_and_white_rejected():
    # 99% saturated black pixels
    arr = np.zeros((200, 200), dtype=np.uint8)
    arr[0, :40] = 100  # small non-zero portion

    validator = ImageValidator()
    result = validator.validate(_make_loaded(arr))
    assert result.is_valid is False
    assert any("saturated black" in r for r in result.reasons)


def test_multiple_simultaneous_failures_reported_together():
    # Image that is: too small (<128) AND flat/blank (std=0) AND invalid channels (4)
    bad_arr = np.full((50, 50, 4), 100, dtype=np.uint8)
    loaded = _make_loaded(bad_arr, channels=4)

    validator = ImageValidator()
    result = validator.validate(loaded)

    assert result.is_valid is False
    # All 3 failure reasons must be collected simultaneously
    assert len(result.reasons) >= 3
    assert any("below minimum" in r for r in result.reasons)
    assert any("channels" in r for r in result.reasons)
    assert any("blank" in r for r in result.reasons)

