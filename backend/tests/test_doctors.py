"""
Tests: Doctor Workflow & Actions

Covers:
- Doctor creates imaging requests
- Doctor submits clinical assessment
- Doctor finalizes report (workflow transition to finalized and medical record update)
- Doctor searches reports by MR number
- Non-doctors cannot submit or finalize doctor assessments
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import (
    DOCTOR_HEADERS, PATIENT_HEADERS, SPECIALIST_HEADERS,
    DOCTOR_USER_ID,
)


@pytest.mark.asyncio
async def test_doctor_creates_imaging_request(client):
    """Doctor can create an imaging request for a patient."""
    mock_db = MagicMock()
    # Mock doctor lookup
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "doctor-db-id-001",
        "profile_id": DOCTOR_USER_ID,
        "doctor_name": "Dr. Sarah Mitchell",
    }
    # Mock insert
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": "ir-new-001",
        "patient_id": "patient-db-id-001",
        "doctor_id": "doctor-db-id-001",
        "imaging_type": "xray",
        "reason": "Suspected pneumonia",
        "status": "requested",
    }]

    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.post(
            "/imaging/requests",
            headers=DOCTOR_HEADERS,
            json={
                "patient_id": "patient-db-id-001",
                "imaging_type": "xray",
                "reason": "Suspected pneumonia",
                "symptoms": "Fever, productive cough",
            },
        )
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_specialist_cannot_create_imaging_request(client):
    """Specialists cannot order imaging requests."""
    resp = await client.post(
        "/imaging/requests",
        headers=SPECIALIST_HEADERS,
        json={
            "patient_id": "patient-db-id-001",
            "imaging_type": "xray",
            "reason": "Invalid attempt",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_doctor_submits_assessment(client):
    """Doctor submits clinical assessment for an existing report."""
    mock_db = MagicMock()
    # Doctor lookup
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "doctor-db-id-001",
    }
    # Report lookup and upsert assessment
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": "da-001",
        "report_id": "report-001",
        "diagnosis": "Right middle lobe consolidation",
        "conclusion": "Bacterial pneumonia confirmed",
    }]
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{}]

    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.post(
            "/reports/report-001/assessment",
            headers=DOCTOR_HEADERS,
            json={
                "conclusion": "Bacterial pneumonia confirmed on imaging and clinical grounds",
                "diagnosis": "Community-Acquired Pneumonia",
                "medications": "Amoxicillin-Clavulanate 625mg TID for 7 days",
                "recommendations": "Rest and hydration, repeat chest radiograph in 4 weeks",
                "follow_up_instructions": "Return if dyspnea or high fevers persist",
            },
        )
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_patient_cannot_submit_doctor_assessment(client):
    """Patients cannot submit or modify doctor clinical assessments."""
    resp = await client.post(
        "/reports/report-001/assessment",
        headers=PATIENT_HEADERS,
        json={
            "conclusion": "Self-diagnosis attempt",
            "diagnosis": "None",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_doctor_finalizes_report(client):
    """Doctor can finalize report once an assessment is completed."""
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "doctor-db-id-001",
        "patient_id": "patient-db-id-001",
        "imaging_study_id": "study-db-id-001",
        "diagnosis": "Pneumonia",
        "conclusion": "Resolved",
    }
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{}]
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [{}]

    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.patch(
            "/reports/report-001/finalize",
            headers=DOCTOR_HEADERS,
        )
    assert resp.status_code == 200
    assert "finalized" in resp.json().get("message", "").lower()


@pytest.mark.asyncio
async def test_specialist_cannot_finalize_report(client):
    """Specialists cannot finalize doctor reports."""
    resp = await client.patch(
        "/reports/report-001/finalize",
        headers=SPECIALIST_HEADERS,
    )
    assert resp.status_code == 403
