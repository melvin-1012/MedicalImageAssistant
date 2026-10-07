# MediSight AI — Multimodal Medical Image Intelligence System

**HNX26 · Team: The Unscripted · Hacknex 2026**

> An end-to-end AI-powered clinical decision support system for hospitals. Doctors request imaging studies, specialists upload X-rays, and a three-layer AI pipeline — Computer Vision, DenseNet-121 classification, and a Groq LLM — analyzes the scans and generates evidence-grounded clinical explanations. The attending physician reviews the AI findings, writes their own conclusion, and a secure PDF report is generated for the patient.

**The AI does not replace the doctor. It acts as a second pair of eyes.**

---

## What This Project Does

MediSight AI handles the full clinical imaging workflow:

```
Patient registers → Doctor requests scan → Specialist uploads X-ray
                                                      ↓
                              ┌───────────────────────────────────┐
                              │         AI Pipeline               │
                              │  1. Computer Vision (YOLO)        │
                              │     → Bounding boxes + heatmap    │
                              │  2. Classification (DenseNet-121) │
                              │     → Disease probabilities       │
                              │  3. GenAI (Groq LLM)             │
                              │     → Clinical explanation        │
                              └───────────────────────────────────┘
                                                      ↓
                    Doctor reviews AI findings → Writes conclusion
                                                      ↓
                              PDF Medical Report generated
                                                      ↓
                              Patient downloads report from portal
```

### Key Features

- **Role-Based Access Control** — Separate dashboards and permissions for Patients, Doctors, Specialists, and Admins
- **Secure Medical Storage** — X-rays, CT scans, and MRIs stored in private Supabase Storage buckets with time-limited signed URLs
- **Three-Layer AI Analysis** — YOLO detection + DenseNet-121 classification + LLM explanation running in sequence
- **Evidence-Grounded Explanations** — The LLM links imaging findings directly to the patient's symptoms and clinical notes
- **AI Safety Guarantees** — Confidence scores and bounding boxes are never altered by the LLM; every output explicitly requires physician review
- **PDF Report Generation** — Auto-generated, printable medical reports combining AI findings and physician conclusions
- **Full Audit Trail** — Permanent medical records created upon report finalization

---

## Technologies, Libraries, and Models

### Frontend
| Component | Technology |
|-----------|-----------|
| UI | HTML5, CSS3, Vanilla JavaScript |
| Layout | CSS Grid / Flexbox (responsive) |
| Server | Python `http.server` (`serve.py`) |

### Backend & API
| Component | Technology |
|-----------|-----------|
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Language | Python 3.10+ |
| Data Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| PDF Generation | ReportLab |
| Testing | Pytest (47+ tests) |

