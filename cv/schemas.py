"""Structured data contracts shared across the pipeline (Phases 1-9).

Arrays (images/masks) live in `LoadedImage` / `PreprocessedImage` and are
never serialised. Everything in `CVAnalysisResult` is JSON-safe and deterministic.
Includes:
- Batch 1 & 2 schemas: ImageMetadata, QualityLevel, ImageQualityResult, BoundingBox, Detection
- Batch 3 schemas: FindingLocation, FindingEvidence (Phase 8), structured CV -> GenAI contract (Phase 9)
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
    extra: Dict[str, Any] = field(default_factory=dict)  # e.g. DICOM tags


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
    """Pixel coordinates in original radiograph space, (x_min, y_min) top-left, (x_max, y_max) bottom-right."""
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
class FindingLocation:
    """Original-radiograph coordinate bounding box (x1, y1, x2, y2)."""
    x1: float
    y1: float
    x2: float
    y2: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "x1": round(float(self.x1), 1),
            "y1": round(float(self.y1), 1),
            "x2": round(float(self.x2), 1),
            "y2": round(float(self.y2), 1),
        }


@dataclass
class FindingEvidence:
    """Phase 8: Evidence-backed finding preserving model confidence and original-space location.

    Strict medical safety:
    - Never uses presumptuous wording ("Pneumonia confirmed").
    - Always preserves genuine CV model confidence.
    - Coordinates are strictly mapped to original radiograph space.
    - Always mandates physician review.
    """
    finding: str = "possible_abnormal_opacity"
    finding_label: str = "Possible abnormal opacity"
    confidence: float = 0.0
    location: FindingLocation = field(default_factory=lambda: FindingLocation(0.0, 0.0, 0.0, 0.0))
    heatmap_available: bool = False
    segmentation_available: bool = False
    requires_physician_review: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding": self.finding,
            "finding_label": self.finding_label,
            "confidence": float(self.confidence),
            "location": self.location.to_dict() if isinstance(self.location, FindingLocation) else self.location,
            "heatmap_available": bool(self.heatmap_available),
            "segmentation_available": bool(self.segmentation_available),
            "requires_physician_review": bool(self.requires_physician_review),
        }


@dataclass
class VisualizationResult:
    overlay_path: Optional[str] = None
    processed_path: Optional[str] = None
    comparison_path: Optional[str] = None
    heatmap_path: Optional[str] = None
    mask_path: Optional[str] = None


@dataclass
class CVAnalysisResult:
    """Primary pipeline analysis result shared across CV, GenAI, and visualization layers."""
    status: AnalysisStatus = AnalysisStatus.NOT_RUN
    metadata: Optional[ImageMetadata] = None
    quality: Optional[ImageQualityResult] = None
    detections: List[Detection] = field(default_factory=list)
    findings: List[FindingEvidence] = field(default_factory=list)
    visualization: Optional[VisualizationResult] = None
    model_loaded: bool = False
    segmentation_status: str = "unavailable"
    segmentation_note: str = (
        "Pixel-level segmentation is unavailable because the RSNA dataset provides "
        "bounding-box annotations, not pixel-level masks."
    )
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_genai_dict(self) -> Dict[str, Any]:
        """Phase 9: Export stable, deterministic structured schema for CV -> GenAI handshake."""
        source_name = self.metadata.path if self.metadata else "unknown"
        width = self.metadata.width if self.metadata else 0
        height = self.metadata.height if self.metadata else 0
        modality = "X-Ray"
        if self.metadata and self.metadata.extra:
            raw_mod = self.metadata.extra.get("modality", "")
            if raw_mod in ("CR", "DX", "RG", "X-Ray"):
                modality = "X-Ray"
            elif raw_mod:
                modality = str(raw_mod)

        quality_status = self.quality.level.value if self.quality else "UNKNOWN"
        quality_score = round(self.quality.score, 2) if self.quality else 0.0
        quality_issues = list(self.quality.issues) if self.quality else []

        if self.status == AnalysisStatus.REJECTED or quality_status == "POOR":
            status_str = "poor_quality"
        elif self.status == AnalysisStatus.ERROR:
            status_str = "error"
        else:
            status_str = "success"

        findings_list = [f.to_dict() for f in self.findings]

        art_original = str(source_name) if source_name != "unknown" else None
        art_processed = None
        art_detections = None
        art_heatmap = None
        art_seg = None
        if self.visualization:
            art_processed = self.visualization.processed_path
            art_detections = self.visualization.overlay_path
            art_heatmap = self.visualization.heatmap_path
            art_seg = self.visualization.mask_path

        return {
            "status": status_str,
            "modality": modality,
            "image": {
                "source": str(source_name),
                "width": int(width),
                "height": int(height),
                "modality": modality,
            },
            "quality": {
                "status": quality_status,
                "score": quality_score,
                "issues": quality_issues,
            },
            "findings": findings_list,
            "artifacts": {
                "original": art_original,
                "processed": art_processed,
                "detections": art_detections,
                "heatmap": art_heatmap,
                "segmentation": art_seg,
            },
            "safety": {
                "physician_review_required": True,
                "no_confirmed_diagnosis": True,
            },
        }

    def to_genai_json(self, indent: int = 2) -> str:
        """Serialize Phase 9 CV -> GenAI handshake schema to deterministic JSON."""
        return json.dumps(self.to_genai_dict(), indent=indent)

    def to_dict(self) -> Dict[str, Any]:
        """Convert complete analysis result to dictionary with structured output included."""
        d = json.loads(json.dumps(asdict(self), default=_enum_default))
        d["structured_output"] = self.to_genai_dict()
        return d

    def to_json(self, indent: int = 2) -> str:
        """Serialize complete analysis result to JSON."""
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
