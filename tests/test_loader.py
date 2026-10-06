"""Unit tests for ImageLoader with synthetic DICOMs (zero patient data)."""
from __future__ import annotations

import cv2
import numpy as np
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid
import pytest

from cv.image_loader import ImageLoader
from cv.schemas import LoadedImage


def _create_synthetic_dicom(
    path,
    array: np.ndarray,
    photometric: str = "MONOCHROME2",
    bits: int = 8,
    view_position: str | None = "PA",
    modality: str | None = "CR",
    rescale_slope: float | None = None,
    rescale_intercept: float | None = None,
    window_center: float | None = None,
    window_width: float | None = None,
    phi_tags: dict | None = None,
) -> None:
    """Helper to create synthetic DICOM without any real patient data."""
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(path), {}, file_meta=meta, preamble=b"\0" * 128)
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID

    if modality is not None:
        ds.Modality = modality
    if view_position is not None:
        ds.ViewPosition = view_position

    ds.Rows, ds.Columns = array.shape[:2]
    ds.BitsAllocated = 8 if bits == 8 else 16
    ds.BitsStored = bits
    ds.HighBit = bits - 1
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = photometric
    ds.PixelData = array.tobytes()

    if rescale_slope is not None:
        ds.RescaleSlope = rescale_slope
    if rescale_intercept is not None:
        ds.RescaleIntercept = rescale_intercept
    if window_center is not None:
        ds.WindowCenter = window_center
    if window_width is not None:
        ds.WindowWidth = window_width

    # Optionally inject PHI to verify de-identification scrubbing
    if phi_tags:
        for k, v in phi_tags.items():
            setattr(ds, k, v)

    ds.save_as(str(path))


def test_loader_ready_and_formats():
    loader = ImageLoader()
    assert loader.ready
    assert ".png" in loader.supported_extensions
    assert ".dcm" in loader.supported_extensions


def test_load_standard_png_and_jpg(tmp_path):
    img = (np.random.rand(256, 256, 3) * 255).astype(np.uint8)
    png_path = tmp_path / "test.png"
    jpg_path = tmp_path / "test.jpg"
    cv2.imwrite(str(png_path), img)
    cv2.imwrite(str(jpg_path), img)

    loader = ImageLoader()
    loaded_png = loader.load(png_path)
    assert loaded_png.metadata.format == "png"
    assert loaded_png.metadata.channels == 3

    loaded_jpg = loader.load(jpg_path)
    assert loaded_jpg.metadata.format == "jpg"
    assert loaded_jpg.metadata.channels == 3


def test_load_rgba_drops_alpha(tmp_path):
    # 4-channel image
    rgba = np.full((100, 100, 4), 180, dtype=np.uint8)
    rgba[:, :, 3] = 50  # alpha
    rgba_path = tmp_path / "alpha.png"
    cv2.imwrite(str(rgba_path), rgba)

    loader = ImageLoader()
    loaded = loader.load(rgba_path)
    # Alpha dropped -> 3 channels RGB
    assert loaded.metadata.channels == 3
    assert loaded.image.shape == (100, 100, 3)


def test_load_path_with_spaces_and_special_chars(tmp_path):
    subfolder = tmp_path / "folder with spaces and üñícode"
    subfolder.mkdir()
    img_path = subfolder / "test x-ray.png"
    arr = np.full((128, 128), 120, dtype=np.uint8)
    # Use imencode + tofile so Windows paths with unicode save properly
    success, enc = cv2.imencode(".png", arr)
    assert success
    enc.tofile(str(img_path))

    loader = ImageLoader()
    loaded = loader.load(img_path)
    assert loaded.metadata.width == 128
    assert loaded.metadata.height == 128



def test_load_corrupt_file_raises(tmp_path):
    corrupt_path = tmp_path / "corrupt.png"
    corrupt_path.write_bytes(b"INVALID_HEADER_NOT_AN_IMAGE")

    loader = ImageLoader()
    with pytest.raises(ValueError, match="Failed to decode"):
        loader.load(corrupt_path)



