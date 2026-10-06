-- ============================================================
-- MediVision AI — Demo Seed Data
-- Run AFTER schema.sql and rls_policies.sql
-- Creates demo accounts (use Supabase Auth to create users first,
-- then run this to add profile/patient/doctor/specialist records)
-- ============================================================

-- ── NOTE: Replace these UUIDs with actual Supabase auth.users IDs
-- after creating demo accounts in Supabase Auth dashboard.
-- Or use the signup endpoint to create them programmatically.

-- Demo auth user IDs (placeholders — replace with real IDs)
-- Patient 1:   'aaaaaaaa-0001-0001-0001-000000000001'
-- Patient 2:   'aaaaaaaa-0002-0002-0002-000000000002'
-- Patient 3:   'aaaaaaaa-0003-0003-0003-000000000003'
-- Doctor 1:    'bbbbbbbb-0001-0001-0001-000000000001'
-- Doctor 2:    'bbbbbbbb-0002-0002-0002-000000000002'
-- Specialist:  'cccccccc-0001-0001-0001-000000000001'

-- ── PROFILES ──────────────────────────────────────────────────
INSERT INTO public.profiles (id, role, full_name) VALUES
    ('aaaaaaaa-0001-0001-0001-000000000001', 'patient',    'Priya Sharma'),
    ('aaaaaaaa-0002-0002-0002-000000000002', 'patient',    'Rajan Kumar'),
    ('aaaaaaaa-0003-0003-0003-000000000003', 'patient',    'Meena Nair'),
    ('bbbbbbbb-0001-0001-0001-000000000001', 'doctor',     'Dr. Arun Mehta'),
    ('bbbbbbbb-0002-0002-0002-000000000002', 'doctor',     'Dr. Sunita Patel'),
    ('cccccccc-0001-0001-0001-000000000001', 'specialist', 'Technician Rajesh Kumar')
ON CONFLICT (id) DO NOTHING;

-- ── PATIENTS ──────────────────────────────────────────────────
INSERT INTO public.patients (id, profile_id, mr_number, full_name, date_of_birth, gender, phone, email, address, blood_group) VALUES
    ('p1000000-0000-0000-0000-000000000001', 'aaaaaaaa-0001-0001-0001-000000000001', 'MR-2024-0001', 'Priya Sharma',  '1990-05-15', 'female', '+91-9876543210', 'priya.sharma@demo.com',  '12, Anna Nagar, Chennai 600040', 'O+'),
    ('p2000000-0000-0000-0000-000000000002', 'aaaaaaaa-0002-0002-0002-000000000002', 'MR-2024-0002', 'Rajan Kumar',   '1978-11-22', 'male',   '+91-9876543211', 'rajan.kumar@demo.com',   '45, T Nagar, Chennai 600017',    'B+'),
    ('p3000000-0000-0000-0000-000000000003', 'aaaaaaaa-0003-0003-0003-000000000003', 'MR-2024-0003', 'Meena Nair',    '1965-03-08', 'female', '+91-9876543212', 'meena.nair@demo.com',    '88, Adyar, Chennai 600020',      'A-')
ON CONFLICT (mr_number) DO NOTHING;

-- ── DOCTORS ───────────────────────────────────────────────────
INSERT INTO public.doctors (id, profile_id, doctor_name, specialization, license_number, phone, email, department) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'bbbbbbbb-0001-0001-0001-000000000001', 'Dr. Arun Mehta',   'Pulmonology',  'TN-MED-001', '+91-9900112233', 'arun.mehta@medivision.com',   'Chest & Pulmonary'),
    ('d2000000-0000-0000-0000-000000000002', 'bbbbbbbb-0002-0002-0002-000000000002', 'Dr. Sunita Patel', 'Neurology',    'TN-MED-002', '+91-9900112244', 'sunita.patel@medivision.com', 'Neurosciences')
ON CONFLICT (license_number) DO NOTHING;

-- ── SPECIALISTS ───────────────────────────────────────────────
INSERT INTO public.specialists (id, profile_id, specialist_name, specialization, department, phone, email) VALUES
    ('s1000000-0000-0000-0000-000000000001', 'cccccccc-0001-0001-0001-000000000001', 'Rajesh Kumar', 'Radiology Technician', 'Medical Imaging', '+91-9900112255', 'rajesh.kumar@medivision.com')
ON CONFLICT DO NOTHING;

-- ── APPOINTMENTS ──────────────────────────────────────────────
INSERT INTO public.appointments (patient_id, doctor_id, full_name, mr_number, symptoms, department, appointment_date, appointment_time, status, phone) VALUES
    ('p1000000-0000-0000-0000-000000000001', 'd1000000-0000-0000-0000-000000000001', 'Priya Sharma', 'MR-2024-0001', 'Persistent cough, chest pain, mild fever for 2 weeks', 'Chest & Pulmonary', CURRENT_DATE + 2, '10:00', 'confirmed', '+91-9876543210'),
    ('p2000000-0000-0000-0000-000000000002', 'd2000000-0000-0000-0000-000000000002', 'Rajan Kumar',  'MR-2024-0002', 'Severe headaches, dizziness, blurred vision', 'Neurosciences', CURRENT_DATE + 3, '14:00', 'pending', '+91-9876543211'),
    ('p3000000-0000-0000-0000-000000000003', 'd1000000-0000-0000-0000-000000000001', 'Meena Nair',   'MR-2024-0003', 'Back pain, difficulty breathing when lying down', 'Chest & Pulmonary', CURRENT_DATE - 5, '09:00', 'completed', '+91-9876543212');

