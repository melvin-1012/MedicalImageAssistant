-- ============================================================
-- MediVision AI — Storage Bucket Setup
-- Run in Supabase SQL Editor
-- ============================================================

-- Create storage buckets (if using SQL; alternatively create via Supabase Dashboard)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
    ('medical-images', 'medical-images', false, 52428800,  -- 50MB
     ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/dicom', 'application/dicom']),
    ('medical-reports', 'medical-reports', false, 10485760,  -- 10MB
     ARRAY['application/pdf']),
    ('analysis-results', 'analysis-results', false, 10485760,
     ARRAY['image/jpeg', 'image/png', 'application/json'])
ON CONFLICT (id) DO NOTHING;

-- ── Storage Policies ──────────────────────────────────────────

-- medical-images: specialists upload, doctors/specialists read
CREATE POLICY "Specialists can upload medical images"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'medical-images'
        AND (auth.uid() IS NOT NULL)
    );

CREATE POLICY "Authorized users can read medical images"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'medical-images'
        AND auth.uid() IS NOT NULL
    );

-- medical-reports: backend uploads, authenticated users read own
CREATE POLICY "Backend can upload medical reports"
    ON storage.objects FOR INSERT
    WITH CHECK (bucket_id = 'medical-reports');

CREATE POLICY "Authenticated users can read reports"
    ON storage.objects FOR SELECT
    USING (
        bucket_id = 'medical-reports'
        AND auth.uid() IS NOT NULL
    );

-- analysis-results: backend only
CREATE POLICY "Backend can manage analysis results"
    ON storage.objects FOR ALL
    USING (bucket_id = 'analysis-results');
