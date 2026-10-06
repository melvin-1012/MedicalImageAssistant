"""Dataset inspection, annotation parsing, and YOLO dataset preparation for the RSNA Pneumonia Detection Challenge.

Encapsulates:
- Parsing stage_2_train_labels.csv (patientId, x, y, width, height, Target)
- Validation of coordinates and integrity checks
- Converting RSNA bounding boxes to normalized YOLO format (class_id center_x center_y width height)
- Reproducible, leakage-free patient-level train/val/test splits (80/10/10) with fixed seed
- Generating YOLO dataset configuration YAML
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
import random
from typing import Any, Dict, List, Optional, Tuple

from cv.schemas import BoundingBox
from utils.logger import get_logger

logger = get_logger("dataset")

CLASS_NAME = "possible_abnormal_opacity"
DEFAULT_SPLIT_SEED = 42


@dataclass
class RSNAAnnotation:
    """Parsed annotations for a single patient."""
    patient_id: str
    target: int  # 0 = Normal / No opacity, 1 = Lung opacity present
    boxes: List[BoundingBox] = field(default_factory=list)
    detailed_class: Optional[str] = None


@dataclass
class DatasetReport:
    """Summary report from inspecting a dataset directory."""
    dataset_path: str
    is_available: bool = False
    csv_found: bool = False
    images_found: int = 0
    total_patients_in_labels: int = 0
    positive_cases: int = 0
    negative_cases: int = 0
    total_bounding_boxes: int = 0
    matched_image_count: int = 0
    missing_image_count: int = 0
    malformed_rows_count: int = 0
    missing_components: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=" * 65,
            "RSNA PNEUMONIA DETECTION DATASET INSPECTION REPORT",
            "=" * 65,
            f"Dataset Path              : {self.dataset_path}",
            f"Dataset Available         : {'YES' if self.is_available else 'NO'}",
            f"Annotation CSV Found      : {'YES' if self.csv_found else 'NO'}",
            f"DICOM Images Located      : {self.images_found}",
            f"Total Unique Patients     : {self.total_patients_in_labels}",
            f"Positive Cases (Target=1) : {self.positive_cases}",
            f"Negative Cases (Target=0) : {self.negative_cases}",
            f"Total Bounding Boxes      : {self.total_bounding_boxes}",
            f"Matched DICOM Scans       : {self.matched_image_count}",
            f"Missing DICOM Scans       : {self.missing_image_count}",
            f"Malformed Annotation Rows : {self.malformed_rows_count}",
        ]
        if self.missing_components:
            lines.append("\nMissing Components:")
            for item in self.missing_components:
                lines.append(f"  - {item}")
        if self.issues:
            lines.append("\nIssues Identified:")
            for issue in self.issues:
                lines.append(f"  - {issue}")
        lines.append("=" * 65)
        return "\n".join(lines)


class RSNADatasetInspector:
    """Inspector and parser for RSNA Pneumonia Detection dataset."""

    @staticmethod
    def parse_annotations(csv_path: Path | str) -> Tuple[Dict[str, RSNAAnnotation], List[str]]:
        """Parse stage_2_train_labels.csv into a mapping of patientId -> RSNAAnnotation.

        Expected CSV columns:
            patientId, x, y, width, height, Target
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"Annotation file not found: {csv_file}")

        annotations: Dict[str, RSNAAnnotation] = {}
        errors: List[str] = []

        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]
            required_cols = {"patientId", "Target"}
            if not required_cols.issubset(set(fieldnames)):
                raise ValueError(
                    f"Invalid RSNA CSV schema in {csv_file.name}. Expected columns: {required_cols}, found: {fieldnames}"
                )

            for row_idx, row in enumerate(reader, start=2):
                patient_id = row.get("patientId", "").strip()
                if not patient_id:
                    errors.append(f"Row {row_idx}: Missing patientId")
                    continue

                target_str = row.get("Target", "").strip()
                try:
                    target = int(target_str)
                    if target not in (0, 1):
                        raise ValueError(f"Target must be 0 or 1, got {target}")
                except ValueError as err:
                    errors.append(f"Row {row_idx} ({patient_id}): Invalid Target value '{target_str}': {err}")
                    continue

                if patient_id not in annotations:
                    annotations[patient_id] = RSNAAnnotation(patient_id=patient_id, target=target)
                elif annotations[patient_id].target != target:
                    errors.append(
                        f"Row {row_idx} ({patient_id}): Target mismatch ({annotations[patient_id].target} vs {target})"
                    )

                if target == 1:
                    x_str = row.get("x", "").strip()
                    y_str = row.get("y", "").strip()
                    w_str = row.get("width", "").strip()
                    h_str = row.get("height", "").strip()

                    try:
                        x = float(x_str)
                        y = float(y_str)
                        w = float(w_str)
                        h = float(h_str)

                        if w <= 0 or h <= 0:
                            errors.append(f"Row {row_idx} ({patient_id}): Non-positive box dimensions (w={w}, h={h})")
                            continue
                        if x < 0 or y < 0:
                            errors.append(f"Row {row_idx} ({patient_id}): Negative box coordinates (x={x}, y={y})")
                            continue

                        box = BoundingBox(
                            x_min=float(x),
                            y_min=float(y),
                            x_max=float(x + w),
                            y_max=float(y + h),
                        )
                        annotations[patient_id].boxes.append(box)
                    except ValueError as err:
                        errors.append(f"Row {row_idx} ({patient_id}): Malformed box coordinate values: {err}")

        return annotations, errors

    @classmethod
    def inspect(cls, dataset_dir: Path | str) -> DatasetReport:
        """Inspect a directory for RSNA dataset files and evaluate completeness."""
        target_dir = Path(dataset_dir)
        report = DatasetReport(dataset_path=str(target_dir.resolve()))

        if not target_dir.exists():
            report.is_available = False
            report.missing_components.append(f"Dataset root directory does not exist: {target_dir}")
            report.issues.append("Set DATASET_DIR environment variable or point to valid RSNA dataset location.")
            return report

        # 1. Locate annotation CSV
        candidate_csvs = [
            target_dir / "stage_2_train_labels.csv",
            target_dir / "train_labels.csv",
            target_dir.parent / "stage_2_train_labels.csv",
        ]
        csv_file: Optional[Path] = None
        for cand in candidate_csvs:
            if cand.exists():
                csv_file = cand
                break

        if not csv_file:
            all_csvs = list(target_dir.glob("*.csv"))
            if all_csvs:
                csv_file = all_csvs[0]

        if csv_file:
            report.csv_found = True
            try:
                annotations, errors = cls.parse_annotations(csv_file)
                report.total_patients_in_labels = len(annotations)
                report.malformed_rows_count = len(errors)
                report.positive_cases = sum(1 for a in annotations.values() if a.target == 1)
                report.negative_cases = sum(1 for a in annotations.values() if a.target == 0)
                report.total_bounding_boxes = sum(len(a.boxes) for a in annotations.values())
                if errors:
                    report.issues.extend(errors[:10])
            except Exception as exc:
                report.issues.append(f"Error parsing annotation CSV {csv_file.name}: {exc}")
        else:
            report.missing_components.append("stage_2_train_labels.csv (annotation file)")

        # 2. Locate DICOM images
        dcm_files = list(target_dir.glob("*.dcm"))
        if not dcm_files:
            subdirs = [target_dir / "stage_2_train_images", target_dir / "images"]
            for s in subdirs:
                if s.exists():
                    dcm_files.extend(list(s.glob("*.dcm")))
            if not dcm_files:
                dcm_files = list(target_dir.rglob("*.dcm"))

        report.images_found = len(dcm_files)
        if report.images_found == 0:
            report.missing_components.append("stage_2_train_images/*.dcm (DICOM image scans)")

        # 3. Match patient IDs if both CSV and images are found
        if csv_file and dcm_files and report.total_patients_in_labels > 0:
            dcm_stems = {f.stem for f in dcm_files}
            matched = sum(1 for pid in annotations if pid in dcm_stems)
            report.matched_image_count = matched
            report.missing_image_count = report.total_patients_in_labels - matched
            if report.missing_image_count > 0:
                report.issues.append(
                    f"{report.missing_image_count} labeled patient IDs do not have corresponding .dcm files on disk."
                )

        # 4. Overall availability assessment
        report.is_available = (
            report.csv_found
            and report.images_found > 0
            and report.positive_cases > 0
            and report.matched_image_count > 0
        )

        return report


