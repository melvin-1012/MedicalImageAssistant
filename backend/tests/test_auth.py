"""
Tests: Authentication & Role Authorization

Covers:
- GET /auth/me with valid/invalid tokens
- Role enforcement for patient, doctor, specialist, admin
- Unauthenticated access rejection
"""

import pytest
from tests.conftest import (
    PATIENT_HEADERS, DOCTOR_HEADERS, SPECIALIST_HEADERS, ADMIN_HEADERS,
    DOCTOR_USER_ID, PATIENT_USER_ID,
)
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_health_check(client):
    """Health endpoint should return 200 without auth."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_returns_ok(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_get_me_no_token_returns_403(client):
    """Requests without a Bearer token must be rejected."""
    resp = await client.get("/auth/me")
    assert resp.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_get_me_invalid_token_returns_401(client):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_patients_endpoint_requires_auth(client):
    """GET /patients must reject unauthenticated requests."""
    resp = await client.get("/patients")
    assert resp.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_patient_cannot_access_all_patients(client):
    """Patients should NOT be able to list all patients (doctor-only endpoint)."""
    resp = await client.get("/patients", headers=PATIENT_HEADERS)
    # Should be 403 Forbidden (patient role not allowed)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_doctor_can_access_patients_list(client):
    """Doctors should be able to list patients."""
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.order.return_value.execute.return_value.data = []
    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.get("/patients", headers=DOCTOR_HEADERS)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_specialist_cannot_access_patients_list(client):
    """Specialists should NOT be able to list all patients."""
    resp = await client.get("/patients", headers=SPECIALIST_HEADERS)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_imaging_request_rejected(client):
    """Creating imaging requests without auth must fail."""
    resp = await client.post("/imaging", json={
        "patient_id": "some-id",
        "imaging_type": "xray",
        "reason": "test",
    })
    assert resp.status_code in (401, 403, 404, 422)


@pytest.mark.asyncio
async def test_patient_cannot_create_imaging_request(client):
    """Patients must not be able to create imaging requests."""
    resp = await client.post("/imaging/requests", headers=PATIENT_HEADERS, json={
        "patient_id": "some-id",
        "imaging_type": "xray",
        "reason": "self referral attempt",
    })
    assert resp.status_code in (403, 404, 422)


@pytest.mark.asyncio
async def test_unauthenticated_appointments_rejected(client):
    resp = await client.get("/appointments")
    assert resp.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_unauthenticated_reports_rejected(client):
    resp = await client.get("/reports")
    assert resp.status_code in (401, 403, 422)
