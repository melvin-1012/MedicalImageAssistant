from supabase import create_client, Client
from app.config import settings

_supabase_client: Client | None = None
_supabase_admin: Client | None = None


def get_supabase() -> Client:
    """Anon-key client (respects RLS)."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key,
        )
    return _supabase_client


def get_supabase_admin() -> Client:
    """Service-role client (bypasses RLS – use ONLY in trusted backend operations)."""
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
    return _supabase_admin
