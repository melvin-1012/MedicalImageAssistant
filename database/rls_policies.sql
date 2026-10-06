-- ============================================================
-- MediVision AI — Row Level Security Policies
-- Run AFTER schema.sql in Supabase SQL Editor
-- ============================================================

-- ── Enable RLS on all tables ──────────────────────────────────
ALTER TABLE public.profiles         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doctors          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.specialists      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.imaging_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.imaging_studies  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medical_reports  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doctor_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medical_records  ENABLE ROW LEVEL SECURITY;

-- ── Helper functions ──────────────────────────────────────────

-- Get current user's role from profiles
CREATE OR REPLACE FUNCTION auth.user_role()
RETURNS TEXT LANGUAGE sql STABLE AS $$
  SELECT role FROM public.profiles WHERE id = auth.uid()
$$;

-- Get current user's patient_id
CREATE OR REPLACE FUNCTION auth.my_patient_id()
RETURNS UUID LANGUAGE sql STABLE AS $$
  SELECT id FROM public.patients WHERE profile_id = auth.uid()
$$;

-- Get current user's doctor_id
CREATE OR REPLACE FUNCTION auth.my_doctor_id()
RETURNS UUID LANGUAGE sql STABLE AS $$
  SELECT id FROM public.doctors WHERE profile_id = auth.uid()
$$;

-- Get current user's specialist_id
CREATE OR REPLACE FUNCTION auth.my_specialist_id()
RETURNS UUID LANGUAGE sql STABLE AS $$
  SELECT id FROM public.specialists WHERE profile_id = auth.uid()
$$;

-- ── PROFILES ──────────────────────────────────────────────────
DROP POLICY IF EXISTS "Users can view own profile"   ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (id = auth.uid());

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- ── PATIENTS ──────────────────────────────────────────────────
DROP POLICY IF EXISTS "Patients can read own record"    ON public.patients;
DROP POLICY IF EXISTS "Doctors can read all patients"   ON public.patients;
DROP POLICY IF EXISTS "Patients can update own record"  ON public.patients;

CREATE POLICY "Patients can read own record"
    ON public.patients FOR SELECT
    USING (profile_id = auth.uid());

CREATE POLICY "Doctors and specialists can read all patients"
    ON public.patients FOR SELECT
    USING (auth.user_role() IN ('doctor', 'specialist', 'admin'));

CREATE POLICY "Patients can update own record"
    ON public.patients FOR UPDATE
    USING (profile_id = auth.uid())
    WITH CHECK (profile_id = auth.uid());

CREATE POLICY "Backend can insert patients"
    ON public.patients FOR INSERT
    WITH CHECK (auth.user_role() IN ('admin', 'doctor') OR profile_id = auth.uid());

-- ── DOCTORS ───────────────────────────────────────────────────
CREATE POLICY "Authenticated users can view doctors"
    ON public.doctors FOR SELECT
    TO authenticated
    USING (true);

-- ── SPECIALISTS ───────────────────────────────────────────────
CREATE POLICY "Authenticated users can view specialists"
    ON public.specialists FOR SELECT
    TO authenticated
    USING (true);

-- ── APPOINTMENTS ──────────────────────────────────────────────
DROP POLICY IF EXISTS "Patients can view own appointments"  ON public.appointments;
DROP POLICY IF EXISTS "Doctors can view their appointments" ON public.appointments;
DROP POLICY IF EXISTS "Patients can create appointments"    ON public.appointments;

CREATE POLICY "Patients can view own appointments"
    ON public.appointments FOR SELECT
    USING (patient_id = auth.my_patient_id());

CREATE POLICY "Doctors can view their appointments"
    ON public.appointments FOR SELECT
    USING (
        auth.user_role() IN ('doctor', 'admin') AND
        (doctor_id = auth.my_doctor_id() OR auth.user_role() = 'admin')
    );

CREATE POLICY "Authenticated users can create appointments"
    ON public.appointments FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Doctors can update appointment status"
    ON public.appointments FOR UPDATE
    USING (auth.user_role() IN ('doctor', 'admin'));

-- ── IMAGING REQUESTS ──────────────────────────────────────────
CREATE POLICY "Doctors can create imaging requests"
    ON public.imaging_requests FOR INSERT
    WITH CHECK (auth.user_role() IN ('doctor', 'admin'));

