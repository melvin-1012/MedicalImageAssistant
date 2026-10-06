from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, patients, doctors, appointments, imaging, reports, analysis, specialists

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Healthcare Management System — MediVision AI",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router,         prefix="/auth",             tags=["Authentication"])
app.include_router(patients.router,     prefix="/patients",         tags=["Patients"])
app.include_router(doctors.router,      prefix="/doctors",          tags=["Doctors"])
app.include_router(appointments.router, prefix="/appointments",     tags=["Appointments"])
app.include_router(imaging.router,      prefix="/imaging",          tags=["Imaging"])
app.include_router(imaging.router,      prefix="/imaging-requests", tags=["Imaging Requests"])
app.include_router(reports.router,      prefix="/reports",          tags=["Reports"])
app.include_router(analysis.router,     prefix="/analysis",         tags=["Analysis"])
app.include_router(specialists.router,  prefix="/specialists",      tags=["Specialists"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
