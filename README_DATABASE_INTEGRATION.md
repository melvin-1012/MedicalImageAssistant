# Database & Backend Integration Documentation

This document provides a comprehensive overview of all the work completed in the backend and database layer of the **MediVision AI** repository. It outlines the schema, backend architecture, GenAI/Vision AI pipelines, and the complete authentication flow.

---

## 1. Supabase Database Schema

The core database consists of **11 PostgreSQL tables**, fully normalized and secured.
These tables have been successfully executed in the live Supabase project.

1. **`profiles`**: Linked to Supabase `auth.users`. Stores the user's role (`patient`, `doctor`, `specialist`, `admin`) and basic info.
2. **`patients`**: Stores patient-specific data, including a unique **MR Number** (Medical Record Number).
3. **`doctors`** & **`specialists`**: Separate tables for clinical and imaging staff.
4. **`appointments`**: Consultation bookings.
5. **`imaging_requests`**: Requests created by doctors for specific imaging (`xray`, `ct_scan`, `mri`).
6. **`imaging_studies`**: Represents the actual image upload by a specialist, containing the Supabase Storage bucket path.
7. **`ai_analysis_results`**: Stores the structured output from both the **Vision AI** and **Multimodal GenAI** engines.
8. **`medical_reports`**: Master record containing the final generated PDF report path.
9. **`doctor_assessments`**: Stores the human-in-the-loop clinical conclusion and diagnosis provided by the doctor.
10. **`medical_records`**: A permanent historical record generated after a medical report is finalized.

### Triggers
- **`on_auth_user_created`**: A PostgreSQL trigger automatically creates a `profiles` row whenever a new user signs up via Supabase Auth.
- **`updated_at` Triggers**: Automatically updates the `updated_at` timestamp across all tables whenever a row is modified.

### Row Level Security (RLS)
Security is enforced at the database layer. 
- **Patients** can only read their own records and finalized reports.
- **Doctors** can view patient records, submit assessments, and finalize reports.
- **Specialists** can upload imaging studies and update imaging requests, but cannot alter reports or doctor assessments.

### Supabase Storage
Two main buckets are configured:
1. `medical-images`: For raw DICOM/JPEG uploads.
2. `medical-reports`: For the finalized PDF documents.

---

## 2. FastAPI Backend Architecture

The backend is built with **FastAPI** (`backend/app/main.py`) and is organized into functional routers, keeping concerns separated:

- **`/auth/`**: Registration, login (Email & MR Number support), and JWT token management.
- **`/patients/`**: Patient directory, creation, and profile retrieval.
- **`/doctors/`** & **`/specialists/`**: Clinical staff management and role-specific views.
- **`/appointments/`**: Appointment scheduling.
- **`/imaging/`**: Handles the upload of medical images directly to Supabase Storage.
- **`/analysis/`**: Triggers the AI pipeline manually or fetches analysis status.
- **`/reports/`**: PDF generation, doctor assessment submission, and report finalization.

### Security
- **No plaintext passwords** are stored in our custom tables. All passwords and session tokens are securely handled by Supabase Auth.
- **Dependencies**: `app.dependencies` enforces role-based access control (RBAC). For example, `require_doctor` ensures only authenticated doctors can access certain endpoints.

---

## 3. Authentication Flow Implementation

The authentication flow tightly integrates the Frontend UI with FastAPI and Supabase Auth.

- **Doctor Login**: Doctors authenticate using their email and password. The backend verifies their role against the `profiles` table. Unauthorized users are blocked with an HTTP 403.
- **New Patient Signup**: 
  1. The user registers with Name, Email, and Password.
  2. Supabase Auth creates the secure user identity.
  3. The `on_auth_user_created` trigger provisions their profile.
  4. The FastAPI backend automatically generates a secure, unique **MR Number** (e.g., `MR-2024-8192`) and inserts a row into the `patients` table.
- **Returning Patient Login (MRN Support)**: 
  Patients can log in using either their **Email** OR their **MR Number**. If an MR Number is provided, the backend seamlessly queries the database to resolve it to the associated email address, and then authenticates against Supabase Auth.

---

## 4. AI Pipeline Integrations

The backend successfully merges the work of the AI team members into a single, cohesive asynchronous pipeline orchestrated by `imaging_service.py`.

### Vision AI (Computer Vision)
- Integrated from `origin/Computer-Vision-V1`.
- Housed in `backend/app/services/vision_service.py`.
- **Flow**: Downloads the patient's image from Supabase Storage into a temporary file -> Passes the image through the `MedicalCVPipeline` -> Extracts the highest-confidence finding, bounding box location, and model metadata.

### Multimodal GenAI
- Integrated via `genai_module/` using the Groq LLaMA 3.2 90B Vision model.
- Housed in `backend/app/services/genai_service.py`.
- **Flow**: Takes the structured output from the Vision AI and the patient's clinical context (age, gender, symptoms) -> Prompts the GenAI model -> Returns a structured, evidence-grounded clinical explanation and explicit AI limitations.

Both AI results are then unified and saved to the `ai_analysis_results` PostgreSQL table.

---

## 5. Testing & Verification

A robust test suite of **47 Pytest tests** validates the entire backend architecture.
Run the tests locally via:
```bash
pytest backend/tests/ -v
```

The tests cover:
- Authentication & Role-based Authorization.
- Database CRUD operations and Supabase Client initialization.
- Medical image validation (MIME types, size limits, MRN formatting).
- E2E routing of the AI Pipeline (with mock fallbacks to prevent test failure without API keys).
- Doctor assessment and Report generation logic.

---

## Next Steps / Getting Started

1. Set up your `.env` variables in `backend/.env` containing your live `SUPABASE_URL`, `SUPABASE_KEY` (Anon Key), and `GROQ_API_KEY`.
2. Start the FastAPI backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
3. Open `http://localhost:8000/docs` to view the Swagger API Documentation.
4. Start the Frontend (if running locally):
   ```bash
   python serve.py
   ```
   Navigate to `http://localhost:8080` to access the Patient Portal and Doctor Dashboard.