class RSNAtoYOLOConverter:
    """Converts RSNA bounding-box annotations into normalized YOLO format."""

    @staticmethod
    def box_to_yolo(
        box: BoundingBox,
        image_width: float = 1024.0,
        image_height: float = 1024.0,
        class_id: int = 0,
    ) -> str:
        """Convert a pixel BoundingBox into normalized YOLO format string.

        Format: <class_id> <x_center> <y_center> <width> <height>
        All values are floats in [0.0, 1.0].
        """
        w = max(0.0, box.x_max - box.x_min)
        h = max(0.0, box.y_max - box.y_min)

        center_x = (box.x_min + w / 2.0) / image_width
        center_y = (box.y_min + h / 2.0) / image_height
        norm_w = w / image_width
        norm_h = h / image_height

        # Clamp safely into [0.0, 1.0]
        center_x = max(0.0, min(1.0, center_x))
        center_y = max(0.0, min(1.0, center_y))
        norm_w = max(0.0, min(1.0, norm_w))
        norm_h = max(0.0, min(1.0, norm_h))

        return f"{class_id} {center_x:.6f} {center_y:.6f} {norm_w:.6f} {norm_h:.6f}"

    @staticmethod
    def yolo_to_box(
        yolo_line: str,
        image_width: float = 1024.0,
        image_height: float = 1024.0,
    ) -> Tuple[int, BoundingBox]:
        """Convert a YOLO format line back into (class_id, BoundingBox) in pixel space."""
        parts = yolo_line.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid YOLO line format: '{yolo_line}'")

        class_id = int(parts[0])
        cx, cy, nw, nh = map(float, parts[1:])

        w = nw * image_width
        h = nh * image_height
        x_min = (cx * image_width) - (w / 2.0)
        y_min = (cy * image_height) - (h / 2.0)
        x_max = x_min + w
        y_max = y_min + h

        return class_id, BoundingBox(
            x_min=round(max(0.0, min(image_width, x_min)), 2),
            y_min=round(max(0.0, min(image_height, y_min)), 2),
            x_max=round(max(0.0, min(image_width, x_max)), 2),
            y_max=round(max(0.0, min(image_height, y_max)), 2),
        )

    @staticmethod
    def split_dataset(
        patient_ids: List[str],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = DEFAULT_SPLIT_SEED,
    ) -> Dict[str, List[str]]:
        """Create a deterministic patient-level train/validation/test split.

        Guarantees zero patient leakage between splits.
        """
        if not patient_ids:
            return {"train": [], "val": [], "test": []}

        # Deterministic sorting prior to shuffling ensures reproducibility
        sorted_ids = sorted(list(set(patient_ids)))
        rng = random.Random(seed)
        shuffled = sorted_ids.copy()
        rng.shuffle(shuffled)

        total = len(shuffled)
        train_end = int(round(total * train_ratio))
        val_end = train_end + int(round(total * val_ratio))

        train_set = shuffled[:train_end]
        val_set = shuffled[train_end:val_end]
        test_set = shuffled[val_end:]

        # Handle rounding edge cases
        if not test_set and test_ratio > 0.0 and len(val_set) > 1:
            test_set.append(val_set.pop())

        return {
            "train": sorted(train_set),
            "val": sorted(val_set),
            "test": sorted(test_set),
        }

    @classmethod
    def convert_annotations_to_yolo_labels(
        cls,
        annotations: Dict[str, RSNAAnnotation],
        split_mapping: Dict[str, List[str]],
        output_dir: Path | str,
        image_width: float = 1024.0,
        image_height: float = 1024.0,
    ) -> Dict[str, int]:
        """Write YOLO .txt label files for all splits.

        - Negative patients (Target=0): Empty .txt file (YOLO standard for background images).
        - Positive patients (Target=1): Multi-line .txt file with one line per bounding box.

        Returns:
            Dictionary with counts of generated label files per split.
        """
        out_base = Path(output_dir)
        counts = {"train": 0, "val": 0, "test": 0}

        for split_name, patient_list in split_mapping.items():
            split_dir = out_base / "labels" / split_name
            split_dir.mkdir(parents=True, exist_ok=True)

            for pid in patient_list:
                ann = annotations.get(pid)
                txt_path = split_dir / f"{pid}.txt"

                if ann is None or ann.target == 0 or not ann.boxes:
                    # Write empty file for negative image
                    txt_path.write_text("", encoding="utf-8")
                else:
                    lines = [
                        cls.box_to_yolo(b, image_width=image_width, image_height=image_height, class_id=0)
                        for b in ann.boxes
                    ]
                    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

                counts[split_name] = counts.get(split_name, 0) + 1

        return counts

    @staticmethod
    def generate_yolo_yaml(
        output_dir: Path | str,
        class_name: str = CLASS_NAME,
    ) -> Path:
        """Generate YOLO dataset YAML configuration file."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        yaml_file = out_path / "dataset.yaml"

        yaml_content = (
            f"# RSNA Pneumonia Detection YOLO Configuration\n"
            f"# Medically conservative single-target class\n"
            f"path: {out_path.resolve().as_posix()}\n"
            f"train: images/train\n"
            f"val: images/val\n"
            f"test: images/test\n"
            f"\n"
            f"names:\n"
            f"  0: {class_name}\n"
        )
        yaml_file.write_text(yaml_content, encoding="utf-8")
        return yaml_file
