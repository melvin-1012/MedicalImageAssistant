"""Filesystem helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import config


def ensure_dirs(dirs: Iterable[Path] = config.OUTPUT_DIRS) -> None:
    """Create output directories if missing."""
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def is_supported_image(path: Path) -> bool:
    """True if the extension is currently supported."""
    return Path(path).suffix.lower() in config.SUPPORTED_EXTENSIONS


def list_images(directory: Path = config.SAMPLE_DIR) -> List[Path]:
    """List supported images in a directory (sorted)."""
    return sorted(p for p in Path(directory).glob("*") if is_supported_image(p))
