from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from app.database import get_supabase_admin

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Validate Supabase JWT and return the decoded payload."""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False},
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def get_current_user_id(user: dict = Depends(get_current_user)) -> str:
    return user.get("sub")


async def require_role(required_role: str, user: dict = Depends(get_current_user)) -> dict:
    """Middleware helper — reads role from user_metadata."""
    meta = user.get("user_metadata", {})
    role = meta.get("role", "")
    if role != required_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{required_role}' required")
    return user


def require_patient(user: dict = Depends(get_current_user)) -> dict:
    meta = user.get("user_metadata", {})
    if meta.get("role") != "patient":
        raise HTTPException(status_code=403, detail="Patient role required")
    return user


def require_doctor(user: dict = Depends(get_current_user)) -> dict:
    meta = user.get("user_metadata", {})
    if meta.get("role") != "doctor":
        raise HTTPException(status_code=403, detail="Doctor role required")
    return user


def require_specialist(user: dict = Depends(get_current_user)) -> dict:
    meta = user.get("user_metadata", {})
    if meta.get("role") not in ("specialist", "imaging_staff"):
        raise HTTPException(status_code=403, detail="Specialist role required")
    return user


def require_doctor_or_admin(user: dict = Depends(get_current_user)) -> dict:
    meta = user.get("user_metadata", {})
    if meta.get("role") not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Doctor or admin role required")
    return user
