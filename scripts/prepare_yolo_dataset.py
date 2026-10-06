"""Prepares and converts RSNA Pneumonia Detection DICOM dataset into YOLO format.

Pipeline:
1. Parse stage_2_train_labels.csv into RSNAAnnotation mappings.
2. Select balanced cohort (positive pneumonia scans + true negative scans).
3. Split deterministically into train (80%), val (10%), test (10%) with fixed seed (42).
4. Decode DICOMs via ImageLoader (preserving 8-bit density, inverting MONOCHROME1, scrubbing PHI).
5. Save pre-sized 640x640 JPEG images into images/{train,val,test}.
6. Generate normalized YOLO .txt label files into labels/{train,val,test}.
7. Generate dataset.yaml.

Usage:
    python scripts/prepare_yolo_dataset.py [--max-samples 2500] [--img-size 640]
"""
from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np

import config
from cv.dataset import RSNADatasetInspector, RSNAtoYOLOConverter
from cv.image_loader import ImageLoader


def prepare_yolo_dataset(
    source_dir: Path | str,
    output_dir: Path | str,
    max_samples: int | None = 2500,
    img_size: int = 640,
    seed: int = 42,
) -> Path:
    source_path = Path(source_dir)
    out_path = Path(output_dir)

    print("=" * 65)
    print("RSNA PNEUMONIA DETECTION - YOLO DATASET CONVERSION")
    print("=" * 65)
    print(f"Source Directory : {source_path.resolve()}")
    print(f"Output Directory : {out_path.resolve()}")
    print(f"Target Image Size: {img_size}x{img_size}")
    print(f"Random Seed      : {seed}")

    csv_file = source_path / "stage_2_train_labels.csv"
    if not csv_file.exists():
        cand = list(source_path.rglob("stage_2_train_labels.csv"))
        if not cand:
            raise FileNotFoundError(f"stage_2_train_labels.csv not found in {source_path}")
        csv_file = cand[0]

    # Find DICOM images
    images_dir = source_path / "stage_2_train_images"
    if not images_dir.exists():
        cand_dirs = [p for p in source_path.rglob("stage_2_train_images") if p.is_dir()]
        if not cand_dirs:
            raise FileNotFoundError(f"stage_2_train_images not found in {source_path}")
        images_dir = cand_dirs[0]

    print(f"\nParsing annotations from: {csv_file.name}...")
    annotations, errors = RSNADatasetInspector.parse_annotations(csv_file)
    print(f"Total labeled patients: {len(annotations)} (Malformed rows: {len(errors)})")

    positives = [pid for pid, ann in annotations.items() if ann.target == 1]
    negatives = [pid for pid, ann in annotations.items() if ann.target == 0]
    print(f"Total Positive Cases: {len(positives)}")
    print(f"Total Negative Cases: {len(negatives)}")

    # Sample cohort if requested
    if max_samples and max_samples < len(annotations):
        rng = random.Random(seed)
        half = max_samples // 2
        selected_pos = rng.sample(positives, min(half, len(positives)))
        selected_neg = rng.sample(negatives, min(half, len(negatives)))
        cohort = selected_pos + selected_neg
        rng.shuffle(cohort)
        print(f"Selected balanced cohort of {len(cohort)} patients ({len(selected_pos)} pos, {len(selected_neg)} neg)")
    else:
        cohort = list(annotations.keys())
        print(f"Using complete dataset of {len(cohort)} patients")

    # Split cohort 80/10/10
    splits = RSNAtoYOLOConverter.split_dataset(cohort, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=seed)
    print(f"\nSplit Distribution:")
    print(f"  Train: {len(splits['train'])} ({len(splits['train'])/len(cohort)*100:.1f}%)")
    print(f"  Val  : {len(splits['val'])} ({len(splits['val'])/len(cohort)*100:.1f}%)")
    print(f"  Test : {len(splits['test'])} ({len(splits['test'])/len(cohort)*100:.1f}%)")

    loader = ImageLoader()

    # Create directories
    for split_name in ("train", "val", "test"):
        (out_path / "images" / split_name).mkdir(parents=True, exist_ok=True)
        (out_path / "labels" / split_name).mkdir(parents=True, exist_ok=True)

    print(f"\nConverting DICOMs and writing YOLO annotations...")
    total_converted = 0

    for split_name, patient_list in splits.items():
        img_out_dir = out_path / "images" / split_name
        lbl_out_dir = out_path / "labels" / split_name

        for pid in patient_list:
            dcm_path = images_dir / f"{pid}.dcm"
            if not dcm_path.exists():
                continue

            # Load and standardize DICOM via ImageLoader
            try:
                loaded = loader.load(dcm_path)
            except Exception as exc:
                print(f"Error loading {pid}.dcm: {exc}")
                continue

            orig_w, orig_h = loaded.metadata.width, loaded.metadata.height
            img_arr = loaded.image

            # Resize to target size for YOLO
            if img_arr.shape[:2] != (img_size, img_size):
                resized = cv2.resize(img_arr, (img_size, img_size), interpolation=cv2.INTER_AREA)
            else:
                resized = img_arr

            # Write image as JPEG
            target_img_path = img_out_dir / f"{pid}.jpg"
            cv2.imwrite(str(target_img_path), resized, [cv2.IMWRITE_JPEG_QUALITY, 95])

            # Write label file (.txt)
            ann = annotations.get(pid)
            lbl_file = lbl_out_dir / f"{pid}.txt"

            if ann is None or ann.target == 0 or not ann.boxes:
                lbl_file.write_text("", encoding="utf-8")
            else:
                lines = [
                    RSNAtoYOLOConverter.box_to_yolo(box, image_width=orig_w, image_height=orig_h, class_id=0)
                    for box in ann.boxes
                ]
                lbl_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

            total_converted += 1
            if total_converted % 500 == 0:
                print(f"  Processed {total_converted}/{len(cohort)} images...")

    print(f"Successfully converted {total_converted} images into {out_path}")

    # Generate dataset.yaml
    yaml_file = RSNAtoYOLOConverter.generate_yolo_yaml(out_path)
    print(f"Generated YOLO configuration: {yaml_file}")
    print("=" * 65)
    return yaml_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert RSNA dataset to YOLO format.")
    parser.add_argument(
        "--source",
        default="datasets/rsna",
        help="Source RSNA dataset directory (default: datasets/rsna)",
    )
    parser.add_argument(
        "--output",
        default="datasets/rsna_yolo",
        help="Output YOLO dataset directory (default: datasets/rsna_yolo)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=2500,
        help="Number of balanced samples to convert (default: 2500)",
    )
    parser.add_argument(
        "--img-size",
        type=int,
        default=640,
        help="Image size for training (default: 640)",
    )
    args = parser.parse_args()

    prepare_yolo_dataset(
        source_dir=args.source,
        output_dir=args.output,
        max_samples=args.max_samples,
        img_size=args.img_size,
    )


if __name__ == "__main__":
    main()
