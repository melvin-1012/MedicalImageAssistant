from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.database import get_supabase, get_supabase_admin

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # patient | doctor | specialist


@router.post("/login")
async def login(body: LoginRequest):
    """Sign in with email + password. Returns Supabase session tokens."""
    try:
        db = get_supabase()
        response = db.auth.sign_in_with_password({"email": body.email, "password": body.password})
        session = response.session
        user = response.user
        if not session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        role = (user.user_metadata or {}).get("role", "patient")
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "role": role,
                "full_name": (user.user_metadata or {}).get("full_name", ""),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/signup")
async def signup(body: SignUpRequest):
    """Register a new user with a specific role."""
    allowed_roles = {"patient", "doctor", "specialist"}
    if body.role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {allowed_roles}")
    try:
        db = get_supabase_admin()
        response = db.auth.admin.create_user({
            "email": body.email,
            "password": body.password,
            "user_metadata": {"role": body.role, "full_name": body.full_name},
            "email_confirm": True,
        })
        user = response.user
        return {
            "id": user.id,
            "email": user.email,
            "role": body.role,
            "message": "User created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout():
    return {"message": "Logged out. Please clear your local session token."}


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        db = get_supabase()
        response = db.auth.refresh_session(refresh_token)
        session = response.session
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
