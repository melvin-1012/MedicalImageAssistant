from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.database import get_supabase, get_supabase_admin
from app.dependencies import get_current_user, get_current_user_id
from app.config import settings
import uuid

router = APIRouter()


class LoginRequest(BaseModel):
    identifier: str
    password: str


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # patient | doctor | specialist


@router.get("/me")
async def get_current_user_profile(
    user_id: str = Depends(get_current_user_id),
    user: dict = Depends(get_current_user),
):
    """Retrieve profile of the currently authenticated user."""
    meta = user.get("user_metadata") or {}
    role = meta.get("role", "patient")
    email = user.get("email") or meta.get("email")
    full_name = meta.get("full_name")

    db = get_supabase_admin()
    profile_table_id = None
    try:
        if role == "patient":
            p = db.table("patients").select("id").eq("profile_id", user_id).single().execute()
            if p.data:
                profile_table_id = p.data["id"]
        elif role == "doctor":
            d = db.table("doctors").select("id").eq("profile_id", user_id).single().execute()
            if d.data:
                profile_table_id = d.data["id"]
        elif role == "specialist":
            s = db.table("specialists").select("id").eq("profile_id", user_id).single().execute()
            if s.data:
                profile_table_id = s.data["id"]
    except Exception:
        pass

    return {
        "id": user_id,
        "role": role,
        "full_name": full_name,
        "email": email,
        "profile_table_id": profile_table_id,
    }


@router.post("/login")
async def login(body: LoginRequest):
    """Sign in with email/MRN + password. Returns Supabase session tokens."""
    identifier = body.identifier.strip()
    password = body.password
    email = identifier
    
    # Offline Demo Mock
    if "your-project-id" in settings.supabase_url:
        import datetime
        from jose import jwt
        email_lower = email.lower()
        role = "doctor" if ("doc" in email_lower or "joison" in email_lower or "melvin" in email_lower or "joseph" in email_lower or "ilakkiya" in email_lower) else ("specialist" if "specialist" in email_lower else "patient")
        user_id = "00000000-0000-0000-0000-000000000001"
        full_name = email.split("@")[0].replace(".", " ").title() if "@" in email else email
        token_payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "user_metadata": {"role": role, "full_name": full_name},
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        }
        token = jwt.encode(token_payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return {
            "access_token": token,
            "refresh_token": "demo-refresh-token",
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "role": role,
                "full_name": full_name,
            },
        }

    try:
        db = get_supabase_admin()
        
        # If identifier is not an email, assume it's an MRN
        if "@" not in identifier:
            p_resp = db.table("patients").select("profile_id, email").eq("mr_number", identifier).single().execute()
            if not p_resp.data:
                raise HTTPException(status_code=404, detail="Medical Record Number not found")
            
            # Use patient's stored email if exists, otherwise fallback to auth user via profile
            if p_resp.data.get("email"):
                email = p_resp.data["email"]
            elif p_resp.data.get("profile_id"):
                user_resp = db.auth.admin.get_user_by_id(p_resp.data["profile_id"])
                if user_resp.user and user_resp.user.email:
                    email = user_resp.user.email
                else:
                    raise HTTPException(status_code=404, detail="No email linked to this MR Number")
            else:
                raise HTTPException(status_code=404, detail="Patient profile is incomplete")

        # Authenticate via Supabase Auth
        auth_client = get_supabase()
        response = auth_client.auth.sign_in_with_password({"email": email, "password": password})
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
        msg = str(e)
        if "Invalid login credentials" in msg:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        raise HTTPException(status_code=401, detail=msg)


@router.post("/signup")
async def signup(body: SignUpRequest):
    """Register a new user with a specific role."""
    allowed_roles = {"patient", "doctor", "specialist"}
    if body.role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {allowed_roles}")

    if "your-project-id" in settings.supabase_url:
        import uuid
        return {
            "id": str(uuid.uuid4()),
            "email": body.email,
            "role": body.role,
            "message": "User created successfully",
        }

    try:
        db = get_supabase_admin()
        
        # Check if user already exists
        # In a real app we might catch the exception, but Supabase will throw a 422 if email exists.
        try:
            response = db.auth.admin.create_user({
                "email": body.email,
                "password": body.password,
                "user_metadata": {"role": body.role, "full_name": body.full_name},
                "email_confirm": True,
            })
            user = response.user
        except Exception as e:
            if "already registered" in str(e).lower() or "already exists" in str(e).lower():
                raise HTTPException(status_code=409, detail="User with this email already exists")
            raise HTTPException(status_code=400, detail=str(e))

        # Supabase trigger `on_auth_user_created` creates the `profiles` record automatically.
        
        if body.role == "patient":
            import random
            from datetime import datetime
            import time
            
            # Wait briefly to ensure the trigger has committed the profile
            time.sleep(0.5) 
            
            # Generate a unique MR Number
            year = datetime.utcnow().year
            mrn = f"MR-{year}-{random.randint(1000, 9999)}"
            
            # Insert into patients table
            db.table("patients").insert({
                "profile_id": user.id,
                "full_name": body.full_name,
                "mr_number": mrn,
                "email": user.email
            }).execute()

        return {
            "id": user.id,
            "email": user.email,
            "role": body.role,
            "message": "User created successfully",
        }
    except HTTPException:
        raise
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
