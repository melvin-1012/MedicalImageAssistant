"""OpenCV preprocessing. Never mutates the original image."""
from __future__ import annotations

from typing import List, Tuple
import cv2
import numpy as np

from config import PreprocessConfig
from cv.coordinates import ResizeTransform
from cv.image_loader import scale_to_8bit
from cv.schemas import PreprocessedImage
from utils.logger import get_logger

logger = get_logger("preprocessor")


class Preprocessor:
    """Grayscale conversion, aspect-preserving letterboxing, CLAHE, denoising, and normalization."""

    name = "Preprocessor"

    def __init__(self, preprocess_config: PreprocessConfig | None = None) -> None:
        self.config = preprocess_config or PreprocessConfig()

    @property
    def ready(self) -> bool:
        return True

    def to_8bit_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert any image (16-bit, multi-channel RGB) to 8-bit single-channel grayscale."""
        if image is None or image.size == 0:
            raise ValueError("Cannot convert empty image to grayscale")

        working = image.copy()
        # Scale multi-bit (e.g. 16-bit) to 8-bit
        if working.dtype != np.uint8:
            working = scale_to_8bit(working)

        # Convert multi-channel to grayscale
        if working.ndim == 3:
            if working.shape[2] == 3:
                working = cv2.cvtColor(working, cv2.COLOR_RGB2GRAY)
            elif working.shape[2] == 4:
                working = cv2.cvtColor(working[:, :, :3], cv2.COLOR_RGB2GRAY)
            elif working.shape[2] == 1:
                working = working.squeeze(axis=2)

        return working

    def letterbox_resize(
        self,
        img: np.ndarray,
        target_size: Tuple[int, int],
        pad_value: int | None = None,
    ) -> Tuple[np.ndarray, ResizeTransform]:
        """Generic aspect-preserving resize with centered border padding.

        Args:
            img: 2D or 3D numpy array.
            target_size: (target_width, target_height).
            pad_value: constant value for padding border (default from config: 0 / black).

        Returns:
            Tuple of (padded_image, ResizeTransform)
        """
        if pad_value is None:
            pad_value = self.config.letterbox_pad_value

        orig_h, orig_w = img.shape[:2]
        target_w, target_h = target_size

        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = max(1, int(round(orig_w * scale)))
        new_h = max(1, int(round(orig_h * scale)))

        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        pad_x = (target_w - new_w) // 2
        pad_y = (target_h - new_h) // 2

        if img.ndim == 2:
            canvas = np.full((target_h, target_w), pad_value, dtype=img.dtype)
            canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized
        else:
            canvas = np.full((target_h, target_w, img.shape[2]), pad_value, dtype=img.dtype)
            canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w, :] = resized

        transform = ResizeTransform(
            original_size=(orig_w, orig_h),
            model_size=(target_w, target_h),
            scale=scale,
            pad_x=pad_x,
            pad_y=pad_y,
        )
        return canvas, transform

    def apply_clahe(
        self,
        img: np.ndarray,
        clip_limit: float | None = None,
        tile_grid: Tuple[int, int] | None = None,
    ) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization."""
        clip = clip_limit if clip_limit is not None else self.config.clahe_clip_limit
        grid = tile_grid if tile_grid is not None else self.config.clahe_tile_grid
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=grid)
        return clahe.apply(img)

    def denoise(self, img: np.ndarray) -> np.ndarray:
        """Apply noise reduction (fastNlMeans for uint8 or Gaussian smoothing)."""
        if img.dtype == np.uint8 and img.ndim == 2:
            return cv2.fastNlMeansDenoising(img, None, h=10, templateWindowSize=7, searchWindowSize=21)
        return cv2.GaussianBlur(img, (3, 3), 0)

    def sharpen(self, img: np.ndarray) -> np.ndarray:
        """Sharpen image using unsharp masking."""
        blurred = cv2.GaussianBlur(img, (0, 0), 3)
        return cv2.addWeighted(img, 1.5, blurred, -0.5, 0)

    def normalize(self, img: np.ndarray) -> np.ndarray:
        """Produce normalized model-ready float32 array in range [0.0, 1.0]."""
        return (img.astype(np.float32) / 255.0).clip(0.0, 1.0)

    def preprocess(self, image: np.ndarray) -> PreprocessedImage:
        """Execute complete modular preprocessing pipeline on an image copy."""
        if image is None or image.size == 0:
            raise ValueError("Cannot preprocess empty image")

        # NON-NEGOTIABLE RULE: Original image is NEVER modified
        working = image.copy()
        steps: List[str] = []

        # 1. Convert to 8-bit single-channel grayscale
        working = self.to_8bit_grayscale(working)
        steps.append("to_8bit_grayscale")

        # 2. Aspect-ratio-preserving letterbox resize
        if self.config.keep_aspect_ratio:
            working, transform = self.letterbox_resize(
                working, self.config.target_size, self.config.letterbox_pad_value
            )
            steps.append(
                f"letterbox_resize(target={self.config.target_size}, scale={transform.scale:.4f}, pad=({transform.pad_x},{transform.pad_y}))"
            )
        else:
            orig_h, orig_w = working.shape[:2]
            target_w, target_h = self.config.target_size
            working = cv2.resize(working, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            transform = ResizeTransform(
                original_size=(orig_w, orig_h),
                model_size=(target_w, target_h),
                scale=target_w / orig_w,
                pad_x=0,
                pad_y=0,
            )
            steps.append(f"direct_resize(target={self.config.target_size})")

        # 3. CLAHE contrast enhancement
        if self.config.apply_clahe:
            working = self.apply_clahe(working)
            steps.append(
                f"clahe(clip={self.config.clahe_clip_limit}, grid={self.config.clahe_tile_grid})"
            )

        # 4. Optional denoising
        if self.config.denoise:
            working = self.denoise(working)
            steps.append("denoise")

        # 5. Optional sharpening
        if self.config.sharpen:
            working = self.sharpen(working)
            steps.append("sharpen")

        # Display-safe copy is uint8
        display_image = working.copy()

        # 6. Model-ready normalized float32 array [0, 1]
        model_input = None
        if self.config.normalize_float:
            model_input = self.normalize(working)
            steps.append("normalize_float32[0,1]")

        logger.info(
            "Preprocessed image %s -> %s via: %s",
            transform.original_size,
            transform.model_size,
            ", ".join(steps),
        )
        return PreprocessedImage(
            image=display_image,
            transform=transform,
            steps=steps,
            model_input=model_input,
        )
