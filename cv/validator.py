"""Input validation: existence, decodability, size, channels, blank check."""
from __future__ import annotations

from config import ValidationConfig
from cv.schemas import LoadedImage, ValidationResult


class ImageValidator:
    """Rejects unusable inputs before any processing."""

    name = "Validator"

    def __init__(self, config: ValidationConfig | None = None) -> None:
        self.config = config or ValidationConfig()

    @property
    def ready(self) -> bool:
        return True

    def validate(self, loaded: LoadedImage) -> ValidationResult:
        """Validate a loaded image. Implemented in Phase 1."""
        raise NotImplementedError("ImageValidator.validate: Phase 1")
