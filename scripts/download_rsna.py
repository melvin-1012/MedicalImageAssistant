"""Automated downloader and setup for RSNA Pneumonia Detection Challenge dataset.

Usage:
    python scripts/download_rsna.py
"""
from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def check_kaggle_auth() -> bool:
    """Check if Kaggle credentials are configured via kaggle.json or environment."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.is_file():
        return True

    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    if username and key:
        return True

    return False


def get_dir_size_str(path: Path) -> str:
    """Calculate approximate size in MB or GB."""
    if not path.exists():
        return "0 MB"
    total_bytes = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    if total_bytes >= 1024 ** 3:
        return f"{total_bytes / (1024 ** 3):.2f} GB"
    return f"{total_bytes / (1024 ** 2):.2f} MB"


def setup_rsna_dataset() -> None:
    print("=" * 65)
    print("RSNA PNEUMONIA DETECTION CHALLENGE - DATASET SETUP")
    print("=" * 65)

    has_auth = check_kaggle_auth()
    kaggle_json_path = Path.home() / ".kaggle" / "kaggle.json"

    if not has_auth:
        print("\n[STATUS] Kaggle authentication: NOT CONFIGURED")
        print("\nCredential Setup Required on your machine:")
        print(f"  1. Go to your Kaggle Account settings (https://www.kaggle.com/settings)")
        print(f"  2. Click 'Create New Token' to download 'kaggle.json'.")
        print(f"  3. Save 'kaggle.json' to:")
        print(f"     {kaggle_json_path}")
        print(f"     (Or set KAGGLE_USERNAME and KAGGLE_KEY environment variables).")
        print(f"  4. Ensure you have accepted the competition rules at:")
        print("     https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge/rules")
        print("\nOnce placed, re-run:")
        print("  .\\venv\\Scripts\\python.exe scripts/download_rsna.py")
        print("=" * 65)
        return

    print("\n[STATUS] Kaggle authentication: CONFIGURED (kaggle.json found)")
    print("[INFO] Checking cache / downloading dataset via KaggleHub...")

    try:
        import kagglehub
    except ImportError:
        print("[ERROR] 'kagglehub' package is not installed.")
        return

    try:
        download_path_str = kagglehub.competition_download("rsna-pneumonia-detection-challenge")
        download_path = Path(download_path_str)
        print(f"[SUCCESS] Dataset located at: {download_path}")
    except Exception as exc:
        print(f"\n[ERROR] Kaggle download request failed: {exc}")
        print("\nPlease verify:")
        print("  - Your kaggle.json credentials are valid.")
        print("  - You have accepted the competition rules at:")
        print("    https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge/rules")
        print("=" * 65)
        return

    # Locate required files
    labels_csv = download_path / "stage_2_train_labels.csv"
    if not labels_csv.exists():
        cand = list(download_path.rglob("stage_2_train_labels.csv"))
        if cand:
            labels_csv = cand[0]

    images_dir = download_path / "stage_2_train_images"
    if not images_dir.exists():
        cand_dirs = [p for p in download_path.rglob("stage_2_train_images") if p.is_dir()]
        if cand_dirs:
            images_dir = cand_dirs[0]

    labels_exist = labels_csv.exists()
    images_exist = images_dir.exists()

    dcm_count = len(list(images_dir.glob("*.dcm"))) if images_exist else 0
    size_str = get_dir_size_str(download_path)

    print(f"\n--- Component Verification ---")
    print(f"stage_2_train_labels.csv : {'EXISTS' if labels_exist else 'MISSING'} ({labels_csv})")
    print(f"stage_2_train_images     : {'EXISTS' if images_exist else 'MISSING'} ({dcm_count} .dcm files located)")
    print(f"Approximate disk usage   : {size_str}")

    # Set up project path junction without duplicating disk usage
    target_link = PROJECT_ROOT / "datasets" / "rsna"
    target_link.parent.mkdir(parents=True, exist_ok=True)

    if not target_link.exists():
        try:
            subprocess.run(
                ["cmd", "/c", f'mklink /J "{target_link}" "{download_path}"'],
                check=True,
                capture_output=True,
            )
            print(f"[INFO] Created directory junction: {target_link} -> {download_path}")
        except Exception:
            print(f"[INFO] Using direct path without junction: {download_path}")

    print("=" * 65)


if __name__ == "__main__":
    setup_rsna_dataset()
