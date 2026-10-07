"""Input validation: file existence, decodability, dimensions, channels, and blank/saturation checks."""
from __future__ import annotations

from pathlib import Path
from typing import List, Union

import numpy as np

import config
from cv.schemas import LoadedImage, ValidationResult
from utils.logger import get_logger

logger = get_logger("validator")


class ImageValidator:
    """Rejects unusable inputs before any processing by collecting all failure reasons."""

    name = "Validator"

    def __init__(self, validation_config: config.ValidationConfig | None = None) -> None:
        self.config = validation_config or config.ValidationConfig()

    @property
    def ready(self) -> bool:
        return True

    def validate_path(self, path: Path | str) -> ValidationResult:
        """Validate input path before loading."""
        p = Path(path)
        reasons: List[str] = []

        if not p.exists():
            reasons.append(f"File does not exist: {p.name}")
            return ValidationResult(is_valid=False, reasons=reasons)

        if not p.is_file():
            reasons.append(f"Path is not a regular file: {p.name}")

        suffix = p.suffix.lower()
        if suffix not in config.SUPPORTED_EXTENSIONS:
            reasons.append(
                f"Unsupported file format '{suffix}'. Supported formats: {', '.join(config.SUPPORTED_EXTENSIONS)}"
            )

        if p.exists() and p.stat().st_size == 0:
            reasons.append("File is empty (0 bytes)")

        return ValidationResult(is_valid=len(reasons) == 0, reasons=reasons)

    def validate(self, input_target: Union[LoadedImage, np.ndarray, Path, str]) -> ValidationResult:
        """Validate loaded image or path against all operational constraints."""
        reasons: List[str] = []

        # If a path was provided directly, run path checks first
        if isinstance(input_target, (str, Path)):
            return self.validate_path(input_target)

        if isinstance(input_target, LoadedImage):
            img = input_target.image
        elif isinstance(input_target, np.ndarray):
            img = input_target
        else:
            reasons.append(f"Unsupported validation target type: {type(input_target)}")
            return ValidationResult(is_valid=False, reasons=reasons)

        # 1. Image decodability / empty array check
        if img is None or img.size == 0:
            reasons.append("Image array is empty or unreadable")
            return ValidationResult(is_valid=False, reasons=reasons)

        # 2. Dimensions check (min and max constraints)
        h = int(img.shape[0]) if img.ndim >= 1 else 0
        w = int(img.shape[1]) if img.ndim >= 2 else 0

        if w < self.config.min_width:
            reasons.append(f"Image width ({w}px) below minimum ({self.config.min_width}px)")
        elif w > self.config.max_width:
            reasons.append(f"Image width ({w}px) exceeds maximum ({self.config.max_width}px)")

        if h < self.config.min_height:
            reasons.append(f"Image height ({h}px) below minimum ({self.config.min_height}px)")
        elif h > self.config.max_height:
            reasons.append(f"Image height ({h}px) exceeds maximum ({self.config.max_height}px)")

        # 3. Channels check
        channels = 1 if img.ndim == 2 else img.shape[2]
        if channels not in self.config.allowed_channels:
            reasons.append(f"Image channels ({channels}) not allowed ({self.config.allowed_channels})")

        # 4. Blank or near-constant image check (standard deviation threshold)
        std_val = float(np.std(img))
        if std_val < self.config.blank_std_threshold:
            reasons.append(
                f"Image appears blank (pixel std {std_val:.2f} < threshold {self.config.blank_std_threshold:.2f})"
            )

        # 5. Saturation check: almost entirely saturated black or white
        # Evaluated on 8-bit equivalent to ensure standard dynamic range assessment
        if img.size > 0:
            if img.dtype != np.uint8:
                # normalize temporarily for saturation check
                min_v, max_v = float(np.min(img)), float(np.max(img))
                if max_v > min_v:
                    check_arr = ((img.astype(np.float32) - min_v) / (max_v - min_v) * 255.0).astype(np.uint8)
                else:
                    check_arr = np.zeros(img.shape, dtype=np.uint8)
            else:
                check_arr = img

            saturated_black = np.count_nonzero(check_arr <= 1)
            saturated_white = np.count_nonzero(check_arr >= 254)
            total_pixels = check_arr.size
            black_frac = saturated_black / total_pixels
            white_frac = saturated_white / total_pixels

            if black_frac >= self.config.max_saturation_fraction:
                reasons.append(
                    f"Image is almost entirely saturated black ({black_frac * 100:.1f}% pixels <= 1)"
                )
            elif white_frac >= self.config.max_saturation_fraction:
                reasons.append(
                    f"Image is almost entirely saturated white ({white_frac * 100:.1f}% pixels >= 254)"
                )

        is_valid = len(reasons) == 0
        if not is_valid:
            logger.warning("Image validation rejected: %s", "; ".join(reasons))
        else:
            logger.info("Image validation passed (%dx%d, %d channels)", w, h, channels)

        return ValidationResult(is_valid=is_valid, reasons=reasons)
