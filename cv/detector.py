"""Model-agnostic detector interface and medical detector implementations.

The pipeline depends on `BaseDetector` / `MedicalDetector`.
YOLO is implemented as one concrete subclass; swapping to another architecture
(e.g., Faster R-CNN, Torchvision) requires no changes to image preprocessing or pipeline stages.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

import config
from cv.schemas import BoundingBox, Detection
from utils.logger import get_logger

logger = get_logger("detector")


class ModelNotLoadedError(RuntimeError):
    """Raised when inference is requested without a loaded model."""


class BaseDetector(ABC):
    """Core detector interface depended upon by the pipeline."""
    name = "Detector interface"

    @property
    @abstractmethod
    def is_loaded(self) -> bool: ...

    @property
    def ready(self) -> bool:
        return True  # interface is usable even without a model

    @abstractmethod
    def load_model(self) -> None: ...

    @abstractmethod
    def predict(self, image: np.ndarray) -> List[Detection]:
        """Run inference on a preprocessed image (model coordinates)."""


class MedicalDetector(BaseDetector):
    """Abstract medical abnormality detector interface.

    Extends BaseDetector with metadata query and training capabilities,
    decoupling specific frameworks (Ultralytics, PyTorch) from the pipeline.
    """
    name = "Medical Detector"

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata (architecture, version, target classes, device)."""

    def train(self, dataset_config: Any, **kwargs: Any) -> Any:
        """Train or fine-tune detector on a medical dataset."""
        raise NotImplementedError("Training must be implemented by concrete detector.")


class NullDetector(MedicalDetector):
    """Placeholder used when no trained model exists."""

    @property
    def is_loaded(self) -> bool:
        return False

    def load_model(self) -> None:
        raise ModelNotLoadedError("No model available. Train or load weights in Phase 4.")

    def predict(self, image: np.ndarray) -> List[Detection]:
        raise ModelNotLoadedError("No medical model loaded.")

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": "NullDetector",
            "is_loaded": False,
            "architecture": None,
            "weights_path": None,
        }


class YOLOMedicalDetector(MedicalDetector):
    """YOLO implementation of MedicalDetector using the Ultralytics framework.

    Standard target label is clinically non-presumptive: 'Possible abnormal opacity'.
    """
    name = "YOLO Medical Detector"
    DEFAULT_TARGET_LABEL = "Possible abnormal opacity"

    def __init__(
        self,
        model_path: Optional[Path | str] = None,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        device: Optional[str] = None,
        target_label: str = DEFAULT_TARGET_LABEL,
    ) -> None:
        self.model_path = Path(model_path) if model_path else config.CONFIG.detector.model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.target_label = target_label
        self._model: Any = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def _resolve_device(self) -> str:
        """Detect CUDA GPU or fallback to CPU."""
        if self.device:
            return self.device
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def load_model(self, weights_path: Optional[Path | str] = None) -> None:
        """Load trained YOLO weights.

        Raises:
            ModelNotLoadedError: If ultralytics is not installed.
            FileNotFoundError: If weights file does not exist.
        """
        path_to_load = Path(weights_path) if weights_path else self.model_path
        if not path_to_load.exists():
            raise FileNotFoundError(f"Model weights file not found: {path_to_load.resolve()}")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ModelNotLoadedError(
                "The 'ultralytics' package is required for YOLO model loading. "
                "Install it with: pip install ultralytics"
            ) from exc

        device_to_use = self._resolve_device()
        logger.info("Loading YOLO weights from %s on device=%s", path_to_load, device_to_use)
        self._model = YOLO(str(path_to_load))
        self.model_path = path_to_load
        self.device = device_to_use

    def predict(self, image: np.ndarray) -> List[Detection]:
        """Run object detection on a preprocessed image array.

        Returns list of standardized Detection objects with BoundingBox in model coordinates.
        Returns empty list if no abnormalities are detected above confidence threshold.
        """
        if not self.is_loaded:
            raise ModelNotLoadedError("No medical model loaded. Call load_model() first.")

        if image is None or image.size == 0:
            raise ValueError("Input image array is empty or None")

        results = self._model.predict(
            image,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            device=self.device or self._resolve_device(),
            verbose=False,
        )

        detections: List[Detection] = []
        if not results:
            return detections

        first_res = results[0]
        if first_res.boxes is None or len(first_res.boxes) == 0:
            return detections

        for box in first_res.boxes:
            coords = box.xyxy[0].tolist() if hasattr(box.xyxy[0], "tolist") else list(box.xyxy[0])
            conf_val = float(box.conf[0]) if hasattr(box.conf[0], "__float__") else float(box.conf)

            x_min, y_min, x_max, y_max = coords[:4]
            detections.append(
                Detection(
                    label=self.target_label,
                    confidence=round(conf_val, 4),
                    bbox=BoundingBox(
                        x_min=float(x_min),
                        y_min=float(y_min),
                        x_max=float(x_max),
                        y_max=float(y_max),
                    ),
                )
            )

        return detections

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata dictionary."""
        return {
            "name": self.name,
            "architecture": "YOLO",
            "is_loaded": self.is_loaded,
            "model_path": str(self.model_path) if self.model_path else None,
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold,
            "device": self.device or self._resolve_device(),
            "target_label": self.target_label,
        }

    def train(
        self,
        data_yaml: Path | str,
        epochs: int = 50,
        batch_size: int = 16,
        imgsz: int = 640,
        output_dir: Optional[Path | str] = None,
        **kwargs: Any,
    ) -> Any:
        """Fine-tune YOLO on prepared dataset YAML."""
        data_path = Path(data_yaml)
        if not data_path.exists():
            raise FileNotFoundError(f"Dataset config YAML not found: {data_path.resolve()}")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ModelNotLoadedError("ultralytics package required for training") from exc

        base_model = self.model_path if (self.model_path and self.model_path.exists()) else "yolo11n.pt"
        yolo = YOLO(str(base_model))
        device_to_use = self._resolve_device()

        train_args = {
            "data": str(data_path),
            "epochs": epochs,
            "batch": batch_size,
            "imgsz": imgsz,
            "device": device_to_use,
            "project": str(output_dir) if output_dir else str(config.MODELS_DIR),
            **kwargs,
        }
        return yolo.train(**train_args)


def find_available_weights() -> Optional[Path]:
    """Search for real medical detector weights in configured model directories."""
    candidates = [
        config.CONFIG.detector.model_path,
        config.MODELS_DIR / "pneumonia_yolo" / "weights" / "best.pt",
        config.MODELS_DIR / "best.pt",
        config.MODELS_DIR / "model.pt",
        config.MODELS_DIR / "pneumonia_yolo.pt",
    ]
    for c in candidates:
        if c and c.is_file():
            return c
    return None


def create_detector(model_path: Optional[Path | str] = None) -> MedicalDetector:
    """Instantiate a ready MedicalDetector.

    If weights are available, instantiates YOLOMedicalDetector and loads the model.
    If no weights exist, safely falls back to NullDetector without crashing.
    """
    weights = Path(model_path) if model_path else find_available_weights()
    if weights and weights.is_file():
        try:
            det = YOLOMedicalDetector(model_path=weights)
            det.load_model()
            return det
        except Exception as exc:
            logger.warning("Failed to load weights from %s: %s; falling back to NullDetector", weights, exc)
            return NullDetector()
    return NullDetector()

