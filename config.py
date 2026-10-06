"""Central configuration for the Medical CV engine.

All tunable constants live here so no module hardcodes paths or thresholds.
Values are placeholders until the relevant phase calibrates them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

PROJECT_NAME = "Medical CV Engine"
PROJECT_ID = "HNX26PSI05"

# --- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
SAMPLE_DIR = INPUT_DIR / "sample_images"
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = OUTPUT_DIR / "processed"
OVERLAYS_DIR = OUTPUT_DIR / "overlays"
HEATMAPS_DIR = OUTPUT_DIR / "heatmaps"
MASKS_DIR = OUTPUT_DIR / "masks"
MODELS_DIR = BASE_DIR / "models"

OUTPUT_DIRS: Tuple[Path, ...] = (PROCESSED_DIR, OVERLAYS_DIR, HEATMAPS_DIR, MASKS_DIR)

# --- Logging ---------------------------------------------------------------
LOG_LEVEL = "INFO"

# --- Supported formats -----------------------------------------------------
SUPPORTED_EXTENSIONS: Tuple[str, ...] = (".jpg", ".jpeg", ".png")
FUTURE_EXTENSIONS: Tuple[str, ...] = (".dcm",)  # Phase 1+ (needs pydicom)


@dataclass(frozen=True)
class ValidationConfig:
    min_width: int = 128
    min_height: int = 128
    max_width: int = 10000
    max_height: int = 10000
    allowed_channels: Tuple[int, ...] = (1, 3)
    blank_std_threshold: float = 2.0  # near-zero variance => blank image


@dataclass(frozen=True)
class PreprocessConfig:
    target_size: Tuple[int, int] = (640, 640)  # (width, height) for the model
    keep_aspect_ratio: bool = True
    apply_clahe: bool = True
    clahe_clip_limit: float = 2.0
    clahe_tile_grid: Tuple[int, int] = (8, 8)
    denoise: bool = False
    sharpen: bool = False


@dataclass(frozen=True)
class QualityConfig:
    blur_threshold: float = 100.0       # Laplacian variance (calibrate in Phase 3)
    min_brightness: float = 40.0
    max_brightness: float = 215.0
    min_contrast: float = 25.0
    min_resolution: Tuple[int, int] = (256, 256)
    good_score: float = 0.75
    moderate_score: float = 0.50


@dataclass(frozen=True)
class DetectorConfig:
    model_path: Path = MODELS_DIR / "model.pt"  # placeholder, no model ships
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45


@dataclass(frozen=True)
class AppConfig:
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    preprocess: PreprocessConfig = field(default_factory=PreprocessConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)


CONFIG = AppConfig()
