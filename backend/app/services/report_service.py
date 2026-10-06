"""
PDF Report Generator

Generates a professional medical imaging PDF report using ReportLab.
Stores the PDF in Supabase Storage and records metadata in medical_reports.
"""

import io
import logging
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from app.database import get_supabase_admin
from app.services.storage_service import upload_report_pdf

logger = logging.getLogger(__name__)

# ── Colour palette ─────────────────────────────────────────────
PRIMARY_BLUE = colors.HexColor("#1565C0")
LIGHT_BLUE = colors.HexColor("#E3F2FD")
DARK_GRAY = colors.HexColor("#37474F")
RED_WARN = colors.HexColor("#C62828")
GREEN_OK = colors.HexColor("#2E7D32")
BORDER = colors.HexColor("#B0BEC5")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Title2", parent=styles["Title"], textColor=PRIMARY_BLUE, fontSize=20, spaceAfter=4))
    styles.add(ParagraphStyle("SubTitle2", parent=styles["Normal"], textColor=DARK_GRAY, fontSize=10, spaceAfter=2))
    styles.add(ParagraphStyle("SectionHead", parent=styles["Normal"], fontSize=12, fontName="Helvetica-Bold",
                               textColor=PRIMARY_BLUE, spaceBefore=12, spaceAfter=4))
    styles.add(ParagraphStyle("Body2", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8, textColor=RED_WARN,
                               leading=11, spaceBefore=6))
    styles.add(ParagraphStyle("Label", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold",
                               textColor=DARK_GRAY))
    styles.add(ParagraphStyle("Value", parent=styles["Normal"], fontSize=10, textColor=colors.black))
    return styles