-- ── IMAGING REQUESTS ──────────────────────────────────────────
INSERT INTO public.imaging_requests (id, patient_id, doctor_id, specialist_id, mr_number, imaging_type, reason, symptoms, status, requested_at) VALUES
    -- Pending (awaiting specialist upload)
    ('ir100000-0000-0000-0000-000000000001', 'p1000000-0000-0000-0000-000000000001', 'd1000000-0000-0000-0000-000000000001', NULL, 'MR-2024-0001', 'xray', 'Evaluate for pneumonia/pleural effusion', 'Persistent cough, chest pain, mild fever', 'requested', NOW() - INTERVAL '2 days'),
    -- Completed
    ('ir200000-0000-0000-0000-000000000002', 'p3000000-0000-0000-0000-000000000003', 'd1000000-0000-0000-0000-000000000001', 's1000000-0000-0000-0000-000000000001', 'MR-2024-0003', 'ct_scan', 'Rule out spinal cord compression', 'Back pain, difficulty breathing', 'completed', NOW() - INTERVAL '10 days'),
    -- MRI pending
    ('ir300000-0000-0000-0000-000000000003', 'p2000000-0000-0000-0000-000000000002', 'd2000000-0000-0000-0000-000000000002', 's1000000-0000-0000-0000-000000000001', 'MR-2024-0002', 'mri', 'Evaluate for intracranial pathology', 'Severe headaches, dizziness, blurred vision', 'assigned', NOW() - INTERVAL '1 day');

-- ── IMAGING STUDIES (for completed case) ──────────────────────
INSERT INTO public.imaging_studies (id, imaging_request_id, patient_id, imaging_type, storage_path, original_filename, mime_type, file_size, analysis_status, uploaded_at) VALUES
    ('is100000-0000-0000-0000-000000000001', 'ir200000-0000-0000-0000-000000000002', 'p3000000-0000-0000-0000-000000000003', 'ct_scan', 'ir200000-0000-0000-0000-000000000002/demo_ct_scan.jpg', 'demo_ct_scan.jpg', 'image/jpeg', 2048576, 'completed', NOW() - INTERVAL '9 days');

-- ── AI ANALYSIS RESULTS (for completed case) ──────────────────
INSERT INTO public.ai_analysis_results (id, imaging_study_id, finding, location, confidence_score, clinical_context, explanation, limitations, model_name, model_version, analysis_status) VALUES
    ('ar100000-0000-0000-0000-000000000001', 'is100000-0000-0000-0000-000000000001',
     '[DEMO] No acute spinal cord compression or intervertebral disc herniation identified',
     'Thoracic and lumbar spine, T8-L4 vertebral bodies',
     0.81,
     '[DEMO DATA] 60-year-old female presenting with back pain and difficulty breathing when lying down. CT scan of thoracic and lumbar spine performed.',
     '[DEMO DATA] The CT scan demonstrates no significant bony destruction or spinal canal compromise. Mild degenerative changes noted at T10-T11 and L3-L4 levels consistent with age-related changes.',
     'IMPORTANT: This is a DEMO AI analysis. Results are NOT clinically validated and must NOT be used for medical decisions. All findings require review by a qualified radiologist.',
     'mock-vision-v0', '0.0.1', 'completed');

-- ── MEDICAL REPORTS (for completed case) ──────────────────────
INSERT INTO public.medical_reports (id, patient_id, imaging_study_id, ai_analysis_id, report_pdf_path, report_status, generated_at, reviewed_at, finalized_at, reviewed_by) VALUES
    ('rp100000-0000-0000-0000-000000000001',
     'p3000000-0000-0000-0000-000000000003',
     'is100000-0000-0000-0000-000000000001',
     'ar100000-0000-0000-0000-000000000001',
     'p3000000-0000-0000-0000-000000000003/demo_report_MR-2024-0003.pdf',
     'available_to_patient',
     NOW() - INTERVAL '8 days',
     NOW() - INTERVAL '7 days',
     NOW() - INTERVAL '7 days',
     'd1000000-0000-0000-0000-000000000001');

-- ── DOCTOR ASSESSMENTS (for completed case) ───────────────────
INSERT INTO public.doctor_assessments (report_id, doctor_id, conclusion, diagnosis, medications, recommendations, follow_up_instructions, finalized_at) VALUES
    ('rp100000-0000-0000-0000-000000000001',
     'd1000000-0000-0000-0000-000000000001',
     'CT scan findings are reassuring with no acute pathology identified. Mild degenerative changes consistent with patient age.',
     'Mild thoracolumbar spondylosis. No acute spinal pathology.',
     'Tab. Ibuprofen 400mg twice daily after food (5 days), Tab. Pantoprazole 40mg once daily',
     'Physiotherapy referral advised. Avoid heavy lifting. Regular low-impact exercise recommended.',
     'Review in 4 weeks. Repeat CT if symptoms worsen. Urgent review if neurological symptoms develop.',
     NOW() - INTERVAL '7 days');

-- ── MEDICAL RECORDS (for completed case) ──────────────────────
INSERT INTO public.medical_records (patient_id, report_id, visit_date, diagnosis, summary) VALUES
    ('p3000000-0000-0000-0000-000000000003',
     'rp100000-0000-0000-0000-000000000001',
     CURRENT_DATE - 7,
     'Mild thoracolumbar spondylosis',
     'CT scan performed for back pain evaluation. No acute pathology. Conservative management initiated with physiotherapy referral.');
