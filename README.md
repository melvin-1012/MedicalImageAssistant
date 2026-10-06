# MediVision AI — Backend & Database Infrastructure

Backend and Supabase Database infrastructure for our medical imaging & healthcare diagnostic platform.

> **Team Responsibility:** Person 2 — Backend, Database, Supabase, Authentication, Storage, Orchestration, PDF Generation, and API Services.  
> **Notice:** This repository contains **strictly backend and database infrastructure**. All frontend code is maintained separately by Person 1.

---

## Architecture & Directory Structure

```text
The-Unscripted/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & middleware
│   │   ├── config.py                # Environment configuration (Pydantic BaseSettings)
│   │   ├── database.py              # Supabase client instantiation (anon & service-role)
│   │   ├── dependencies.py          # JWT verification & role authorization dependencies
│   │   │
│   │   ├── routers/                 # REST API Routers
│   │   │   ├── auth.py              # Login, token validation, user profile
│   │   │   ├── patients.py          # Patient directory & patient self-service
│   │   │   ├── doctors.py           # Doctor registry & lookup
│   │   │   ├── specialists.py       # Imaging specialist operations & assignments
│   │   │   ├── appointments.py      # Consultation scheduling & status updates
│   │   │   ├── imaging.py           # Imaging request lifecycle & file uploads
│   │   │   ├── analysis.py          # AI analysis trigger and lookup
│   │   │   └── reports.py           # PDF report generation, doctor review & finalize
│   │   │
│   │   ├── schemas/                 # Pydantic v2 Request/Response Schemas
│   │   │   ├── auth.py
│   │   │   ├── patient.py
│   │   │   ├── doctor.py
│   │   │   ├── appointment.py
│   │   │   ├── imaging.py
│   │   │   ├── analysis.py
│   │   │   └── report.py
│   │   │
│   │   ├── services/                # Business Logic & AI Interfaces
│   │   │   ├── storage_service.py   # Supabase Storage operations & signed URLs
│   │   │   ├── imaging_service.py   # Imaging pipeline orchestration
│   │   │   ├── analysis_service.py  # Analysis workflow execution
│   │   │   ├── vision_service.py    # Clean interface for Person 3 (Vision AI)
│   │   │   ├── genai_service.py     # Clean interface for Person 4 (Multimodal AI)
│   │   │   ├── report_service.py    # Report generation logic
│   │   │   └── pdf_service.py       # ReportLab PDF compilation & rendering
│   │   │
│   │   └── utils/
│   │       └── validation.py        # File type, MIME, MR Number & data validators
│   │
│   ├── tests/                       # Pytest test suite
│   │   ├── conftest.py              # Mock fixtures & JWT token generators
│   │   ├── test_auth.py             # Auth & role-based access tests
│   │   ├── test_patients.py         # Patient access & data isolation tests
│   │   ├── test_doctors.py          # Doctor assessments & finalization tests
│   │   ├── test_specialists.py      # Specialist upload & workflow tests
│   │   ├── test_appointments.py     # Appointment booking & status update tests
│   │   └── test_imaging_and_analysis.py # Validation & AI pipeline tests
│   │
│   ├── API_DOCUMENTATION.md         # Comprehensive REST API spec for Person 1 (Frontend)
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Template for required environment variables
│
└── database/
    ├── schema.sql                   # 11 PostgreSQL tables, indexes, UUIDs & triggers
    ├── rls_policies.sql             # Row Level Security (RLS) policies per role
    ├── storage_setup.sql            # Supabase Storage buckets & access policies
    └── seed_data.sql                # Seed data for demo patients, doctors, & cases
```

---

## Database Design (Supabase PostgreSQL)

The database schema is fully normalized and includes 11 relational tables:

1. **`profiles`**: Connected directly with Supabase Auth users (`auth.users`) to enforce roles (`patient`, `doctor`, `specialist`, `admin`).
2. **`patients`**: Patient demographics, unique `mr_number`, age, contact, medical alerts.
3. **`doctors`**: Doctor registry with specialization, department, license number.
4. **`specialists`**: Imaging specialists / technicians for scan intake.
5. **`appointments`**: Patient-doctor appointment booking with status tracking.
6. **`imaging_requests`**: Doctor's prescription for imaging (`xray`, `ct_scan`, `mri`).
7. **`imaging_studies`**: Uploaded scan metadata, file size, MIME type, Supabase Storage path.
8. **`ai_analysis_results`**: Segregated AI findings (Vision findings, confidence scores, GenAI explanation, limitations).
9. **`medical_reports`**: Master report record tracking PDF path and review status.
10. **`doctor_assessments`**: **Strictly separated** doctor conclusions, diagnosis, prescriptions, and recommendations.
11. **`medical_records`**: Permanent visit history populated upon report finalization.

---

## Row Level Security (RLS) Policies

All tables enforce Row Level Security:
- **Patients**: Can only access their own profile, records, and reports once marked `available_to_patient`.
- **Doctors**: Can access patient medical histories, create imaging requests, review AI analyses, submit clinical assessments, and finalize reports.
- **Specialists**: Can view assigned imaging requests, upload scan files to Supabase Storage, but **cannot modify doctor assessments or finalize reports**.
- **Admin**: Administrative oversight across records.

---

## Supabase Storage Setup

Three private storage buckets are configured:
- `medical-images`: Medical scan files (X-Ray, CT, MRI up to 50MB).
- `medical-reports`: Rendered PDF medical reports.
- `analysis-results`: Heatmaps and analytical artifacts.

All file downloads are served via authenticated, time-limited **Signed URLs** to ensure HIPAA-aligned security.

---

## AI Service Integration Interfaces

Clean plug-and-play interfaces are provided for team members:
- **`app/services/vision_service.py`**: Integration point for Person 3 (Vision AI). Accepts image scan and returns `finding`, `location`, `confidence_score`, and `heatmap_storage_path`.
- **`app/services/genai_service.py`**: Integration point for Person 4 (Multimodal AI). Accepts patient context and Vision findings to generate evidence-grounded clinical summaries and limitations.

---

## Quickstart & Local Setup

### 1. Database Setup in Supabase
Run the SQL scripts in your Supabase project's SQL Editor in this order:
1. `database/schema.sql`
2. `database/rls_policies.sql`
3. `database/storage_setup.sql`
4. `database/seed_data.sql` *(optional, for demo accounts)*

### 2. Configure Environment Variables
Copy `backend/.env.example` to `backend/.env` and provide your Supabase credentials:
```bash
cp backend/.env.example backend/.env
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Run the FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs (Swagger): `http://localhost:8000/docs`
- Alternative API Docs (ReDoc): `http://localhost:8000/redoc`

### 5. Run Backend Tests
```bash
pytest -v
```

---

## API Documentation for Frontend (Person 1)

For full REST API specifications, parameters, headers, and request/response JSON payloads, refer to [`backend/API_DOCUMENTATION.md`](backend/API_DOCUMENTATION.md).