CREATE POLICY "Doctors can view their requests"
    ON public.imaging_requests FOR SELECT
    USING (
        auth.user_role() = 'doctor' AND doctor_id = auth.my_doctor_id()
    );

CREATE POLICY "Specialists can view all requests"
    ON public.imaging_requests FOR SELECT
    USING (auth.user_role() IN ('specialist', 'admin'));

CREATE POLICY "Patients can view own imaging requests"
    ON public.imaging_requests FOR SELECT
    USING (patient_id = auth.my_patient_id());

CREATE POLICY "Doctors and specialists can update imaging requests"
    ON public.imaging_requests FOR UPDATE
    USING (auth.user_role() IN ('doctor', 'specialist', 'admin'));

-- ── IMAGING STUDIES ───────────────────────────────────────────
CREATE POLICY "Specialists can upload imaging studies"
    ON public.imaging_studies FOR INSERT
    WITH CHECK (auth.user_role() IN ('specialist', 'admin'));

CREATE POLICY "Doctors and specialists can view imaging studies"
    ON public.imaging_studies FOR SELECT
    USING (auth.user_role() IN ('doctor', 'specialist', 'admin'));

CREATE POLICY "Patients can view own imaging studies"
    ON public.imaging_studies FOR SELECT
    USING (patient_id = auth.my_patient_id());

CREATE POLICY "Specialists can update imaging study status"
    ON public.imaging_studies FOR UPDATE
    USING (auth.user_role() IN ('specialist', 'admin'));

-- ── AI ANALYSIS RESULTS ───────────────────────────────────────
CREATE POLICY "Doctors and specialists can view analysis results"
    ON public.ai_analysis_results FOR SELECT
    USING (auth.user_role() IN ('doctor', 'specialist', 'admin'));

CREATE POLICY "Backend can insert analysis results"
    ON public.ai_analysis_results FOR INSERT
    WITH CHECK (auth.user_role() IN ('specialist', 'admin', 'doctor'));

-- ── MEDICAL REPORTS ───────────────────────────────────────────
CREATE POLICY "Patients can view own finalized reports"
    ON public.medical_reports FOR SELECT
    USING (
        patient_id = auth.my_patient_id() AND
        report_status = 'available_to_patient'
    );

CREATE POLICY "Doctors can view reports for their patients"
    ON public.medical_reports FOR SELECT
    USING (auth.user_role() IN ('doctor', 'admin'));

CREATE POLICY "Backend can insert reports"
    ON public.medical_reports FOR INSERT
    WITH CHECK (auth.user_role() IN ('specialist', 'doctor', 'admin'));

CREATE POLICY "Doctors can update reports"
    ON public.medical_reports FOR UPDATE
    USING (auth.user_role() IN ('doctor', 'admin'));

-- ── DOCTOR ASSESSMENTS ────────────────────────────────────────
CREATE POLICY "Doctors can create/update assessments"
    ON public.doctor_assessments FOR INSERT
    WITH CHECK (auth.user_role() IN ('doctor', 'admin'));

CREATE POLICY "Doctors can update their assessments"
    ON public.doctor_assessments FOR UPDATE
    USING (auth.user_role() IN ('doctor', 'admin'));

CREATE POLICY "Doctors can view all assessments"
    ON public.doctor_assessments FOR SELECT
    USING (auth.user_role() IN ('doctor', 'admin'));

CREATE POLICY "Patients can view assessments on their finalized reports"
    ON public.doctor_assessments FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.medical_reports r
            WHERE r.id = report_id
            AND r.patient_id = auth.my_patient_id()
            AND r.report_status = 'available_to_patient'
        )
    );

-- ── MEDICAL RECORDS ───────────────────────────────────────────
CREATE POLICY "Patients can view own records"
    ON public.medical_records FOR SELECT
    USING (patient_id = auth.my_patient_id());

CREATE POLICY "Doctors can view all medical records"
    ON public.medical_records FOR SELECT
    USING (auth.user_role() IN ('doctor', 'admin'));

CREATE POLICY "Doctors can insert medical records"
    ON public.medical_records FOR INSERT
    WITH CHECK (auth.user_role() IN ('doctor', 'admin'));
