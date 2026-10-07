"""Command-line entry point for the Medical CV engine.

Usage:
    python main.py                                      # verify structure & banner
    python main.py <image_path>                         # readable summary
    python main.py <image_path> --json                  # full JSON output
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import config
from cv.pipeline import MedicalCVPipeline
from cv.schemas import AnalysisStatus
from utils.logger import get_logger

BAR = "=" * 40


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=config.PROJECT_NAME)
    parser.add_argument("image", nargs="?", type=Path, help="path to a medical image")
    parser.add_argument("--json", action="store_true", help="output full CVAnalysisResult JSON")
    parser.add_argument("--genai", action="store_true", help="output CV -> GenAI handshake JSON schema")
    parser.add_argument("--conf", type=float, default=None, help="override detector confidence threshold")
    args = parser.parse_args(argv)

    print(f"{BAR}\n{config.PROJECT_NAME}\n{config.PROJECT_ID}\n{BAR}\n")
    logger = get_logger("main")

    pipeline = MedicalCVPipeline()
    pipeline.initialize()
    if args.conf is not None and hasattr(pipeline.detector, "confidence_threshold"):
        pipeline.detector.confidence_threshold = args.conf
    print("\nMedical CV pipeline initialized successfully.\n")

    if not pipeline.detector.is_loaded:
        print("No medical model loaded.")

    if args.image is None:
        print("Batch 3 active: Phases 1 through 9 initialized (Loading, Preprocessing, Quality, Model, Localization, Heatmap, Segmentation, Confidence/Evidence, Structured JSON).")
        return 0

    result = pipeline.run(args.image)

    if args.genai:
        print(result.to_genai_json())
        return 0 if result.status == AnalysisStatus.OK else 1

    if args.json:
        print(result.to_json())
        return 0 if result.status == AnalysisStatus.OK else 1

    # Human-readable summary
    print(f"\nAnalysis Summary:")
    print(f"  Status       : {result.status.value.upper()}")
    if result.metadata:
        m = result.metadata
        print(f"  File         : {Path(m.path).name}")
        print(f"  Dimensions   : {m.width}x{m.height} ({m.channels} channel, {m.dtype})")
        print(f"  File size    : {m.file_size_bytes} bytes")
        if m.extra:
            extras = ", ".join(f"{k}={v}" for k, v in m.extra.items())
            print(f"  Metadata     : {extras}")

    if result.quality:
        q = result.quality
        print(f"  Quality      : {q.level.value} (Score: {q.score:.2f})")
        print(f"    - Blur     : {q.blur} (Laplacian var on reference size)")
        print(f"    - Brightness: {q.brightness}")
        print(f"    - Contrast : {q.contrast}")
        print(f"    - Noise    : {q.noise}")
        if q.issues:
            print(f"    - Issues   : {'; '.join(q.issues)}")

    if result.model_loaded:
        if result.detections:
            print(f"  Detections   : {len(result.detections)} finding(s) identified")
            for idx, det in enumerate(result.detections, start=1):
                box_str = (
                    f"[{det.bbox.x_min}, {det.bbox.y_min}, {det.bbox.x_max}, {det.bbox.y_max}]"
                    if det.bbox else "None"
                )
                print(f"    - Finding {idx:02d}: {det.label} (Conf: {det.confidence * 100:.1f}%) | Original BBox: {box_str}")
        else:
            print("  Detections   : No model-detected abnormality above configured threshold.")
    else:
        print("  Model        : No medical model loaded (NullDetector).")

    if result.visualization:
        v = result.visualization
        if v.processed_path:
            print(f"  Processed img: {v.processed_path}")
        if v.comparison_path:
            print(f"  Comparison   : {v.comparison_path}")
        if v.overlay_path:
            print(f"  Overlay (BBox): {v.overlay_path}")
        if v.heatmap_path:
            print(f"  Heatmap      : {v.heatmap_path}")

    if result.warnings:
        print(f"  Warnings     : {'; '.join(result.warnings)}")

    if result.errors:
        print(f"  Errors       : {'; '.join(result.errors)}")

    return 0 if result.status == AnalysisStatus.OK else 1


if __name__ == "__main__":
    sys.exit(main())
