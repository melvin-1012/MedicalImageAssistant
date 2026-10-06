"""Image loading. Phase 1: JPG/JPEG/PNG. Later: DICOM (pydicom)."""
from __future__ import annotations

from pathlib import Path

import config
from cv.schemas import LoadedImage
from utils.logger import get_logger

logger = get_logger("loader")


class ImageLoader:
    """Loads an image from disk and returns pixels + metadata."""

    name = "Image loader"

    def __init__(self, supported_extensions=config.SUPPORTED_EXTENSIONS) -> None:
        self.supported_extensions = tuple(supported_extensions)

    @property
    def ready(self) -> bool:
        return True

    def load(self, path: Path) -> LoadedImage:
        """Load an image. Implemented in Phase 1."""
        raise NotImplementedError("ImageLoader.load: Phase 1")

    # Phase 1+: _load_standard() for jpg/png, _load_dicom() for .dcm