### Database, Auth & Storage
| Component | Technology |
|-----------|-----------|
| Database | [Supabase](https://supabase.com/) (PostgreSQL) |
| Authentication | Supabase Auth (JWT-based) |
| Row Level Security | Supabase RLS policies (11 tables) |
| File Storage | Supabase Storage (private buckets, signed URLs) |

### AI & Machine Learning
| Model | Library | Purpose |
|-------|---------|---------|
| **YOLO** | Ultralytics | Object detection — bounding boxes for suspected abnormalities |
| **DenseNet-121** | [TorchXRayVision](https://github.com/mlmed/torchxrayvision) | Image classification — probabilities for 18 chest pathologies |
| **GPT-OSS-120B** (via Groq) | `groq` + `instructor` | Clinical explanation generation from imaging + patient notes |
| Image Processing | OpenCV, NumPy, PyDicom | Preprocessing, quality assessment, heatmaps |

---

## Repository Structure

```
MedicalImageAssistant/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entrypoint & middleware
│   │   ├── config.py                # Environment config (Pydantic BaseSettings)
│   │   ├── database.py              # Supabase client
│   │   ├── dependencies.py          # JWT verification & role authorization
│   │   ├── routers/                 # REST API endpoints
│   │   │   ├── auth.py              # Login, token validation
│   │   │   ├── patients.py          # Patient directory
│   │   │   ├── doctors.py           # Doctor registry
│   │   │   ├── specialists.py       # Specialist operations
│   │   │   ├── appointments.py      # Appointment scheduling
│   │   │   ├── imaging.py           # Imaging request lifecycle & uploads
│   │   │   ├── analysis.py          # AI analysis trigger & lookup
│   │   │   └── reports.py           # PDF report generation & finalization
│   │   ├── services/
│   │   │   ├── vision_service.py    # Interface for CV module (Person 3)
│   │   │   ├── genai_service.py     # Interface for GenAI module (Person 4)
│   │   │   ├── imaging_service.py   # Imaging pipeline orchestration
│   │   │   ├── pdf_service.py       # PDF compilation
│   │   │   └── storage_service.py   # Supabase Storage operations
│   │   └── schemas/                 # Pydantic request/response schemas
│   ├── tests/                       # Pytest test suite
│   ├── requirements.txt
│   ├── .env.example
│   └── API_DOCUMENTATION.md         # Full REST API spec for frontend
│
├── database/
│   ├── schema.sql                   # 11 PostgreSQL tables, indexes & triggers
│   ├── rls_policies.sql             # Row Level Security policies per role
│   ├── storage_setup.sql            # Supabase Storage buckets & access policies
│   └── seed_data.sql                # Demo patients, doctors & cases
│
├── genai_module/                    # GenAI reasoning module (Person 4)
│   ├── pipeline.py                  # Main orchestrator
│   ├── notes_processor.py           # Extracts symptoms from clinical notes
│   ├── explanation_generator.py     # LLM-based clinical explanation
│   ├── evidence_validator.py        # Safety validation
│   ├── ai_response_schema.py        # Pydantic schemas (data contracts)
│   ├── api_router.py                # FastAPI router for Person 2
│   ├── test_cases.py                # 4 end-to-end test scenarios
│   └── requirements.txt
│
└── frontend/                        # HTML/CSS/JS UI (Person 1)
    ├── index.html
    ├── dashboard.html
    └── serve.py
```

---

## How to Install Dependencies

### Prerequisites
- Python 3.10+
- A [Supabase](https://supabase.com/) project (free tier works)
- A [Groq Cloud](https://console.groq.com/) API key (free tier works)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/melvin-1012/MedicalImageAssistant.git
cd MedicalImageAssistant
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Install GenAI Module Dependencies

```bash
cd ../genai_module
pip install -r requirements.txt
```

### Step 5: Install Computer Vision Dependencies (for CV module only)

```bash
pip install torch torchvision torchxrayvision ultralytics opencv-python numpy pydicom streamlit
```

---

## How to Configure and Run the System

### Step 1: Set Up the Supabase Database

Run the following SQL scripts in your **Supabase SQL Editor** in this exact order:

```
1. database/schema.sql          ← Creates 11 tables, indexes & triggers
2. database/rls_policies.sql    ← Applies Row Level Security per role
3. database/storage_setup.sql   ← Creates private storage buckets
4. database/seed_data.sql       ← (Optional) Seeds demo accounts
```

### Step 2: Configure Environment Variables

Copy the example `.env` file in the `backend/` folder:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
GROQ_API_KEY=your-groq-api-key
```

Also create `genai_module/.env`:

```env
GROQ_API_KEY=your-groq-api-key
```

### Step 3: Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Step 4: Start the Frontend

Open a new terminal in the project root:

```bash
python serve.py
```

- Frontend Portal: [http://localhost:8080](http://localhost:8080)

---

## How to Reproduce the Demonstrated Results

Follow the full end-to-end clinical workflow:

### 1. Patient Registration
- Navigate to `http://localhost:8080`
- Click **Patient Registration** and create an account
- The system auto-generates a unique MR Number (e.g. `MR-2024-1234`)

### 2. Doctor Orders an Imaging Study
- Log in as a Doctor (create a user in Supabase Auth dashboard, set role to `doctor`, link in `doctors` table)
- In the Doctor Dashboard, locate the patient and click **Refer to Specialist**
- Enter symptoms and select imaging type (e.g., `Chest X-Ray`)

### 3. Specialist Uploads the Scan
- Log in as a Specialist
- View the pending imaging request in the queue
- Upload a chest X-ray (JPEG/PNG/DICOM — max 50MB)
- File is securely stored in the Supabase `medical-images` bucket

### 4. AI Pipeline Runs Automatically
The backend triggers the full 3-layer AI analysis:

| Layer | What Happens |
|-------|-------------|
| **YOLO** | Detects bounding boxes around suspected opacities in the X-ray |
| **DenseNet-121** | Classifies probabilities for 18 chest pathologies |
| **Groq LLM** | Generates a clinical explanation linking findings to patient symptoms |

Results are saved to the `ai_analysis_results` table in Supabase.

### 5. Doctor Reviews AI Findings
- Switch back to the Doctor Dashboard
- Open the patient's pending report
- Review AI findings, bounding boxes, confidence scores, and the LLM explanation
- Write your **Physician Conclusion** and submit the assessment

### 6. PDF Report Generated
- The backend merges patient data, AI findings, and the physician assessment
- A PDF Medical Report is generated and stored in the `medical-reports` bucket
- The patient can now log in to their portal and securely download their report

---

### Testing the GenAI Module Independently

```bash
python -m genai_module.test_cases
```

**Expected:** 4 structured JSON responses, all with `"is_valid": true`:
- Test 1: Standard run with findings + clinical notes
- Test 2: Poor quality image (fast-fail, no LLM called)
- Test 3: Normal image with no findings
- Test 4: Multiple findings with no clinical notes

### Running the Backend Tests

```bash
cd backend
pytest -v
```

**Expected:** 47+ tests passing.

---

## Database Schema Overview

The database has 11 normalized PostgreSQL tables:

| Table | Purpose |
|-------|---------|
| `profiles` | Linked to Supabase Auth users; stores role (`patient`, `doctor`, `specialist`, `admin`) |
| `patients` | Demographics, MR number, medical alerts |
| `doctors` | Registry with specialization, department, license |
| `specialists` | Imaging technicians for scan intake |
| `appointments` | Patient-doctor scheduling with status tracking |
| `imaging_requests` | Doctor's prescription for imaging (X-ray, CT, MRI) |
| `imaging_studies` | Uploaded scan metadata and Supabase Storage path |
| `ai_analysis_results` | Vision findings, confidence scores, GenAI explanation |
| `medical_reports` | Master report record, PDF path, review status |
| `doctor_assessments` | Physician's conclusion, diagnosis, prescriptions |
| `medical_records` | Permanent visit history upon finalization |

---

## Medical Safety Guarantees

- ✅ **No hallucination** — LLM cannot add findings not detected by the CV model
- ✅ **Confidence scores preserved** — Never altered by the LLM
- ✅ **Bounding boxes preserved** — Coordinates passed through exactly from YOLO
- ✅ **Physician review mandatory** — Every AI output explicitly requires human review
- ✅ **Quality gate** — Poor quality images are rejected before any AI model is invoked
- ✅ **Schema validation** — All outputs validated against strict Pydantic schemas
- ✅ **RLS enforced** — Patients can only see their own records at the database level

---

## Branch Guide

| Branch | Owner | Status |
|--------|-------|--------|
| `main` | All | Stable, merged code |
| `Multimodal-AI` | Person 4 | GenAI reasoning module |
| `Computer-Vision-V1` | Person 3 | YOLO + DenseNet-121 CV pipeline |
| `ilakkiya-frontend` | Person 1 | HTML/CSS/JS frontend UI |
| `Database` | Person 2 | FastAPI backend + Supabase database |

---

## Team

| Person | Role |
|--------|------|
| Person 1 | Frontend (HTML/CSS/JS Portal) |
| Person 2 | Backend API + Supabase Database + PDF Generation |
| Person 3 | Computer Vision (YOLO + DenseNet-121) |
| Person 4 | GenAI Reasoning Module (Groq LLM + Instructor) |
