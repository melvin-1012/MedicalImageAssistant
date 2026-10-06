"""Calibration script for Phase 3 Image Quality Assessment.

Evaluates quality metrics on images and validates that specific degradations
(blur, underexposure, overexposure, low contrast, noise, low resolution)
systematically trigger the expected metrics and issues.

Usage:
    python -m tests.calibrate_quality [folder_path]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import cv2
import numpy as np

import config
from cv.image_loader import ImageLoader
from cv.quality import QualityAnalyzer


def generate_degradations(base_img: np.ndarray) -> dict[str, np.ndarray]:
    """Generate controlled synthetic degradations from a clean reference image."""
    img = base_img.copy()
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    h, w = img.shape[:2]

    # 1. Heavy Gaussian blur
    blurred = cv2.GaussianBlur(img, (25, 25), 9.0)

    # 2. Darken (underexposure)
    darkened = np.clip(img.astype(np.float32) * 0.25, 0, 255).astype(np.uint8)

    # 3. Brighten (overexposure / washout)
    brightened = np.clip(img.astype(np.float32) * 1.5 + 80, 0, 255).astype(np.uint8)

    # 4. Low contrast (compressed dynamic range)
    low_contrast = np.clip(img.astype(np.float32) * 0.15 + 100, 0, 255).astype(np.uint8)

    # 5. Added severe Gaussian noise
    noise_arr = np.random.normal(0, 30.0, img.shape).astype(np.float32)
    noisy = np.clip(img.astype(np.float32) + noise_arr, 0, 255).astype(np.uint8)

    # 6. Downscale (low resolution)
    downscaled = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)

    return {
        "Clean Reference": img,
        "Heavy Blur": blurred,
        "Underexposed (Dark)": darkened,
        "Overexposed (Washout)": brightened,
        "Low Contrast": low_contrast,
        "Severe Noise": noisy,
        "Low Resolution (128x128)": downscaled,
    }


def calibrate_folder(folder_path: Path) -> None:
    folder = Path(folder_path)
    loader = ImageLoader()
    analyzer = QualityAnalyzer()

    print("=" * 70)
    print("PHASE 3 IMAGE QUALITY METRIC CALIBRATION")
    print(f"Target Directory: {folder.resolve()}")
    print("=" * 70)

    files = list(folder.glob("*.dcm")) + list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
    if not files:
        print(f"No image files found in {folder}.")
        return

    print(f"\n1. Quality Metrics on Sample Images ({len(files)} files):")
    print(f"  {'File':22s} | {'Level':8s} | {'Score':5s} | {'Blur':7s} | {'Bright':6s} | {'Contrast':8s} | {'Noise':5s} | Issues")
    print("  " + "-" * 95)

    base_sample_img = None
    for f in files:
        try:
            loaded = loader.load(f)
            q = analyzer.assess(loaded.image)
            issues_str = "; ".join(q.issues) if q.issues else "None"
            print(
                f"  {f.name:22s} | {q.level.value:8s} | {q.score:5.2f} | {q.blur:7.1f} | "
                f"{q.brightness:6.1f} | {q.contrast:8.1f} | {q.noise:5.1f} | {issues_str}"
            )
            if base_sample_img is None:
                base_sample_img = loaded.image.copy()
        except Exception as exc:
            print(f"  {f.name:22s} | FAILED: {exc}")

    if base_sample_img is not None:
        print("\n2. Synthetic Degradation Response Test:")
        print("   Verifying that each degradation moves the specific metric and lowers score:")
        print(f"  {'Degradation':24s} | {'Level':8s} | {'Score':5s} | {'Blur':7s} | {'Bright':6s} | {'Contrast':8s} | {'Noise':5s} | Issues")
        print("  " + "-" * 95)

        degraded_set = generate_degradations(base_sample_img)
        ref_q = analyzer.assess(degraded_set["Clean Reference"])

        for name, img_var in degraded_set.items():
            q = analyzer.assess(img_var)
            issues_str = "; ".join(q.issues) if q.issues else "None"
            print(
                f"  {name:24s} | {q.level.value:8s} | {q.score:5.2f} | {q.blur:7.1f} | "
                f"{q.brightness:6.1f} | {q.contrast:8.1f} | {q.noise:5.1f} | {issues_str}"
            )

        print("\n3. Calibration Validation Summary:")
        blur_q = analyzer.assess(degraded_set["Heavy Blur"])
        dark_q = analyzer.assess(degraded_set["Underexposed (Dark)"])
        bright_q = analyzer.assess(degraded_set["Overexposed (Washout)"])
        contrast_q = analyzer.assess(degraded_set["Low Contrast"])
        noise_q = analyzer.assess(degraded_set["Severe Noise"])
        res_q = analyzer.assess(degraded_set["Low Resolution (128x128)"])

        assert blur_q.blur < ref_q.blur, "Blur failed to lower blur metric"
        assert dark_q.brightness < ref_q.brightness, "Darkening failed to lower brightness metric"
        assert bright_q.brightness > ref_q.brightness, "Brightening failed to increase brightness metric"
        assert contrast_q.contrast < ref_q.contrast, "Low contrast failed to lower contrast metric"
        assert noise_q.noise > ref_q.noise, "Noise failed to increase noise metric"
        assert res_q.level == "POOR", "Low resolution failed to flag POOR"
        print("  [SUCCESS] All degradations correctly perturb target metrics and degrade quality scores.")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate quality metrics and verify degradation responses.")
    parser.add_argument("folder", nargs="?", default="input/sample_images", help="Folder containing sample images")
    args = parser.parse_args()
    calibrate_folder(Path(args.folder))


if __name__ == "__main__":
    main()
