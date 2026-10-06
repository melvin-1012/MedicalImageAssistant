"""Structured data contracts shared across the pipeline.

Arrays (images/masks) live in `LoadedImage` / `PreprocessedImage` and are
never serialised. Everything in `CVAnalysisResult` is JSON-safe.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class QualityLevel(str, Enum):
    GOOD = "GOOD"
    MODERATE = "MODERATE"
    POOR = "POOR"
    UNKNOWN = "UNKNOWN"


class AnalysisStatus(str, Enum):
    OK = "ok"
    REJECTED = "rejected"
    ERROR = "error"
    NOT_RUN = "not_run"


@dataclass
class ImageMetadata:
    path: str
    format: str
    width: int
    height: int
    channels: int
    dtype: str = "uint8"
    file_size_bytes: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)  # e.g. DICOM tags later


@dataclass
class ValidationResult:
    is_valid: bool
    reasons: List[str] = field(default_factory=list)


@dataclass
class ImageQualityResult:
    level: QualityLevel = QualityLevel.UNKNOWN
    score: float = 0.0  # 0..1
    blur: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    noise: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    issues: List[str] = field(default_factory=list)


@dataclass
class BoundingBox:
    """Pixel coordinates, (x_min, y_min) top-left, (x_max, y_max) bottom-right."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class Detection:
    label: str
    confidence: float
    bbox: Optional[BoundingBox] = None
    heatmap_path: Optional[str] = None
    mask_path: Optional[str] = None


@dataclass
class VisualizationResult:
    overlay_path: Optional[str] = None
    processed_path: Optional[str] = None
    comparison_path: Optional[str] = None
    heatmap_path: Optional[str] = None
    mask_path: Optional[str] = None


@dataclass
class CVAnalysisResult:
    status: AnalysisStatus = AnalysisStatus.NOT_RUN
    metadata: Optional[ImageMetadata] = None
    quality: Optional[ImageQualityResult] = None
    detections: List[Detection] = field(default_factory=list)
    visualization: Optional[VisualizationResult] = None
    model_loaded: bool = False
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return json.loads(json.dumps(asdict(self), default=_enum_default))

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# --- In-memory containers (not serialised) ---------------------------------
@dataclass
class LoadedImage:
    image: np.ndarray
    metadata: ImageMetadata


@dataclass
class PreprocessedImage:
    image: np.ndarray            # display-safe uint8 copy
    transform: "ResizeTransform"  # type: ignore[name-defined]  # noqa: F821
    steps: List[str] = field(default_factory=list)
    model_input: Optional[np.ndarray] = None  # normalized float32 [0, 1] array



def _enum_default(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Not JSON serialisable: {type(obj)}")
