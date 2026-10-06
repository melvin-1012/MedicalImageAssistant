"""Image loading. Supports standard formats (JPG/PNG) and DICOM (.dcm)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import cv2
import numpy as np

import config
from cv.schemas import ImageMetadata, LoadedImage
from utils.logger import get_logger

logger = get_logger("loader")


def _get_pydicom():
    """Lazy import of pydicom so non-DICOM usage works without it."""
    try:
        import pydicom
        return pydicom
    except ImportError as exc:
        raise ImportError(
            "pydicom is required to load DICOM (.dcm) files. "
            "Please install it with `pip install pydicom`."
        ) from exc


def scale_to_8bit(image: np.ndarray) -> np.ndarray:
    """Scale a 16-bit or arbitrary integer/float image to 8-bit uint8 without truncating."""
    if image.dtype == np.uint8:
        return image.copy()
    min_v = float(np.min(image))
    max_v = float(np.max(image))
    if max_v > min_v:
        scaled = (image.astype(np.float32) - min_v) / (max_v - min_v) * 255.0
        return np.clip(scaled, 0.0, 255.0).astype(np.uint8)
    return np.zeros(image.shape, dtype=np.uint8)


class ImageLoader:
    """Loads an image from disk and returns pixels + de-identified metadata."""

    name = "Image loader"

    def __init__(self, supported_extensions: Tuple[str, ...] = config.SUPPORTED_EXTENSIONS) -> None:
        self.supported_extensions = tuple(ext.lower() for ext in supported_extensions)

    @property
    def ready(self) -> bool:
        return True

    def load(self, path: Path | str) -> LoadedImage:
        """Load an image from path (standard image or DICOM)."""
        img_path = Path(path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image file does not exist: {img_path.name}")
        if not img_path.is_file():
            raise ValueError(f"Path is not a regular file: {img_path.name}")

        suffix = img_path.suffix.lower()
        if suffix not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file format '{suffix}'. "
                f"Supported: {', '.join(self.supported_extensions)}"
            )

        if suffix == ".dcm":
            return self._load_dicom(img_path)
        else:
            return self._load_standard(img_path)

    def _load_standard(self, path: Path) -> LoadedImage:
        # Read via np.fromfile + cv2.imdecode to support Windows paths with spaces / non-ASCII
        try:
            file_bytes = np.fromfile(str(path), dtype=np.uint8)
        except Exception as exc:
            raise ValueError(f"Failed to read file bytes: {exc}") from exc

        if file_bytes.size == 0:
            raise ValueError(f"Image file is empty: {path.name}")

        img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Failed to decode image file: {path.name}")

        # Handle channel formats:
        # 1. 4-channel with alpha (RGBA/BGRA) -> drop alpha and convert BGR->RGB
        # 2. 2-channel gray+alpha -> drop alpha
        # 3. 3-channel BGR -> convert to RGB (standard in-memory convention)
        # 4. 1-channel grayscale -> keep as-is
        if img.ndim == 3:
            if img.shape[2] == 4:
                # Drop alpha, convert BGR to RGB
                img = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2RGB)
            elif img.shape[2] == 3:
                # Convert BGR to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif img.shape[2] == 2:
                # 2-channel gray + alpha -> drop alpha
                img = img[:, :, 0]
        elif img.ndim == 2:
            pass  # grayscale (8-bit or 16-bit)

        height, width = img.shape[:2]
        channels = 1 if img.ndim == 2 else img.shape[2]
        dtype = str(img.dtype)
        file_size = path.stat().st_size

        metadata = ImageMetadata(
            path=str(path),
            format=path.suffix.lstrip(".").lower(),
            width=width,
            height=height,
            channels=channels,
            dtype=dtype,
            file_size_bytes=file_size,
            extra={},
        )
        logger.info("Loaded standard image (%dx%d, %s, %d channels)", width, height, dtype, channels)
        return LoadedImage(image=img, metadata=metadata)

    def _load_dicom(self, path: Path) -> LoadedImage:
        pydicom = _get_pydicom()
        try:
            ds = pydicom.dcmread(str(path), force=True)
        except Exception as exc:
            raise ValueError(f"Failed to parse DICOM file: {exc}") from exc

        if not hasattr(ds, "pixel_array"):
            raise ValueError(f"DICOM file has no pixel data: {path.name}")

        pixel_array = ds.pixel_array.astype(np.float32)

        # 1. Rescale slope and intercept if present
        slope = float(getattr(ds, "RescaleSlope", 1.0) or 1.0)
        intercept = float(getattr(ds, "RescaleIntercept", 0.0) or 0.0)
        if slope != 1.0 or intercept != 0.0:
            pixel_array = pixel_array * slope + intercept

        # 2. Windowing / VOI LUT scaling to 8-bit
        bits_stored = int(getattr(ds, "BitsStored", 8) or 8)
        wc = getattr(ds, "WindowCenter", None)
        ww = getattr(ds, "WindowWidth", None)
        if wc is not None and ww is not None:
            try:
                center = float(wc[0] if isinstance(wc, (list, pydicom.multival.MultiValue)) else wc)
                width_val = float(ww[0] if isinstance(ww, (list, pydicom.multival.MultiValue)) else ww)
                if width_val > 0:
                    low = center - width_val / 2.0
                    high = center + width_val / 2.0
                    clipped = np.clip(pixel_array, low, high)
                    img_8bit = ((clipped - low) / (high - low) * 255.0).astype(np.uint8)
                else:
                    img_8bit = scale_to_8bit(pixel_array)
            except Exception:
                img_8bit = scale_to_8bit(pixel_array)
        else:
            # Native 8-bit image without VOI LUT retains true density range
            if bits_stored == 8 and pixel_array.max() <= 255 and pixel_array.min() >= 0:
                img_8bit = np.clip(pixel_array, 0, 255).astype(np.uint8)
            else:
                img_8bit = scale_to_8bit(pixel_array)

        # 3. Photometric Interpretation: invert MONOCHROME1 -> standard MONOCHROME2
        photometric = str(getattr(ds, "PhotometricInterpretation", "MONOCHROME2") or "MONOCHROME2").strip().upper()
        if photometric == "MONOCHROME1":
            img_8bit = 255 - img_8bit

        height, width = img_8bit.shape[:2]
        channels = 1 if img_8bit.ndim == 2 else img_8bit.shape[2]
        file_size = path.stat().st_size

        # 4. Extract safe metadata without PHI (no patient name, ID, birth date, age, sex)
        extra: Dict[str, Any] = {}
        modality = getattr(ds, "Modality", None)
        if modality:
            extra["modality"] = str(modality).strip()

        view_pos = getattr(ds, "ViewPosition", None)
        if view_pos:
            extra["view_position"] = str(view_pos).strip()

        if bits_stored:
            extra["original_bits_stored"] = bits_stored

        if photometric:
            extra["photometric_interpretation"] = photometric

        # Strict safety check: strip all PHI tags
        for phi_key in (
            "PatientName", "PatientID", "PatientBirthDate", "PatientAge", "PatientSex",
            "patient_name", "patient_id", "patient_birth_date", "patient_age", "patient_sex",
            "patientId",
        ):
            extra.pop(phi_key, None)

        metadata = ImageMetadata(
            path=str(path),
            format="dcm",
            width=width,
            height=height,
            channels=channels,
            dtype="uint8",
            file_size_bytes=file_size,
            extra=extra,
        )
        logger.info(
            "Loaded DICOM image (%dx%d, %s, %s)",
            width,
            height,
            extra.get("view_position", "unknown-view"),
            photometric,
        )
        return LoadedImage(image=img_8bit, metadata=metadata)
