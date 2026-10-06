"""
PDF Service

A thin facade that delegates PDF generation to report_service.generate_pdf_bytes.
Keep PDF-building logic in report_service; use this module for any additional
pdf-specific utilities (merging, compression, watermarking, etc.).
"""

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def render_pdf(
    patient: dict,
    study: dict,
    analysis: dict,
    doctor_assessment: Optional[dict] = None,
) -> bytes:
    """
    Render a medical report PDF from structured data.

    This delegates to report_service.build_pdf_bytes so that all
    PDF styling is in one place.

    Args:
        patient: Patient row dict (full_name, mr_number, age, gender, etc.)
        study:   Imaging study row dict (imaging_type, original_filename, uploaded_at)
        analysis: AI analysis row dict (finding, location, confidence_score, …)
        doctor_assessment: Optional dict with doctor's conclusion/diagnosis

    Returns:
        PDF as raw bytes
    """
    from app.services.report_service import build_pdf_bytes
    return build_pdf_bytes(
        patient=patient,
        study=study,
        analysis=analysis,
        doctor_assessment=doctor_assessment,
    )


def add_watermark(pdf_bytes: bytes, text: str = "CONFIDENTIAL") -> bytes:
    """
    Add a diagonal watermark to each page of a PDF.

    NOTE: Requires PyPDF2 or pypdf. Currently returns the original bytes
    unchanged as a safe no-op until the dependency is confirmed.
    Replace with real watermarking logic when needed.
    """
    # TODO: implement using pypdf or reportlab if required
    logger.debug(f"[PDFService] Watermark requested ('{text}') – no-op placeholder")
    return pdf_bytes
