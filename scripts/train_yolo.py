"""Train YOLO medical abnormality detector on RSNA dataset.

Usage:
    python scripts/train_yolo.py [--epochs 25] [--batch 8] [--imgsz 640]
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

# Prevent OpenBLAS / OpenMP thread allocation issues on Windows
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
cv2.setNumThreads(0)

import torch
from ultralytics import YOLO

import config


def train_detector(
    dataset_yaml: Path | str = "datasets/rsna_yolo/dataset.yaml",
    epochs: int = 30,
    batch_size: int = 8,
    img_size: int = 640,
    patience: int = 10,
    workers: int = 0,
    cache: bool = False,
    base_model: str = "yolo11n.pt",
    seed: int = 42,
) -> Path:
    yaml_path = Path(dataset_yaml).resolve()
    if not yaml_path.exists():
        raise FileNotFoundError(f"Dataset YAML not found at: {yaml_path}")

    # Determine hardware acceleration
    cuda_available = torch.cuda.is_available()
    device = "0" if cuda_available else "cpu"
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"

    print("=" * 65)
    print("PHASE 4 — YOLO MEDICAL DETECTOR TRAINING")
    print("=" * 65)
    print(f"Dataset Config : {yaml_path}")
    print(f"Base Model     : {base_model}")
    print(f"Device         : {device_name} (device={device})")
    print(f"Epochs         : {epochs}")
    print(f"Patience       : {patience}")
    print(f"Batch Size     : {batch_size}")
    print(f"Image Size     : {img_size}")
    print(f"Workers        : {workers}")
    print(f"Random Seed    : {seed}")
    print("=" * 65)

    # Initialize model
    model = YOLO(base_model)

    output_project = (config.MODELS_DIR / "pneumonia_yolo").resolve()

    # Train model
    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        patience=patience,
        batch=batch_size,
        imgsz=img_size,
        device=device,
        workers=workers,
        seed=seed,
        amp=False,
        cache=cache,
        project=str(output_project),
        name="train_run",
        exist_ok=True,
        verbose=True,
        plots=True,
    )

    # Find best.pt
    run_dir = output_project / "train_run"
    best_weights = run_dir / "weights" / "best.pt"
    if not best_weights.exists():
        best_weights = run_dir / "weights" / "last.pt"

    print("\n--- Training Complete ---")
    print(f"Saved weights to: {best_weights}")

    # Copy to standard models/ locations
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    target_best = config.MODELS_DIR / "model.pt"
    shutil.copy2(best_weights, target_best)
    print(f"Deployed weights to: {target_best}")

    # Evaluate on validation / test split
    print("\nEvaluating trained model on validation data...")
    val_metrics = model.val(data=str(yaml_path), split="val", device=device)

    rd = val_metrics.results_dict if hasattr(val_metrics, "results_dict") else {}
    prec = float(rd.get("metrics/precision(B)", 0.0))
    rec = float(rd.get("metrics/recall(B)", 0.0))
    map50 = float(rd.get("metrics/mAP50(B)", 0.0))
    map50_95 = float(rd.get("metrics/mAP50-95(B)", 0.0))

    print("\n" + "=" * 65)
    print("REAL MODEL EVALUATION METRICS (Validation Split):")
    print("=" * 65)
    print(f"  Precision    : {prec:.4f}")
    print(f"  Recall       : {rec:.4f}")
    print(f"  mAP@0.5      : {map50:.4f}")
    print(f"  mAP@0.5:0.95 : {map50_95:.4f}")
    print("=" * 65)

    return target_best


def main() -> None:
    parser = argparse.ArgumentParser(description="Train YOLO detector on RSNA dataset.")
    parser.add_argument("--yaml", default="datasets/rsna_yolo/dataset.yaml", help="Path to dataset.yaml")
    parser.add_argument("--epochs", type=int, default=30, help="Number of epochs (default: 30)")
    parser.add_argument("--patience", type=int, default=10, help="Early stopping patience (default: 10)")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (default: 8)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size (default: 640)")
    parser.add_argument("--workers", type=int, default=0, help="Dataloader workers (default: 0 for Windows)")
    parser.add_argument("--cache", action="store_true", help="Cache images in RAM for faster training")
    args = parser.parse_args()

    train_detector(
        dataset_yaml=args.yaml,
        epochs=args.epochs,
        patience=args.patience,
        batch_size=args.batch,
        img_size=args.imgsz,
        workers=args.workers,
        cache=args.cache,
    )


if __name__ == "__main__":
    main()


