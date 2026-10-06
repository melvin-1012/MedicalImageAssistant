"""
Supabase Storage Service

Handles secure upload/download of medical images and PDF reports.
Uses the service-role client to upload; uses signed URLs for downloads
so files are never publicly exposed.
"""

import logging
import mimetypes
from typing import Optional
from app.database import get_supabase_admin
from app.config import settings

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png",
    "image/dicom", "application/dicom",
    "image/tiff",
}
ALLOWED_REPORT_TYPES = {"application/pdf"}
MAX_IMAGE_SIZE_MB = 50
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024


def validate_medical_image(filename: str, content_type: str, file_size: int) -> None:
    """Raise ValueError if file is not a valid medical image."""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            f"Invalid file type '{content_type}'. "
            f"Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    if file_size > MAX_IMAGE_SIZE_BYTES:
        raise ValueError(
            f"File too large ({file_size / 1024 / 1024:.1f} MB). "
            f"Maximum: {MAX_IMAGE_SIZE_MB} MB"
        )


async def upload_medical_image(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    request_id: str,
) -> str:
    """
    Upload a medical image to Supabase Storage.

    Returns the storage path (bucket-relative).
    """
    db = get_supabase_admin()
    path = f"{request_id}/{filename}"

    db.storage.from_(settings.storage_bucket_images).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    logger.info(f"[StorageService] Uploaded image: {path}")
    return path


async def upload_report_pdf(
    pdf_bytes: bytes,
    filename: str,
    patient_id: str,
) -> str:
    """Upload a generated PDF report to Supabase Storage."""
    db = get_supabase_admin()
    path = f"{patient_id}/{filename}"

    db.storage.from_(settings.storage_bucket_reports).upload(
        path=path,
        file=pdf_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )
    logger.info(f"[StorageService] Uploaded report: {path}")
    return path


def get_signed_image_url(path: str, expires_in: int = 3600) -> Optional[str]:
    """Generate a signed URL for an image (expires in `expires_in` seconds)."""
    try:
        db = get_supabase_admin()
        response = db.storage.from_(settings.storage_bucket_images).create_signed_url(
            path, expires_in
        )
        return response.get("signedURL") or response.get("signedUrl")
    except Exception as e:
        logger.error(f"[StorageService] Failed to get signed image URL: {e}")
        return None


def get_signed_report_url(path: str, expires_in: int = 3600) -> Optional[str]:
    """Generate a signed URL for a report PDF."""
    try:
        db = get_supabase_admin()
        response = db.storage.from_(settings.storage_bucket_reports).create_signed_url(
            path, expires_in
        )
        return response.get("signedURL") or response.get("signedUrl")
    except Exception as e:
        logger.error(f"[StorageService] Failed to get signed report URL: {e}")
        return None
