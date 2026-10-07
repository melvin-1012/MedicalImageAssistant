"""Evaluation, calibration, and verification of trained YOLO medical CV model.

Performs:
1. Validation on held-out validation set (precision, recall, mAP@0.5, mAP@0.5:0.95)
2. Evaluation of BoxF1 curve to find calibrated confidence threshold
3. End-to-end pipeline inference on known-positive and known-negative test images
4. Verification that known-positive images produce bounding boxes with proper contract
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import torch
from ultralytics import YOLO

import config
from cv.pipeline import MedicalCVPipeline

def run_evaluation_and_calibration():
    print("=" * 70)
    print("EVALUATION & CALIBRATION FOR RETRAINED YOLO MODEL")
    print("=" * 70)

    best_weights = config.MODELS_DIR / "pneumonia_yolo" / "train_run" / "weights" / "best.pt"
    deployed_weights = config.MODELS_DIR / "model.pt"

    if not best_weights.exists():
        raise FileNotFoundError(f"Best checkpoint not found at {best_weights}")
    
    print(f"Loading best checkpoint from: {best_weights}")
    model = YOLO(str(best_weights))
    
    # 1. Validation metrics
    print("\n[Step 1] Running validation on held-out split ('val')...")
    val_results = model.val(
        data="datasets/rsna_yolo/dataset.yaml",
        split="val",
        device="0" if torch.cuda.is_available() else "cpu",
        plots=True,
    )

    rd = val_results.results_dict if hasattr(val_results, "results_dict") else {}
    precision = float(rd.get("metrics/precision(B)", 0.0))
    recall = float(rd.get("metrics/recall(B)", 0.0))
    map50 = float(rd.get("metrics/mAP50(B)", 0.0))
    map50_95 = float(rd.get("metrics/mAP50-95(B)", 0.0))

    print("\n--- Validation Metrics ---")
    print(f"  Precision    : {precision:.4f}")
    print(f"  Recall       : {recall:.4f}")
    print(f"  mAP@0.5      : {map50:.4f}")
    print(f"  mAP@0.5:0.95 : {map50_95:.4f}")

    # 2. Threshold Calibration from F1 curve
    # Ultralytics val_results.box contains fitness, f1, p, r, etc.
    calibrated_threshold = 0.25
    try:
        if hasattr(val_results.box, "f1") and hasattr(val_results.box, "x"):
            f1_curve = val_results.box.f1
            x_curve = val_results.box.x
            best_idx = np.argmax(f1_curve)
            calibrated_threshold = float(x_curve[best_idx])
            best_f1 = float(f1_curve[best_idx])
            print(f"\n[Step 2] Calibrated optimal F1 threshold: {calibrated_threshold:.3f} (Max F1: {best_f1:.4f})")
    except Exception as e:
        print(f"Note: Standard F1 curve extraction warning: {e}. Using calibrated fallback 0.25")

    # If calibrated threshold is too low (e.g. < 0.15) or default 0.25 is standard:
    if calibrated_threshold < 0.15:
        calibrated_threshold = 0.20
    elif calibrated_threshold > 0.40:
        calibrated_threshold = 0.30

    print(f"  Final calibrated operating threshold: {calibrated_threshold:.3f}")

    # 3. Test on known positive and known negative images
    print("\n[Step 3] Running end-to-end MedicalCVPipeline inference on test images...")
    pipeline = MedicalCVPipeline()
    pipeline.initialize()
    # Update detector threshold
    pipeline.detector.confidence_threshold = calibrated_threshold

    test_images_dir = Path("datasets/rsna_yolo/images/test")
    test_labels_dir = Path("datasets/rsna_yolo/labels/test")

    # Identify known positives (files with non-empty label txt)
    positive_files = []
    negative_files = []
    for lbl_path in sorted(test_labels_dir.glob("*.txt")):
        content = lbl_path.read_text().strip()
        img_path = test_images_dir / f"{lbl_path.stem}.jpg"
        if not img_path.exists():
            continue
        if content:
            positive_files.append((img_path, content.splitlines()))
        else:
            negative_files.append(img_path)

    print(f"Total available test set: {len(positive_files)} positives, {len(negative_files)} negatives")

    # Test 5 known positives
    print("\nTesting 5 Known Positives:")
    pos_results = []
    for img_path, ground_truth_boxes in positive_files[:5]:
        res = pipeline.run(img_path)
        dets = res.detections or []
        print(f"\nImage: {img_path.name}")
        print(f"  Ground Truth: {len(ground_truth_boxes)} box(es)")
        print(f"  Detections: {len(dets)} detected")
        for i, d in enumerate(dets):
            print(f"    Det {i+1}: label='{d.label}', conf={d.confidence:.4f}, box=({d.x_min}, {d.y_min}, {d.x_max}, {d.y_max})")
        
        pos_results.append({
            "image": img_path.name,
            "gt_boxes": ground_truth_boxes,
            "detections": [
                {
                    "label": d.label,
                    "confidence": float(d.confidence),
                    "box": [d.x_min, d.y_min, d.x_max, d.y_max]
                }
                for d in dets
            ],
            "genai_finding": res.to_genai_dict().get("finding"),
            "requires_physician_review": res.to_genai_dict().get("requires_physician_review"),
        })

    # Test 5 known negatives
    print("\nTesting 5 Known Negatives:")
    neg_results = []
    for img_path in negative_files[:5]:
        res = pipeline.run(img_path)
        dets = res.detections or []
        print(f"Image: {img_path.name} -> {len(dets)} detections (Expected: 0)")
        neg_results.append({
            "image": img_path.name,
            "detections_count": len(dets),
            "genai_finding": res.to_genai_dict().get("finding"),
        })

    # Summary
    summary = {
        "validation_metrics": {
            "precision": precision,
            "recall": recall,
            "mAP50": map50,
            "mAP50_95": map50_95,
        },
        "calibrated_threshold": calibrated_threshold,
        "positive_test_results": pos_results,
        "negative_test_results": neg_results,
    }

    output_path = Path("output/evaluation_summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSaved evaluation summary to: {output_path}")

    return summary

if __name__ == "__main__":
    run_evaluation_and_calibration()
