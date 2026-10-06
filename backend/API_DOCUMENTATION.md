# MediVision AI — Backend API Documentation for Frontend (Person 1)

> **Audience:** Frontend / UI / UX Developer (Person 1)  
> **Backend Host:** Local development default: `http://localhost:8000` (FastAPI Swagger UI available at `http://localhost:8000/docs`)  
> **Auth Header Format:** All authenticated requests must include:  
> `Authorization: Bearer <supabase_jwt_access_token>`

---

## Table of Contents
1. [Overview & Role Hierarchy](#overview--role-hierarchy)
2. [Authentication Endpoints](#1-authentication)
3. [Patients Endpoints](#2-patients)
4. [Doctors Endpoints](#3-doctors)
5. [Specialists Endpoints](#4-specialists)
6. [Appointments Endpoints](#5-appointments)
7. [Imaging Requests & Upload Endpoints](#6-imaging-requests--studies)
8. [AI Analysis Endpoints](#7-ai-analysis)
9. [Medical Reports & Doctor Finalization Endpoints](#8-medical-reports--finalization)
10. [Error Codes & Response Format](#9-standard-error-responses)

---

## Overview & Role Hierarchy

Users belong to one of four roles stored in Supabase:
- `patient`: Can book appointments, view own records, and view own finalized reports.
- `doctor`: Can view all patients, order imaging requests, review AI analyses, submit clinical assessments, and finalize reports.
- `specialist`: Can claim imaging requests, upload medical scans (X-Ray, CT, MRI), and trigger analysis.
- `admin`: Has administrative oversight.

---

## 1. Authentication

### POST `/auth/login`
Authenticate using email and password via Supabase Auth.

- **Auth Required:** No
- **Required Role:** Any
- **Request Body:**
```json
{
  "email": "priya.sharma@demo.com",
  "password": "Password123!"
}
```
- **Response Body (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": "aaaaaaaa-0001-0001-0001-000000000001",
  "role": "patient",
  "full_name": "Priya Sharma",
  "email": "priya.sharma@demo.com"
}
```
- **Error Responses:**
  - `401 Unauthorized`: `{"detail": "Invalid credentials"}`

---

### GET `/auth/me`
Retrieve profile of currently authenticated user.

- **Auth Required:** Yes
- **Required Role:** Any authenticated user
- **Headers:** `Authorization: Bearer <token>`
- **Response Body (`200 OK`):**
```json
{
  "id": "aaaaaaaa-0001-0001-0001-000000000001",
  "role": "doctor",
  "full_name": "Dr. Arun Mehta",
  "email": "arun.mehta@medivision.com",
  "profile_table_id": "d1000000-0000-0000-0000-000000000001"
}
```

---

## 2. Patients

### GET `/patients`
List all registered patients with demographics.

- **Auth Required:** Yes
- **Required Role:** `doctor` or `admin`
- **Response Body (`200 OK`):**
```json
[
  {
    "id": "p1000000-0000-0000-0000-000000000001",
    "mr_number": "MR-2024-0001",
    "full_name": "Priya Sharma",
    "date_of_birth": "1990-05-15",
    "age": 34,
    "gender": "female",
    "phone": "+91-9876543210",
    "email": "priya.sharma@demo.com",
    "blood_group": "O+",
    "allergies": "Penicillin"
  }
]
```
- **Error Responses:**
  - `403 Forbidden`: If called with `patient` or `specialist` role.

---

### GET `/patients/{patient_id}`
Retrieve a specific patient profile by UUID.

- **Auth Required:** Yes
- **Required Role:** `doctor` or `admin`
- **Response Body (`200 OK`):**
```json
{
  "id": "p1000000-0000-0000-0000-000000000001",
  "mr_number": "MR-2024-0001",
  "full_name": "Priya Sharma",
  "date_of_birth": "1990-05-15",
  "age": 34,
  "gender": "female",
  "phone": "+91-9876543210",
  "email": "priya.sharma@demo.com",
  "blood_group": "O+"
}
```

---

### GET `/patients/mr/{mr_number}`
Lookup patient by medical record number (e.g., `MR-2024-0001`).

- **Auth Required:** Yes
- **Required Role:** `doctor`, `specialist`, `admin`
- **Response Body (`200 OK`):**
```json
{
  "id": "p1000000-0000-0000-0000-000000000001",
  "mr_number": "MR-2024-0001",
  "full_name": "Priya Sharma"
}
```
- **Error Responses:**
  - `404 Not Found`: `{"detail": "No patient found with MR Number: MR-2024-0001"}`

---

### GET `/patients/me`
Patient self-retrieval of demographics.

- **Auth Required:** Yes
- **Required Role:** `patient`
- **Response Body (`200 OK`):** Returns the logged-in patient's record.

---

### GET `/patients/me/records`
Patient self-retrieval of past medical records and visits.

- **Auth Required:** Yes
- **Required Role:** `patient`
- **Response Body (`200 OK`):**
```json
[
  {
    "id": "rec-001",
    "patient_id": "p1000000-0000-0000-0000-000000000001",
    "visit_date": "2026-09-29",
    "diagnosis": "Mild thoracolumbar spondylosis",
    "summary": "Conservative management with physiotherapy."
  }
]
```

---

### GET `/patients/me/reports`
Patient self-retrieval of finalized reports.

- **Auth Required:** Yes
- **Required Role:** `patient`
- **Response Body (`200 OK`):**
```json
[
  {
    "id": "rp100000-0000-0000-0000-000000000001",
    "patient_id": "p1000000-0000-0000-0000-000000000001",
    "report_status": "available_to_patient",
    "generated_at": "2026-09-28T10:00:00Z",
    "finalized_at": "2026-09-29T11:00:00Z"
  }
]
```

---

## 3. Doctors

### GET `/doctors`
List all active hospital doctors and specializations.

- **Auth Required:** Yes (any authenticated user)
- **Response Body (`200 OK`):**
```json
[
  {
    "id": "d1000000-0000-0000-0000-000000000001",
    "doctor_name": "Dr. Arun Mehta",
    "specialization": "Pulmonology",
    "department": "Chest & Pulmonary",
    "phone": "+91-9900112233",
    "email": "arun.mehta@medivision.com"
  }
]
```

---

## 4. Specialists

### GET `/specialists`
List imaging specialists and technicians.

- **Auth Required:** Yes
- **Required Role:** `doctor` or `admin`

### GET `/specialists/me`
Current specialist profile.

- **Auth Required:** Yes
- **Required Role:** `specialist`

### GET `/specialists/me/imaging-requests`
List requests awaiting upload or assigned to this specialist.

- **Auth Required:** Yes
- **Required Role:** `specialist`

### PATCH `/specialists/imaging-requests/{request_id}/assign`
Assign the specialist to an imaging order.

---

## 5. Appointments

### POST `/appointments`
Book a doctor consultation.

- **Auth Required:** Yes
- **Request Body:**
```json
{
  "full_name": "Priya Sharma",
  "phone": "+91-9876543210",
  "email": "priya.sharma@demo.com",
  "department": "Chest & Pulmonary",
  "appointment_date": "2026-10-15",
  "appointment_time": "10:30:00",
  "symptoms": "Persistent cough, chest tightness"
}
```
- **Response Body (`201 Created` or `200 OK`):**
```json
{
  "id": "appt-001",
  "status": "pending",
  "appointment_date": "2026-10-15",
  "appointment_time": "10:30:00",
  "symptoms": "Persistent cough, chest tightness"
}
```

### GET `/appointments`
List appointments (filtered by current user role).

### PATCH `/appointments/{appointment_id}`
Update appointment status (`confirmed`, `completed`, `cancelled`).

---

## 6. Imaging Requests & Studies

### POST `/imaging-requests` *(or `/imaging/requests`)*
Doctor creates a diagnostic imaging request.

- **Auth Required:** Yes
- **Required Role:** `doctor` or `admin`
- **Request Body:**
```json
{
  "patient_id": "p1000000-0000-0000-0000-000000000001",
  "imaging_type": "xray",
  "reason": "Evaluate for pneumonia",
  "symptoms": "Fever, shortness of breath",
  "notes": "Urgent chest radiograph requested"
}
```
*(Valid `imaging_type` options: `"xray"`, `"ct_scan"`, `"mri"`)*

- **Response Body (`200 OK`):**
```json
{
  "id": "ir100000-0000-0000-0000-000000000001",
  "patient_id": "p1000000-0000-0000-0000-000000000001",
  "mr_number": "MR-2024-0001",
  "imaging_type": "xray",
  "reason": "Evaluate for pneumonia",
  "status": "requested",
  "requested_at": "2026-10-06T15:00:00Z"
}
```

---

### GET `/imaging-requests` *(or `/imaging/requests`)*
List imaging requests (Role filtered).

- **Doctor:** sees own patient requests.
- **Specialist:** sees pending/assigned requests.

---

### GET `/imaging-requests/{request_id}`
Retrieve imaging request details including patient demographics.

---

### PATCH `/imaging-requests/{request_id}/status`
Update workflow status.

- **Request Body:**
```json
{
  "status": "assigned"
}
```
*(Valid statuses: `requested`, `assigned`, `image_uploaded`, `analysis_pending`, `analyzed`, `report_generated`, `doctor_review`, `completed`)*

---

### POST `/imaging-requests/{request_id}/upload` *(Multipart/Form-Data)*
Specialist uploads the medical scan image. This automatically initiates the AI Vision + GenAI analysis and report generation in the background!

- **Auth Required:** Yes
- **Required Role:** `specialist`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `imaging_type`: `"xray"`, `"ct_scan"`, or `"mri"` (must match the request)
  - `file`: Binary file upload (JPEG, PNG, DICOM, TIFF up to 50MB)
- **Response Body (`200 OK`):**
```json
{
  "study_id": "is100000-0000-0000-0000-000000000001",
  "storage_path": "ir100000-0000-0000-0000-000000000001/chest_xray.png",
  "status": "uploaded",
  "message": "Image uploaded. Analysis has started in the background."
}
```

---

### GET `/imaging/studies/{study_id}/image-url`
Get a secure, signed Supabase Storage URL to display the scan image in the UI.

- **Response Body (`200 OK`):**
```json
{
  "url": "https://<supabase-project>.supabase.co/storage/v1/object/sign/medical-images/ir001/scan.jpg?token=..."
}
```

---

## 7. AI Analysis

### POST `/analysis/{study_id}`
Manually trigger or re-run the Vision AI + GenAI multimodal analysis pipeline.

- **Auth Required:** Yes
- **Required Role:** `doctor`, `specialist`, or `admin`
- **Response Body (`200 OK`):**
```json
{
  "study_id": "is100000-0000-0000-0000-000000000001",
  "analysis_id": "ar100000-0000-0000-0000-000000000001",
  "report_id": "rp100000-0000-0000-0000-000000000001",
  "status": "completed",
  "message": "AI analysis and medical report generated successfully"
}
```

---

### GET `/analysis/{study_id}`
Retrieve raw AI analysis results.

- **Response Body (`200 OK`):**
```json
{
  "id": "ar100000-0000-0000-0000-000000000001",
  "imaging_study_id": "is100000-0000-0000-0000-000000000001",
  "finding": "[DEMO] No acute cardiopulmonary abnormality detected",
  "location": "Bilateral lung fields, cardiac silhouette",
  "confidence_score": 0.82,
  "clinical_context": "Patient context with symptoms",
  "explanation": "Evidence-grounded explanation",
  "limitations": "DEMO AI output. Not clinically validated.",
  "model_name": "mock-vision-v0",
  "model_version": "0.0.1",
  "analysis_status": "completed"
}
```

---

## 8. Medical Reports & Finalization

### GET `/reports`
List all medical reports (Role-filtered).

---

### GET `/reports/{report_id}`
Retrieve full medical report object including patient info, AI findings, and doctor's assessment.

- **Response Body (`200 OK`):**
```json
{
  "id": "rp100000-0000-0000-0000-000000000001",
  "patient_id": "p1000000-0000-0000-0000-000000000001",
  "report_status": "finalized",
  "generated_at": "2026-10-06T15:10:00Z",
  "patients": {
    "full_name": "Priya Sharma",
    "mr_number": "MR-2024-0001",
    "age": 34,
    "gender": "female"
  },
  "imaging_studies": {
    "imaging_type": "xray",
    "original_filename": "chest_xray.png"
  },
  "ai_analysis_results": {
    "finding": "No acute cardiopulmonary abnormality detected",
    "confidence_score": 0.82,
    "location": "Bilateral lung fields"
  },
  "doctor_assessments": {
    "diagnosis": "Mild viral bronchitis",
    "conclusion": "Lungs clear. No acute bacterial consolidation.",
    "medications": "Guaifenesin 200mg TID, Paracetamol 500mg PRN",
    "recommendations": "Rest and hydration"
  }
}
```

---

### GET `/reports/search/{mr_number}`
Doctor searches reports for a specific patient using their MR Number (e.g., `MR-2024-0001`).

- **Auth Required:** Yes
- **Required Role:** `doctor` or `admin`
- **Response Body (`200 OK`):** List of matching reports.

---

### GET `/reports/{report_id}/pdf-url`
Get a signed download URL for the generated PDF medical report.

- **Response Body (`200 OK`):**
```json
{
  "url": "https://<supabase-project>.supabase.co/storage/v1/object/sign/medical-reports/p001/report_MR-2024-0001.pdf?token=..."
}
```

---

### POST `/reports/{report_id}/assessment` *(or `PATCH`)*
Doctor submits clinical assessment for the report.

- **Auth Required:** Yes
- **Required Role:** `doctor`
- **Request Body:**
```json
{
  "conclusion": "Chest radiograph demonstrates clear lung parenchyma without consolidation or effusion.",
  "diagnosis": "Acute Bronchitis (Viral)",
  "medications": "Symptomatic relief: Levocetirizine 5mg at bedtime, Paracetamol 650mg SOS for fever.",
  "recommendations": "Steam inhalation twice daily, adequate oral hydration.",
  "follow_up_instructions": "Review after 5 days if cough or fevers persist.",
  "additional_notes": "Patient advised to seek immediate attention if hemoptysis develops."
}
```
- **Response Body (`200 OK`):** Returns the saved doctor assessment record.

---

### POST `/reports/{report_id}/finalize` *(or `PATCH`)*
Doctor finalizes the report. This updates the report status to `finalized`, seals the timestamp, creates a permanent medical record entry, and completes the imaging request!

- **Auth Required:** Yes
- **Required Role:** `doctor`
- **Response Body (`200 OK`):**
```json
{
  "message": "Report finalized successfully",
  "report_id": "rp100000-0000-0000-0000-000000000001"
}
```

---

### PATCH `/reports/{report_id}/send-to-patient`
Makes the finalized report visible on the patient's portal.

- **Auth Required:** Yes
- **Required Role:** `doctor`
- **Response Body (`200 OK`):**
```json
{
  "message": "Report sent to patient",
  "report_id": "rp100000-0000-0000-0000-000000000001"
}
```

---

## 9. Standard Error Responses

All error responses from FastAPI conform to standard HTTP status codes:

```json
{
  "detail": "Description of the error"
}
```

| HTTP Status | Meaning | Common Cause |
|---|---|---|
| `400 Bad Request` | Invalid payload or parameter | Mismatched imaging type, file size too large (>50MB), or unsupported file type |
| `401 Unauthorized` | Invalid or missing token | Missing or expired `Authorization: Bearer <token>` |
| `403 Forbidden` | Role permission denied | Patient attempting to access doctor-only endpoints or another patient's records |
| `404 Not Found` | Resource does not exist | Invalid ID or MR Number |
| `413 Entity Too Large`| Upload exceeds size limit | Upload file is larger than 50MB |
| `422 Unprocessable` | Pydantic validation error | Missing required fields or incorrect data types |
