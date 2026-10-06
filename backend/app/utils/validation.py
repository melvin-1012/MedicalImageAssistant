"""
Validation utilities for MediVision AI backend.

Contains reusable validators for file uploads, MR numbers,
phone numbers, and other domain-specific inputs.
"""

import re
import mimetypes
from typing import Optional
from fastapi import HTTPException, status

# ── File validation ────────────────────────────────────────────────────────────

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/tiff",
    "image/dicom",
    "application/dicom",
}

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".dcm"}

MAX_IMAGE_SIZE_BYTES = 50 * 1024 * 1024   # 50 MB
MAX_REPORT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_image_file(
    filename: str,
    content_type: str,
    file_size: int,
) -> None:
    """
    Validate a medical image file.

    Raises HTTPException 400 if the file is invalid.
    """
    ext = _get_extension(filename)
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file extension '{ext}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
            ),
        )
    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid MIME type '{content_type}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_IMAGE_MIME_TYPES))}"
            ),
        )
    if file_size > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File too large ({file_size / 1024 / 1024:.1f} MB). "
                f"Maximum allowed: {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB"
            ),
        )


def validate_mr_number(mr_number: str) -> str:
    """
    Normalise and validate an MR Number.

    MR numbers must match MR-YYYY-NNNN (e.g. MR-2024-0001).
    Returns the upper-cased MR number.
    Raises HTTPException 400 if invalid.
    """
    normalised = mr_number.strip().upper()
    pattern = r"^MR-\d{4}-\d{4}$"
    if not re.match(pattern, normalised):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid MR number format '{mr_number}'. "
                "Expected format: MR-YYYY-NNNN (e.g. MR-2024-0001)"
            ),
        )
    return normalised


def validate_phone_number(phone: str) -> str:
    """
    Basic phone number validation (digits, spaces, +, -, parens allowed).
    Returns the stripped phone number.
    """
    cleaned = re.sub(r"[\s\-().]", "", phone)
    if not re.match(r"^\+?\d{7,15}$", cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid phone number: '{phone}'",
        )
    return phone.strip()


def validate_imaging_type(imaging_type: str) -> str:
    """
    Validate and normalise an imaging type string.
    Returns the lower-cased imaging type.
    Raises HTTPException 400 if not one of: xray, ct_scan, mri.
    """
    normalised = imaging_type.strip().lower()
    allowed = {"xray", "ct_scan", "mri"}
    if normalised not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid imaging type '{imaging_type}'. Allowed: {', '.join(sorted(allowed))}",
        )
    return normalised


def sanitise_filename(filename: str) -> str:
    """
    Remove dangerous characters from a filename.
    Keeps alphanumerics, dots, hyphens, and underscores.
    """
    base = filename.rsplit(".", 1)
    name = re.sub(r"[^\w\-]", "_", base[0])
    if len(base) == 2:
        ext = re.sub(r"[^\w]", "", base[1])
        return f"{name}.{ext}"
    return name


# ── Internal helpers ───────────────────────────────────────────────────────────

def _get_extension(filename: str) -> str:
    """Return the lower-cased extension including the leading dot."""
    parts = filename.rsplit(".", 1)
    if len(parts) == 2:
        return f".{parts[1].lower()}"
    return ""
