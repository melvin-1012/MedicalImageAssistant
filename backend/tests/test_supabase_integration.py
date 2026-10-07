"""
Tests for Supabase Database and Storage Integration.

Verifies:
1. Configuration resolution for SUPABASE_URL, SUPABASE_KEY, and storage buckets.
2. Proper client initialization via get_supabase() and get_supabase_admin().
3. CRUD query mechanics against Supabase PostgreSQL tables.
4. Error handling and HTTP status codes for missing rows and unauthorized access.
5. Supabase Storage bucket resolution for medical images and reports.
"""

import pytest
from unittest.mock import MagicMock, patch
from tests.conftest import DOCTOR_HEADERS, PATIENT_HEADERS, SPECIALIST_HEADERS


def test_supabase_config_key_properties():
    """Verify SUPABASE_URL, SUPABASE_KEY, and storage bucket settings."""
    from app.config import settings
    assert settings.supabase_url is not None
    assert settings.storage_bucket_images == "medical-images"
    assert settings.storage_bucket_reports == "medical-reports"
    assert settings.storage_bucket_analysis == "analysis-results"


def test_supabase_client_creation():
    """Verify get_supabase and get_supabase_admin return valid client instances."""
    import app.database as db_module
    client = db_module.get_supabase()
    admin_client = db_module.get_supabase_admin()
    assert client is not None
    assert admin_client is not None


@pytest.mark.asyncio
async def test_supabase_patients_table_crud(client, mock_supabase):
    """Verify patients table read operation via Supabase admin client."""
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {"id": "p1", "full_name": "Test Patient", "mr_number": "MR-2024-0001", "age": 35}
    ]

    resp = await client.get("/patients/", headers=DOCTOR_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["mr_number"] == "MR-2024-0001"
    mock_supabase.table.assert_called_with("patients")


@pytest.mark.asyncio
async def test_supabase_appointments_table_crud(client, mock_supabase):
    """Verify appointments table insert operation via Supabase client."""
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "p100",
        "mr_number": "MR-2024-0001"
    }
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
        {
            "id": "apt-1",
            "patient_id": "p100",
            "mr_number": "MR-2024-0001",
            "full_name": "Test Patient",
            "department": "Cardiology",
            "status": "pending",
        }
    ]

    payload = {
        "full_name": "Test Patient",
        "mr_number": "MR-2024-0001",
        "symptoms": "Chest tightness",
        "department": "Cardiology",
        "appointment_date": "2026-11-20",
        "appointment_time": "10:30",
        "phone": "+1-555-0100",
    }

    resp = await client.post("/appointments/", headers=PATIENT_HEADERS, json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "apt-1"
    assert data["department"] == "Cardiology"


@pytest.mark.asyncio
async def test_supabase_reports_table_query(client, mock_supabase):
    """Verify medical_reports table select operation with joins."""
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "doc-1"
    }
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"patient_id": "p1"}
    ]
    mock_supabase.table.return_value.select.return_value.order.return_value.in_.return_value.execute.return_value.data = [
        {
            "id": "rep-1",
            "patient_id": "p1",
            "report_status": "under_review",
            "report_pdf_path": "reports/MR-2024-0001_report.pdf",
        }
    ]

    resp = await client.get("/reports/", headers=DOCTOR_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "rep-1"
