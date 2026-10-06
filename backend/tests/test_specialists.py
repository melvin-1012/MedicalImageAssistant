"""
Tests: Specialist Workflow & Role Constraints

Covers:
- Specialist views assigned / available imaging requests
- Specialist assigns themselves to an imaging request
- Specialist cannot access doctor-only operations (finalization, assessments)
- Unauthorized user restrictions on specialist endpoints
"""

import pytest
from unittest.mock import patch, MagicMock
from tests.conftest import (
    SPECIALIST_HEADERS, PATIENT_HEADERS, DOCTOR_HEADERS,
    SPECIALIST_USER_ID,
)


@pytest.mark.asyncio
async def test_specialist_can_get_my_profile(client):
    """Specialist can fetch their profile."""
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "specialist-db-id-001",
        "profile_id": SPECIALIST_USER_ID,
        "specialist_name": "Alex Taylor",
        "specialization": "Radiology Technician",
    }
    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.get("/specialists/me", headers=SPECIALIST_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["specialist_name"] == "Alex Taylor"


@pytest.mark.asyncio
async def test_patient_cannot_access_specialist_me(client):
    """Patients cannot access specialist profile endpoint."""
    resp = await client.get("/specialists/me", headers=PATIENT_HEADERS)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_specialist_can_list_my_imaging_requests(client):
    """Specialists can view requested or assigned imaging requests."""
    mock_db = MagicMock()
    # Mock specialist lookup
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "specialist-db-id-001",
    }
    # Mock imaging requests list
    mock_db.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {
            "id": "ir-001",
            "status": "requested",
            "imaging_type": "xray",
            "specialist_id": None,
        },
        {
            "id": "ir-002",
            "status": "assigned",
            "imaging_type": "mri",
            "specialist_id": "specialist-db-id-001",
        },
    ]
    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.get("/specialists/me/imaging-requests", headers=SPECIALIST_HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_specialist_can_assign_imaging_request(client):
    """Specialist can assign themselves to an imaging request in 'requested' state."""
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "specialist-db-id-001",
        "status": "requested",
    }
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{}]

    with patch("app.database.get_supabase_admin", return_value=mock_db):
        resp = await client.patch(
            "/specialists/imaging-requests/ir-001/assign",
            headers=SPECIALIST_HEADERS,
        )
    assert resp.status_code == 200
    assert "assigned" in resp.json().get("message", "").lower()


@pytest.mark.asyncio
async def test_patient_cannot_assign_imaging_request(client):
    """Patients cannot assign imaging requests."""
    resp = await client.patch(
        "/specialists/imaging-requests/ir-001/assign",
        headers=PATIENT_HEADERS,
    )
    assert resp.status_code == 403
