"""
Tests: Appointment Creation and Management

Covers:
- Booking appointments
- Fetching appointments
- Updating appointment status
- Data validation on appointment fields
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import PATIENT_HEADERS, DOCTOR_HEADERS


@pytest.mark.asyncio
async def test_patient_can_create_appointment(client):
    """Patient can schedule an appointment."""
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "patient-db-id-001",
        "mr_number": "MR-2024-0001",
    }
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": "appt-001",
        "patient_id": "patient-db-id-001",
        "full_name": "John Doe",
        "appointment_date": "2026-10-15",
        "appointment_time": "10:30:00",
        "symptoms": "Severe persistent headache",
        "status": "pending",
    }]

    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.post(
            "/appointments",
            headers=PATIENT_HEADERS,
            json={
                "full_name": "John Doe",
                "phone": "+1-555-0199",
                "appointment_date": "2026-10-15",
                "appointment_time": "10:30:00",
                "symptoms": "Severe persistent headache",
                "department": "Neurology",
            },
        )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_appointment_validation_failure(client):
    """Missing required symptoms field should fail validation."""
    resp = await client.post(
        "/appointments",
        headers=PATIENT_HEADERS,
        json={
            "full_name": "John Doe",
            "phone": "+1-555-0199",
            "appointment_date": "2026-10-15",
            "appointment_time": "10:30:00",
            # missing symptoms
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_doctor_can_update_appointment_status(client):
    """Doctors can update appointment status (e.g. to confirmed or completed)."""
    mock_db = MagicMock()
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
        "id": "appt-001",
        "status": "confirmed",
    }]

    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.patch(
            "/appointments/appt-001",
            headers=DOCTOR_HEADERS,
            json={"status": "confirmed"},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
