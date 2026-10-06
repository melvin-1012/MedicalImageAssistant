"""Unit tests for RSNA Pneumonia Detection dataset inspection and annotation parsing."""
from __future__ import annotations

import csv
from pathlib import Path
import pytest

from cv.dataset import RSNADatasetInspector, DatasetReport
from cv.schemas import BoundingBox


@pytest.fixture
def sample_rsna_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "stage_2_train_labels.csv"
    rows = [
        {"patientId": "patient_001", "x": "", "y": "", "width": "", "height": "", "Target": "0"},
        {"patientId": "patient_002", "x": "150", "y": "200", "width": "120", "height": "180", "Target": "1"},
        {"patientId": "patient_003", "x": "210", "y": "145", "width": "180", "height": "165", "Target": "1"},
        {"patientId": "patient_003", "x": "400", "y": "300", "width": "100", "height": "120", "Target": "1"},
    ]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["patientId", "x", "y", "width", "height", "Target"])
        writer.writeheader()
        writer.writerows(rows)
    return csv_file


def test_parse_annotations_valid(sample_rsna_csv: Path) -> None:
    annotations, errors = RSNADatasetInspector.parse_annotations(sample_rsna_csv)
    assert len(errors) == 0
    assert len(annotations) == 3

    # Negative case
    assert annotations["patient_001"].target == 0
    assert len(annotations["patient_001"].boxes) == 0

    # Single box positive case
    assert annotations["patient_002"].target == 1
    assert len(annotations["patient_002"].boxes) == 1
    b2 = annotations["patient_002"].boxes[0]
    assert b2.x_min == 150.0
    assert b2.y_min == 200.0
    assert b2.x_max == 270.0
    assert b2.y_max == 380.0

    # Multi-box positive case (bilateral pneumonia opacities)
    assert annotations["patient_003"].target == 1
    assert len(annotations["patient_003"].boxes) == 2


def test_parse_annotations_malformed(tmp_path: Path) -> None:
    csv_file = tmp_path / "corrupted_labels.csv"
    rows = [
        {"patientId": "patient_bad1", "x": "-10", "y": "20", "width": "100", "height": "100", "Target": "1"},
        {"patientId": "patient_bad2", "x": "10", "y": "20", "width": "0", "height": "100", "Target": "1"},
        {"patientId": "patient_bad3", "x": "abc", "y": "20", "width": "50", "height": "50", "Target": "1"},
        {"patientId": "patient_bad4", "x": "", "y": "", "width": "", "height": "", "Target": "9"},
    ]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["patientId", "x", "y", "width", "height", "Target"])
        writer.writeheader()
        writer.writerows(rows)

    annotations, errors = RSNADatasetInspector.parse_annotations(csv_file)
    assert len(errors) == 4


def test_parse_annotations_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        RSNADatasetInspector.parse_annotations("non_existent_path.csv")


def test_inspect_missing_directory(tmp_path: Path) -> None:
    missing_dir = tmp_path / "does_not_exist"
    report = RSNADatasetInspector.inspect(missing_dir)
    assert not report.is_available
    assert not report.csv_found
    assert len(report.missing_components) > 0


def test_inspect_directory_with_csv_and_images(tmp_path: Path, sample_rsna_csv: Path) -> None:
    # Create matching dummy files for patient_001 and patient_002
    (tmp_path / "patient_001.dcm").touch()
    (tmp_path / "patient_002.dcm").touch()

    report = RSNADatasetInspector.inspect(tmp_path)
    assert report.csv_found
    assert report.total_patients_in_labels == 3
    assert report.positive_cases == 2
    assert report.negative_cases == 1
    assert report.images_found == 2
    assert report.matched_image_count == 2
    assert report.missing_image_count == 1  # patient_003 DICOM is missing


def test_box_to_yolo_and_reverse() -> None:
    from cv.dataset import RSNAtoYOLOConverter

    # Pixel box in 1024x1024 image
    box = BoundingBox(x_min=256.0, y_min=256.0, x_max=512.0, y_max=768.0)
    # Width = 256.0, Height = 512.0
    # Center_x = (256 + 128) / 1024 = 384 / 1024 = 0.375
    # Center_y = (256 + 256) / 1024 = 512 / 1024 = 0.500
    # Norm_w = 256 / 1024 = 0.250, Norm_h = 512 / 1024 = 0.500

    yolo_str = RSNAtoYOLOConverter.box_to_yolo(box, image_width=1024.0, image_height=1024.0, class_id=0)
    assert yolo_str.startswith("0 0.375000 0.500000 0.250000 0.500000")

    # Roundtrip conversion back to pixel box
    cls_id, restored_box = RSNAtoYOLOConverter.yolo_to_box(yolo_str, image_width=1024.0, image_height=1024.0)
    assert cls_id == 0
    assert pytest.approx(restored_box.x_min, abs=0.1) == 256.0
    assert pytest.approx(restored_box.y_min, abs=0.1) == 256.0
    assert pytest.approx(restored_box.x_max, abs=0.1) == 512.0
    assert pytest.approx(restored_box.y_max, abs=0.1) == 768.0


def test_split_dataset_deterministic_and_leakage_free() -> None:
    from cv.dataset import RSNAtoYOLOConverter

    patients = [f"patient_{i:04d}" for i in range(100)]
    split1 = RSNAtoYOLOConverter.split_dataset(patients, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42)
    split2 = RSNAtoYOLOConverter.split_dataset(patients, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42)

    # Determinism
    assert split1 == split2

    train_set = set(split1["train"])
    val_set = set(split1["val"])
    test_set = set(split1["test"])

    # No leakage between splits
    assert len(train_set.intersection(val_set)) == 0
    assert len(train_set.intersection(test_set)) == 0
    assert len(val_set.intersection(test_set)) == 0

    # Total coverage
    assert len(train_set) + len(val_set) + len(test_set) == 100
    assert len(train_set) == 80
    assert len(val_set) == 10
    assert len(test_set) == 10


def test_convert_annotations_to_yolo_labels_and_yaml(tmp_path: Path, sample_rsna_csv: Path) -> None:
    from cv.dataset import RSNADatasetInspector, RSNAtoYOLOConverter

    annotations, _ = RSNADatasetInspector.parse_annotations(sample_rsna_csv)
    splits = RSNAtoYOLOConverter.split_dataset(list(annotations.keys()), train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, seed=42)

    counts = RSNAtoYOLOConverter.convert_annotations_to_yolo_labels(annotations, splits, tmp_path)
    assert sum(counts.values()) == 3

    # Negative scan produces empty file
    patient_001_path = tmp_path / "labels" / "train" / "patient_001.txt"
    if not patient_001_path.exists():
        patient_001_path = tmp_path / "labels" / "val" / "patient_001.txt"
    if not patient_001_path.exists():
        patient_001_path = tmp_path / "labels" / "test" / "patient_001.txt"

    assert patient_001_path.exists()
    assert patient_001_path.read_text(encoding="utf-8").strip() == ""

    # Generate dataset YAML
    yaml_path = RSNAtoYOLOConverter.generate_yolo_yaml(tmp_path)
    assert yaml_path.exists()
    content = yaml_path.read_text(encoding="utf-8")
    assert "possible_abnormal_opacity" in content
    assert "train: images/train" in content