def test_synthetic_dicom_8bit_vs_16bit(tmp_path):
    loader = ImageLoader()

    # 1. 8-bit synthetic DICOM
    arr_8 = (np.arange(10000) % 256).astype(np.uint8).reshape((100, 100))
    p8 = tmp_path / "syn_8bit.dcm"
    _create_synthetic_dicom(p8, arr_8, bits=8)
    loaded_8 = loader.load(p8)
    assert loaded_8.image.dtype == np.uint8
    assert loaded_8.metadata.extra.get("original_bits_stored") == 8

    # 2. 16-bit synthetic DICOM
    arr_16 = np.linspace(0, 65535, 10000, dtype=np.uint16).reshape((100, 100))
    p16 = tmp_path / "syn_16bit.dcm"
    _create_synthetic_dicom(p16, arr_16, bits=16)
    loaded_16 = loader.load(p16)
    assert loaded_16.image.dtype == np.uint8
    assert loaded_16.metadata.extra.get("original_bits_stored") == 16



def test_synthetic_dicom_monochrome1_inversion(tmp_path):
    loader = ImageLoader()
    gradient = np.tile(np.linspace(0, 255, 100, dtype=np.uint8), (100, 1))

    p_mono2 = tmp_path / "mono2.dcm"
    _create_synthetic_dicom(p_mono2, gradient, photometric="MONOCHROME2", bits=8)

    p_mono1 = tmp_path / "mono1.dcm"
    _create_synthetic_dicom(p_mono1, gradient, photometric="MONOCHROME1", bits=8)

    loaded_mono2 = loader.load(p_mono2)
    loaded_mono1 = loader.load(p_mono1)

    # MONOCHROME1 must be inverted relative to MONOCHROME2
    assert np.allclose(loaded_mono1.image, 255 - loaded_mono2.image)


def test_synthetic_dicom_with_and_without_rescale_tags(tmp_path):
    loader = ImageLoader()
    base_arr = np.full((64, 64), 50, dtype=np.uint16)

    # Without rescale tags
    p_no_rescale = tmp_path / "no_rescale.dcm"
    _create_synthetic_dicom(p_no_rescale, base_arr, bits=16)
    loaded_no_rescale = loader.load(p_no_rescale)
    assert loaded_no_rescale.image is not None

    # With rescale tags (slope=2.0, intercept=10.0)
    p_with_rescale = tmp_path / "with_rescale.dcm"
    _create_synthetic_dicom(
        p_with_rescale,
        base_arr,
        bits=16,
        rescale_slope=2.0,
        rescale_intercept=10.0,
        window_center=110.0,
        window_width=50.0,
    )
    loaded_with_rescale = loader.load(p_with_rescale)
    assert loaded_with_rescale.image is not None


def test_synthetic_dicom_missing_optional_tags(tmp_path):
    loader = ImageLoader()
    arr = np.full((128, 128), 100, dtype=np.uint8)
    arr[0, 0] = 0
    arr[1, 1] = 255

    p_minimal = tmp_path / "minimal.dcm"
    # Omit view_position, modality, rescale, and window tags
    _create_synthetic_dicom(
        p_minimal,
        arr,
        bits=8,
        view_position=None,
        modality=None,
        rescale_slope=None,
        rescale_intercept=None,
        window_center=None,
        window_width=None,
    )

    loaded = loader.load(p_minimal)
    assert loaded.metadata.width == 128
    assert loaded.metadata.height == 128
    assert "view_position" not in loaded.metadata.extra
    assert "modality" not in loaded.metadata.extra


def test_privacy_and_phi_scrubbing(tmp_path):
    """Ensure patient demographics and PHI are never retained in metadata."""
    loader = ImageLoader()
    arr = np.full((64, 64), 120, dtype=np.uint8)

    p_phi = tmp_path / "patient_001.dcm"
    phi = {
        "PatientName": "ANONYMOUS^JOHN",
        "PatientID": "PATIENT_9999",
        "PatientBirthDate": "19750512",
        "PatientAge": "050Y",
        "PatientSex": "M",
    }

    _create_synthetic_dicom(p_phi, arr, bits=8, phi_tags=phi)

    loaded = loader.load(p_phi)
    extra = loaded.metadata.extra

    # PHI tags must NEVER appear in extra metadata or serialized output
    forbidden_keys = [
        "PatientName", "PatientID", "PatientBirthDate", "PatientAge", "PatientSex",
        "patient_name", "patient_id", "patient_birth_date", "patient_age", "patient_sex",
        "patientId",
    ]
    for key in forbidden_keys:
        assert key not in extra
        assert key not in loaded.metadata.__dict__


def test_unsupported_format_raises(tmp_path):
    txt_file = tmp_path / "document.txt"
    txt_file.write_text("not an image")
    loader = ImageLoader()
    with pytest.raises(ValueError, match="Unsupported file format"):
        loader.load(txt_file)


def test_missing_file_raises():
    loader = ImageLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("non_existent_file.dcm")