def _build_patient_table(patient: dict, study: dict, styles) -> Table:
    imaging_labels = {"xray": "X-Ray", "ct_scan": "CT Scan", "mri": "MRI"}
    imaging_type = imaging_labels.get(study.get("imaging_type", ""), study.get("imaging_type", "N/A").upper())
    upload_date = study.get("uploaded_at", datetime.utcnow().isoformat())
    if isinstance(upload_date, str):
        try:
            upload_date = datetime.fromisoformat(upload_date.replace("Z", "+00:00")).strftime("%d %b %Y")
        except Exception:
            pass

    data = [
        [Paragraph("<b>Patient Name</b>", styles["Label"]), Paragraph(patient.get("full_name", "N/A"), styles["Value"]),
         Paragraph("<b>MR Number</b>", styles["Label"]), Paragraph(patient.get("mr_number", "N/A"), styles["Value"])],
        [Paragraph("<b>Age</b>", styles["Label"]), Paragraph(str(patient.get("age", "N/A")), styles["Value"]),
         Paragraph("<b>Gender</b>", styles["Label"]), Paragraph((patient.get("gender") or "N/A").capitalize(), styles["Value"])],
        [Paragraph("<b>Imaging Type</b>", styles["Label"]), Paragraph(imaging_type, styles["Value"]),
         Paragraph("<b>Date</b>", styles["Label"]), Paragraph(upload_date, styles["Value"])],
    ]
    t = Table(data, colWidths=[38*mm, 62*mm, 38*mm, 62*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BLUE, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


async def generate_report(
    patient: dict,
    study: dict,
    analysis_id: str,
    analysis: dict,
    doctor_assessment: Optional[dict] = None,
) -> Optional[str]:
    """
    Generate a PDF report and store in Supabase Storage.
    Returns report_id from medical_reports table.
    """
    db = get_supabase_admin()
    styles = _styles()
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=15*mm, bottomMargin=20*mm,
    )

    elements = []

    # ── Header ─────────────────────────────────────────────────
    elements.append(Paragraph("MediVision AI", styles["Title2"]))
    elements.append(Paragraph("Medical Imaging & Analysis Report", styles["SubTitle2"]))
    elements.append(Paragraph("City Medical Center · Dept. of Radiology & Medical Imaging", styles["SubTitle2"]))
    elements.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_BLUE, spaceAfter=10))

    # ── Patient Info ───────────────────────────────────────────
    elements.append(Paragraph("Patient Information", styles["SectionHead"]))
    elements.append(_build_patient_table(patient, study, styles))
    elements.append(Spacer(1, 10))

    # ── AI Findings ────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    elements.append(Paragraph("⚠ AI-Generated Findings (Demo — Not a Medical Diagnosis)", styles["SectionHead"]))

    findings_data = [
        [Paragraph("<b>Finding</b>", styles["Label"]), Paragraph(analysis.get("finding", "N/A"), styles["Body2"])],
        [Paragraph("<b>Location</b>", styles["Label"]), Paragraph(analysis.get("location", "N/A"), styles["Body2"])],
        [Paragraph("<b>Confidence</b>", styles["Label"]),
         Paragraph(f"{float(analysis.get('confidence_score', 0)) * 100:.0f}%", styles["Body2"])],
        [Paragraph("<b>Model</b>", styles["Label"]),
         Paragraph(f"{analysis.get('model_name', 'N/A')} v{analysis.get('model_version', 'N/A')}", styles["Body2"])],
    ]
    ft = Table(findings_data, colWidths=[45*mm, 115*mm])
    ft.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BLUE, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(ft)
    elements.append(Spacer(1, 8))

    # ── Clinical Context ───────────────────────────────────────
    elements.append(Paragraph("Clinical Context", styles["SectionHead"]))
    elements.append(Paragraph(analysis.get("clinical_context", "N/A"), styles["Body2"]))
    elements.append(Spacer(1, 8))

    # ── AI Explanation ─────────────────────────────────────────
    elements.append(Paragraph("AI Analysis Explanation", styles["SectionHead"]))
    elements.append(Paragraph(analysis.get("explanation", "N/A"), styles["Body2"]))
    elements.append(Spacer(1, 8))

    # ── AI Limitations ─────────────────────────────────────────
    elements.append(Paragraph("Limitations & Disclaimer", styles["SectionHead"]))
    elements.append(Paragraph(analysis.get("limitations", ""), styles["Disclaimer"]))
    elements.append(Spacer(1, 12))

    # ── Doctor's Final Assessment (if finalized) ───────────────
    if doctor_assessment:
        elements.append(HRFlowable(width="100%", thickness=2, color=GREEN_OK, spaceAfter=6))
        elements.append(Paragraph("✔ Doctor's Final Clinical Assessment", styles["SectionHead"]))

        da_data = [
            [Paragraph("<b>Diagnosis</b>", styles["Label"]),
             Paragraph(doctor_assessment.get("diagnosis", "N/A"), styles["Body2"])],
            [Paragraph("<b>Conclusion</b>", styles["Label"]),
             Paragraph(doctor_assessment.get("conclusion", "N/A"), styles["Body2"])],
            [Paragraph("<b>Medications</b>", styles["Label"]),
             Paragraph(doctor_assessment.get("medications", "None specified"), styles["Body2"])],
            [Paragraph("<b>Recommendations</b>", styles["Label"]),
             Paragraph(doctor_assessment.get("recommendations", "N/A"), styles["Body2"])],
            [Paragraph("<b>Follow-up</b>", styles["Label"]),
             Paragraph(doctor_assessment.get("follow_up_instructions", "N/A"), styles["Body2"])],
        ]
        if doctor_assessment.get("additional_notes"):
            da_data.append([
                Paragraph("<b>Notes</b>", styles["Label"]),
                Paragraph(doctor_assessment["additional_notes"], styles["Body2"]),
            ])

        dat = Table(da_data, colWidths=[45*mm, 115*mm])
        dat.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#E8F5E9"), colors.white]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(dat)
        elements.append(Spacer(1, 10))

        # Finalized by
        finalized_at = doctor_assessment.get("finalized_at", "")
        if isinstance(finalized_at, str) and finalized_at:
            try:
                finalized_at = datetime.fromisoformat(finalized_at.replace("Z", "+00:00")).strftime("%d %b %Y %H:%M")
            except Exception:
                pass
        elements.append(Paragraph(
            f"This report has been reviewed and finalized by the treating physician on {finalized_at}.",
            styles["Body2"]
        ))

    # ── Footer ─────────────────────────────────────────────────
    elements.append(Spacer(1, 16))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elements.append(Paragraph(
        "MediVision AI · City Medical Center · 123 Medical Drive, Chennai 600001 · Tel: +91-44-1234-5678 · "
        "Email: info@medivision-ai.com · This document is confidential.",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=7, textColor=DARK_GRAY, alignment=TA_CENTER),
    ))

    doc.build(elements)
    pdf_bytes = buf.getvalue()

    # Upload PDF
    mr_number = patient.get("mr_number", "UNKNOWN")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{mr_number}_{timestamp}.pdf"
    patient_id = patient.get("id", "unknown")
    pdf_path = await upload_report_pdf(pdf_bytes, filename, patient_id)

    # Save to medical_reports
    study_id = study.get("id")
    report_data = {
        "patient_id": patient_id,
        "imaging_study_id": study_id,
        "ai_analysis_id": analysis_id,
        "report_pdf_path": pdf_path,
        "report_status": "generated",
        "generated_at": datetime.utcnow().isoformat(),
    }
    report_resp = db.table("medical_reports").insert(report_data).execute()
    report = report_resp.data[0] if report_resp.data else {}
    report_id = report.get("id")

    # Update imaging request to report_generated
    request_id = study.get("imaging_request_id")
    if request_id:
        db.table("imaging_requests").update({"status": "report_generated"}).eq("id", request_id).execute()

    logger.info(f"[ReportService] Generated report {report_id} → {pdf_path}")
    return report_id
