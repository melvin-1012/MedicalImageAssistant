"""Dataset inspection and quality threshold calibration script.

Given a folder or dataset directory, prints:
- RSNA Annotation CSV summary (positive vs negative cases, bounding box counts)
- DICOM file count and matching with labels
- Size/resolution distribution
- Bit-depth / dtype distribution
- View positions (PA / AP)
- Phase 3 Image Quality metrics summary (blur, brightness, contrast, noise, score)
- Quality Level classification breakdown (GOOD / MODERATE / POOR)

Usage:
    python tests/inspect_dataset.py [folder_path] [--max-samples N]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import List

import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from cv.dataset import RSNADatasetInspector
from cv.image_loader import ImageLoader
from cv.quality import QualityAnalyzer
from cv.schemas import QualityLevel


def inspect_dataset(target_dir: Path, max_samples: int | None = None) -> None:
    """Inspect a directory of DICOM files and annotations, reporting completeness and quality."""
    target_dir = Path(target_dir)

    # 1. First run RSNA annotation & integrity inspection
    ds_report = RSNADatasetInspector.inspect(target_dir)
    print(ds_report.summary())

    if not target_dir.exists():
        return

    # 2. Find all .dcm files for image quality calibration
    dcm_files = list(target_dir.glob("*.dcm"))
    if not dcm_files:
        dcm_files = list(target_dir.rglob("*.dcm"))

    if not dcm_files:
        print("\nNo .dcm files found in target directory for image quality calibration.")
        return

    total_files = len(dcm_files)
    print(f"\nEvaluating image quality on {total_files} DICOM files...")

    if max_samples and max_samples < total_files:
        print(f"Sampling {max_samples} files for evaluation...")
        import random
        random.seed(42)
        dcm_files = random.sample(dcm_files, max_samples)

    loader = ImageLoader()
    quality_analyzer = QualityAnalyzer()

    sizes: List[str] = []
    dtypes: List[str] = []
    view_positions: List[str] = []
    modalities: List[str] = []
    photometrics: List[str] = []
    quality_levels: List[str] = []

    blurs: List[float] = []
    brightnesses: List[float] = []
    contrasts: List[float] = []
    noises: List[float] = []
    scores: List[float] = []
    issues_counter = Counter()

    processed_count = 0
    for file_path in dcm_files:
        try:
            loaded = loader.load(file_path)
            meta = loaded.metadata
            q = quality_analyzer.assess(loaded.image)

            sizes.append(f"{meta.width}x{meta.height}")
            dtypes.append(f"{meta.extra.get('original_bits_stored', meta.dtype)}-bit")
            view_positions.append(meta.extra.get("view_position", "UNKNOWN"))
            modalities.append(meta.extra.get("modality", "UNKNOWN"))
            photometrics.append(meta.extra.get("photometric_interpretation", "UNKNOWN"))

            quality_levels.append(q.level.value)
            if q.blur is not None:
                blurs.append(q.blur)
            if q.brightness is not None:
                brightnesses.append(q.brightness)
            if q.contrast is not None:
                contrasts.append(q.contrast)
            if q.noise is not None:
                noises.append(q.noise)
            scores.append(q.score)

            for issue in q.issues:
                issues_counter[issue] += 1

            processed_count += 1
        except Exception as exc:
            print(f"Failed to process {file_path.name}: {exc}")

    if processed_count == 0:
        print("No files could be processed successfully.")
        return

    print("\n--- 1. Image Size & Geometry Distribution ---")
    for size_str, count in Counter(sizes).most_common():
        pct = (count / processed_count) * 100
        print(f"  {size_str:15s}: {count:5d} ({pct:5.1f}%)")

    print("\n--- 2. Bit Depth / Dtype Distribution ---")
    for dt_str, count in Counter(dtypes).most_common():
        pct = (count / processed_count) * 100
        print(f"  {dt_str:15s}: {count:5d} ({pct:5.1f}%)")

    print("\n--- 3. View Position Distribution ---")
    for vp_str, count in Counter(view_positions).most_common():
        pct = (count / processed_count) * 100
        print(f"  {vp_str:15s}: {count:5d} ({pct:5.1f}%)")

    print("\n--- 4. Photometric Interpretation Distribution ---")
    for pi_str, count in Counter(photometrics).most_common():
        pct = (count / processed_count) * 100
        print(f"  {pi_str:15s}: {count:5d} ({pct:5.1f}%)")

    print("\n--- 5. Phase 3 Quality Metrics Summary ---")
    metrics = [
        ("Blur (Laplacian Var)", blurs),
        ("Brightness (Mean)", brightnesses),
        ("Contrast (Std Dev)", contrasts),
        ("Noise (Residual Std)", noises),
        ("Composite Score (0..1)", scores),
    ]
    print(f"  {'Metric':25s} | {'Mean':8s} | {'Std':8s} | {'Min':8s} | {'Max':8s} | {'Median':8s}")
    print("  " + "-" * 72)
    for name, vals in metrics:
        if vals:
            v_arr = np.array(vals)
            print(
                f"  {name:25s} | {np.mean(v_arr):8.2f} | {np.std(v_arr):8.2f} | "
                f"{np.min(v_arr):8.2f} | {np.max(v_arr):8.2f} | {np.median(v_arr):8.2f}"
            )

    print("\n--- 6. Quality Level Breakdown ---")
    level_counts = Counter(quality_levels)
    good_cnt = level_counts.get(QualityLevel.GOOD.value, 0)
    mod_cnt = level_counts.get(QualityLevel.MODERATE.value, 0)
    poor_cnt = level_counts.get(QualityLevel.POOR.value, 0)

    good_pct = (good_cnt / processed_count) * 100
    mod_pct = (mod_cnt / processed_count) * 100
    poor_pct = (poor_cnt / processed_count) * 100

    print(f"  GOOD    : {good_cnt:5d} ({good_pct:5.1f}%)")
    print(f"  MODERATE: {mod_cnt:5d} ({mod_pct:5.1f}%)")
    print(f"  POOR    : {poor_cnt:5d} ({poor_pct:5.1f}%)")

    if issues_counter:
        print("\n--- 7. Most Frequent Quality Issues ---")
        for issue, count in issues_counter.most_common(5):
            pct = (count / processed_count) * 100
            print(f"  - {issue}: {count} ({pct:.1f}%)")

    print("=" * 65)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect RSNA dataset and calibrate image quality.")
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Folder containing dataset (default: DATASET_DIR or input/sample_images)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum number of DICOM files to evaluate",
    )
    args = parser.parse_args()

    if args.folder:
        folder = Path(args.folder)
    elif config.DATASET_DIR.exists() and any(config.DATASET_DIR.glob("*.dcm")):
        folder = config.DATASET_DIR
    else:
        folder = config.SAMPLE_DIR

    inspect_dataset(folder, max_samples=args.max_samples)


if __name__ == "__main__":
    main()
