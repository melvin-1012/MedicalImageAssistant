"""
Pytest configuration and shared fixtures for MediVision AI backend tests.

Uses httpx.AsyncClient with the FastAPI app for integration-style tests.
No real Supabase calls are made — all DB/Auth interactions are mocked.
"""

import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from httpx import AsyncClient, ASGITransport

# ── JWT helpers ─────────────────────────────────────────────────────────────

import jose.jwt as _jwt
import datetime

SECRET = "test-jwt-secret-for-testing-only"
ALGORITHM = "HS256"


def _make_token(user_id: str, role: str, extra: dict | None = None) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        "user_metadata": {"role": role, **(extra or {})},
    }
    return _jwt.encode(payload, SECRET, algorithm=ALGORITHM)


# ── Tokens for each role ─────────────────────────────────────────────────────

PATIENT_USER_ID    = "patient-user-uuid-0001"
DOCTOR_USER_ID     = "doctor-user-uuid-0001"
SPECIALIST_USER_ID = "specialist-user-uuid-0001"
ADMIN_USER_ID      = "admin-user-uuid-0001"
OTHER_PATIENT_ID   = "patient-user-uuid-0002"

PATIENT_TOKEN    = _make_token(PATIENT_USER_ID,    "patient")
DOCTOR_TOKEN     = _make_token(DOCTOR_USER_ID,     "doctor")
SPECIALIST_TOKEN = _make_token(SPECIALIST_USER_ID, "specialist")
ADMIN_TOKEN      = _make_token(ADMIN_USER_ID,      "admin")
OTHER_TOKEN      = _make_token(OTHER_PATIENT_ID,   "patient")


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


PATIENT_HEADERS    = auth_headers(PATIENT_TOKEN)
DOCTOR_HEADERS     = auth_headers(DOCTOR_TOKEN)
SPECIALIST_HEADERS = auth_headers(SPECIALIST_TOKEN)
ADMIN_HEADERS      = auth_headers(ADMIN_TOKEN)
OTHER_HEADERS      = auth_headers(OTHER_TOKEN)


# ── App fixture with mocked settings ────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def mock_settings():
    """Patch settings so the app loads without real .env values."""
    with patch("app.config.Settings.__init__", lambda self: None), \
         patch("app.config.settings") as s:
        s.app_name = "MediVision AI Test"
        s.app_version = "test"
        s.debug = True
        s.cors_origins = ["*"]
        s.supabase_url = "https://mock.supabase.co"
        s.supabase_anon_key = "mock-anon-key"
        s.supabase_service_role_key = "mock-service-role-key"
        s.jwt_secret = SECRET
        s.jwt_algorithm = ALGORITHM
        s.access_token_expire_minutes = 60
        s.storage_bucket_images = "medical-images"
        s.storage_bucket_reports = "medical-reports"
        s.storage_bucket_analysis = "analysis-results"
        s.vision_ai_enabled = False
        s.genai_enabled = False
        yield s


@pytest.fixture(scope="session")
def mock_supabase():
    """Return a MagicMock that behaves like the Supabase client."""
    client = MagicMock()
    # Default: empty result
    client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
    return client


@pytest_asyncio.fixture(scope="session")
async def client(mock_settings, mock_supabase):
    """AsyncClient wired to the FastAPI app."""
    with patch("app.database.get_supabase_admin", return_value=mock_supabase), \
         patch("app.database.get_supabase", return_value=mock_supabase):
        from app.main import app
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
