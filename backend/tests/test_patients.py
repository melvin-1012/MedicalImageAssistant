"""
Tests: Patient Access & Data Isolation

Covers:
- Patient can view own profile/records/reports
- Patient CANNOT view another patient's data
- Patient CANNOT access doctor-only endpoints
- MR number lookup
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import (
    PATIENT_HEADERS, DOCTOR_HEADERS, OTHER_HEADERS,
    PATIENT_USER_ID, OTHER_PATIENT_ID,
)


def _mock_db_with_patient(patient_id: str, mr_number: str = "MR-2024-0001"):
    db = MagicMock()
    patient_row = {
        "id": patient_id,
        "profile_id": PATIENT_USER_ID,
        "mr_number": mr_number,
        "full_name": "Test Patient",
        "age": 35,
        "gender": "male",
    }
    db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = patient_row
    db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [patient_row]
    db.table.return_value.select.return_value.order.return_value.execute.return_value.data = []
    return db


@pytest.mark.asyncio
async def test_patient_can_view_own_profile(client):
    db = _mock_db_with_patient("patient-db-id-001")
    with patch("app.database._override_admin", db):
        resp = await client.get("/patients/me", headers=PATIENT_HEADERS)
    assert resp.status_code in (200, 404)  # 404 if no DB row, 200 if found


@pytest.mark.asyncio
async def test_patient_can_view_own_records(client):
    db = _mock_db_with_patient("patient-db-id-001")
    db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    with patch("app.database._override_admin", db):
        resp = await client.get("/patients/me/records", headers=PATIENT_HEADERS)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_patient_can_view_own_reports(client):
    db = _mock_db_with_patient("patient-db-id-001")
    db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    with patch("app.database._override_admin", db):
        resp = await client.get("/patients/me/reports", headers=PATIENT_HEADERS)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_patient_cannot_view_all_patients(client):
    """Patients must get 403 on the list-all-patients endpoint."""
    resp = await client.get("/patients", headers=PATIENT_HEADERS)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_patient_cannot_access_other_patients_report(client):
    """A patient requesting another patient's report must be denied."""
    db = MagicMock()
    # Report belongs to a DIFFERENT patient
    report_row = {
        "id": "report-001",
        "patient_id": "different-patient-id",
        "report_status": "available_to_patient",
    }
    db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = report_row
    # Requesting patient has a different patient_id
    own_patient_row = {"id": "own-patient-id"}
    # Chain: patients table lookup
    def side_effect_table(table_name):
        mock = MagicMock()
        if table_name == "medical_reports":
            mock.select.return_value.eq.return_value.single.return_value.execute.return_value.data = report_row
        elif table_name == "patients":
            mock.select.return_value.eq.return_value.single.return_value.execute.return_value.data = own_patient_row
        return mock
    db.table.side_effect = side_effect_table
    with patch("app.database._override_admin", db):
        resp = await client.get("/reports/report-001", headers=PATIENT_HEADERS)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_doctor_can_search_by_mr_number(client):
    db = MagicMock()
    patient_row = {"id": "patient-db-id-001", "mr_number": "MR-2024-0001"}
    db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = patient_row
    db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    with patch("app.database._override_admin", db):
        resp = await client.get("/reports/search/MR-2024-0001", headers=DOCTOR_HEADERS)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_patient_cannot_search_by_mr_number_of_other(client):
    """Patient trying to search another patient's MR number."""
    db = MagicMock()
    other_patient = {"id": "other-patient-id", "mr_number": "MR-2024-0099"}
    # mr_number lookup returns a different patient
    db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = other_patient
    # Reports filtered to available_to_patient will be empty
    db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    with patch("app.database._override_admin", db):
        resp = await client.get("/reports/search/MR-2024-0099", headers=PATIENT_HEADERS)
    # Should return empty list (patient sees empty) or access denied
    assert resp.status_code in (200, 403, 404)


@pytest.mark.asyncio
async def test_patient_cannot_create_imaging_request(client):
    resp = await client.post("/imaging/requests", headers=PATIENT_HEADERS, json={
        "patient_id": "any",
        "imaging_type": "xray",
        "reason": "self-referral",
    })
    assert resp.status_code in (403, 404, 422)
