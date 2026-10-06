-- ============================================================
-- MediVision AI — PostgreSQL Schema (Supabase)
-- Run in Supabase SQL Editor or psql
-- ============================================================

-- Enable UUID extension (already enabled in Supabase by default)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ────────────────────────────────────────────────────────────
-- 1. PROFILES (linked to auth.users)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('patient', 'doctor', 'specialist', 'admin')),
    full_name   TEXT,
    avatar_url  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-create profile on signup via trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  INSERT INTO public.profiles (id, role, full_name)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'role', 'patient'),
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  ) ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ────────────────────────────────────────────────────────────
-- 2. PATIENTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.patients (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id      UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    mr_number       TEXT UNIQUE NOT NULL,
    full_name       TEXT NOT NULL,
    date_of_birth   DATE,
    age             INTEGER,
    gender          TEXT CHECK (gender IN ('male', 'female', 'other')),
    phone           TEXT,
    email           TEXT,
    address         TEXT,
    blood_group     TEXT,
    allergies       TEXT,
    emergency_contact TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patients_profile_id ON public.patients(profile_id);
CREATE INDEX IF NOT EXISTS idx_patients_mr_number  ON public.patients(mr_number);

-- ────────────────────────────────────────────────────────────
-- 3. DOCTORS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.doctors (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id      UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    doctor_name     TEXT NOT NULL,
    specialization  TEXT,
    license_number  TEXT UNIQUE,
    phone           TEXT,
    email           TEXT,
    department      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_doctors_profile_id ON public.doctors(profile_id);

-- ────────────────────────────────────────────────────────────
-- 4. SPECIALISTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.specialists (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id      UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    specialist_name TEXT NOT NULL,
    specialization  TEXT,
    department      TEXT,
    phone           TEXT,
    email           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_specialists_profile_id ON public.specialists(profile_id);

-- ────────────────────────────────────────────────────────────
-- 5. APPOINTMENTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.appointments (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id          UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    doctor_id           UUID REFERENCES public.doctors(id) ON DELETE SET NULL,
    full_name           TEXT NOT NULL,
    mr_number           TEXT,
    symptoms            TEXT NOT NULL,
    department          TEXT,
    preferred_doctor    TEXT,
    appointment_date    DATE NOT NULL,
    appointment_time    TIME,
    notes               TEXT,
    phone               TEXT,
    email               TEXT,
    gender              TEXT,
    status              TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON public.appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_id  ON public.appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date       ON public.appointments(appointment_date);

-- ────────────────────────────────────────────────────────────
-- 6. IMAGING REQUESTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.imaging_requests (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    doctor_id       UUID REFERENCES public.doctors(id) ON DELETE SET NULL,
    specialist_id   UUID REFERENCES public.specialists(id) ON DELETE SET NULL,
    mr_number       TEXT,
    imaging_type    TEXT NOT NULL CHECK (imaging_type IN ('xray', 'ct_scan', 'mri')),
    reason          TEXT NOT NULL,
    symptoms        TEXT,
    notes           TEXT,
    status          TEXT NOT NULL DEFAULT 'requested'
                        CHECK (status IN (
                            'requested', 'assigned', 'image_uploaded',
                            'analysis_pending', 'analyzed', 'report_generated',
                            'doctor_review', 'completed'
                        )),
    requested_at    TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_imaging_requests_patient_id  ON public.imaging_requests(patient_id);
CREATE INDEX IF NOT EXISTS idx_imaging_requests_doctor_id   ON public.imaging_requests(doctor_id);
CREATE INDEX IF NOT EXISTS idx_imaging_requests_status      ON public.imaging_requests(status);

-- ────────────────────────────────────────────────────────────
-- 7. IMAGING STUDIES
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.imaging_studies (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    imaging_request_id  UUID REFERENCES public.imaging_requests(id) ON DELETE CASCADE,
    patient_id          UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    imaging_type        TEXT NOT NULL,
    storage_path        TEXT NOT NULL,
    original_filename   TEXT,
    mime_type           TEXT,
    file_size           BIGINT,
    uploaded_by         UUID,
    analysis_status     TEXT DEFAULT 'pending'
                            CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed')),
    uploaded_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_imaging_studies_request_id ON public.imaging_studies(imaging_request_id);
CREATE INDEX IF NOT EXISTS idx_imaging_studies_patient_id ON public.imaging_studies(patient_id);

-- ────────────────────────────────────────────────────────────
-- 8. AI ANALYSIS RESULTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.ai_analysis_results (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    imaging_study_id        UUID REFERENCES public.imaging_studies(id) ON DELETE CASCADE,
    finding                 TEXT,
    location                TEXT,
    confidence_score        FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    heatmap_storage_path    TEXT,
    clinical_context        TEXT,
    explanation             TEXT,
    limitations             TEXT,
    model_name              TEXT,
    model_version           TEXT,
    analysis_status         TEXT DEFAULT 'completed',
    raw_vision_output       JSONB,
    raw_genai_output        JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_results_study_id ON public.ai_analysis_results(imaging_study_id);

-- ────────────────────────────────────────────────────────────
-- 9. MEDICAL REPORTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.medical_reports (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id          UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    imaging_study_id    UUID REFERENCES public.imaging_studies(id) ON DELETE SET NULL,
    ai_analysis_id      UUID REFERENCES public.ai_analysis_results(id) ON DELETE SET NULL,
    report_pdf_path     TEXT,
    report_status       TEXT NOT NULL DEFAULT 'generated'
                            CHECK (report_status IN (
                                'generated', 'under_review', 'finalized', 'available_to_patient'
                            )),
    generated_at        TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at         TIMESTAMPTZ,
    finalized_at        TIMESTAMPTZ,
    reviewed_by         UUID REFERENCES public.doctors(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_patient_id ON public.medical_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_reports_status     ON public.medical_reports(report_status);

-- ────────────────────────────────────────────────────────────
-- 10. DOCTOR ASSESSMENTS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.doctor_assessments (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id               UUID UNIQUE REFERENCES public.medical_reports(id) ON DELETE CASCADE,
    doctor_id               UUID REFERENCES public.doctors(id) ON DELETE SET NULL,
    conclusion              TEXT NOT NULL,
    diagnosis               TEXT NOT NULL,
    medications             TEXT,
    recommendations         TEXT,
    follow_up_instructions  TEXT,
    additional_notes        TEXT,
    finalized_at            TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assessments_report_id ON public.doctor_assessments(report_id);

-- ────────────────────────────────────────────────────────────
-- 11. MEDICAL RECORDS
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.medical_records (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id  UUID REFERENCES public.patients(id) ON DELETE CASCADE,
    report_id   UUID REFERENCES public.medical_reports(id) ON DELETE SET NULL,
    visit_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    diagnosis   TEXT,
    summary     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_records_patient_id ON public.medical_records(patient_id);

-- ============================================================
-- UPDATED_AT TRIGGERS
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE OR REPLACE TRIGGER trg_patients_updated_at BEFORE UPDATE ON public.patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_doctors_updated_at BEFORE UPDATE ON public.doctors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_specialists_updated_at BEFORE UPDATE ON public.specialists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_appointments_updated_at BEFORE UPDATE ON public.appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_imaging_requests_updated_at BEFORE UPDATE ON public.imaging_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_ai_analysis_updated_at BEFORE UPDATE ON public.ai_analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_reports_updated_at BEFORE UPDATE ON public.medical_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_assessments_updated_at BEFORE UPDATE ON public.doctor_assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_medical_records_updated_at BEFORE UPDATE ON public.medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE OR REPLACE TRIGGER trg_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
