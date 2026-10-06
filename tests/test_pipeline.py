"""Unit tests for MedicalCVPipeline."""
from __future__ import annotations

import json
from pathlib import Path
import cv2
import numpy as np
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

from cv.pipeline import MedicalCVPipeline
from cv.schemas import AnalysisStatus, CVAnalysisResult, QualityLevel


def _create_test_dicom(path: Path, array: np.ndarray | None = None) -> None:
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(path), {}, file_meta=meta, preamble=b"\0" * 128)
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
    ds.Modality = "CR"
    ds.ViewPosition = "PA"

    if array is None:
        array = (np.random.rand(512, 512) * 200 + 30).astype(np.uint8)

    ds.Rows, ds.Columns = array.shape[:2]
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelData = array.tobytes()
    ds.save_as(str(path))


def test_pipeline_initializes_without_model():
    p = MedicalCVPipeline()
    p.initialize()
    assert p.detector.is_loaded is False


def test_result_serialises_to_json():
    data = json.loads(CVAnalysisResult().to_json())
    assert data["status"] == "not_run"
    assert data["detections"] == []


def test_pipeline_run_phases_1_to_3(tmp_path):
    dcm_path = tmp_path / "valid_test.dcm"
    _create_test_dicom(dcm_path)

    pipeline = MedicalCVPipeline()
    pipeline.initialize()

    # Pass tmp_path so outputs stay in temp directory
    result = pipeline.run(dcm_path, output_dir=tmp_path)

    assert result.status == AnalysisStatus.OK
    assert result.metadata is not None
    assert result.metadata.format == "dcm"
    assert result.metadata.width == 512
    assert result.metadata.height == 512

    # Phase 3 Quality
    assert result.quality is not None
    assert result.quality.level in ("GOOD", "MODERATE", "POOR")
    assert result.quality.score > 0.0

    # Phase 2 Preprocessed output & comparison image
    assert result.visualization is not None
    assert result.visualization.processed_path is not None
    assert Path(result.visualization.processed_path).exists()
    assert result.visualization.comparison_path is not None
    assert Path(result.visualization.comparison_path).exists()

    # Outputs strictly written to tmp_path
    assert tmp_path in Path(result.visualization.processed_path).parents
    assert tmp_path in Path(result.visualization.comparison_path).parents

    # Model inference untouched in Batch 1
    assert result.model_loaded is False
    assert result.detections == []

    # JSON export
    json_str = result.to_json()
    parsed = json.loads(json_str)
    assert parsed["status"] == "ok"


def test_pipeline_rejects_blank_image(tmp_path):
    blank_dcm = tmp_path / "blank.dcm"
    _create_test_dicom(blank_dcm, array=np.zeros((512, 512), dtype=np.uint8))

    pipeline = MedicalCVPipeline()
    result = pipeline.run(blank_dcm, output_dir=tmp_path)

    assert result.status == AnalysisStatus.REJECTED
    assert any("blank" in err for err in result.errors)


def test_pipeline_continues_with_warning_on_poor_quality(tmp_path):
    """Rule: POOR quality does NOT reject the image; adds warning and continues."""
    # Structural image with low contrast (std ~9.8 > blank threshold 2.0, but < min_contrast 25.0)
    poor_img = np.full((512, 512), 100, dtype=np.uint8)
    poor_img[:, 256:] = 120
    poor_img = cv2.GaussianBlur(poor_img, (31, 31), 10.0)
    poor_dcm = tmp_path / "poor_quality.dcm"
    _create_test_dicom(poor_dcm, array=poor_img)

    pipeline = MedicalCVPipeline()
    result = pipeline.run(poor_dcm, output_dir=tmp_path)


    # Status must be OK, not rejected
    assert result.status == AnalysisStatus.OK
    assert result.quality is not None
    assert result.quality.level == QualityLevel.POOR
    assert len(result.warnings) > 0
    assert len(result.errors) == 0



def test_pipeline_handles_missing_file_without_crash(tmp_path):
    pipeline = MedicalCVPipeline()
    missing_path = tmp_path / "non_existent.png"
    result = pipeline.run(missing_path, output_dir=tmp_path)

    assert result.status == AnalysisStatus.REJECTED
    assert any("does not exist" in err for err in result.errors)
