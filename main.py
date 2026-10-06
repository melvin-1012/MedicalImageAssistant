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
    args = parser.parse_args(argv)

    print(f"{BAR}\n{config.PROJECT_NAME}\n{config.PROJECT_ID}\n{BAR}\n")
    logger = get_logger("main")

    pipeline = MedicalCVPipeline()
    pipeline.initialize()
    print("\nMedical CV pipeline initialized successfully.\n")

    if not pipeline.detector.is_loaded:
        print("No medical model loaded.")

    if args.image is None:
        print("Phase 3 complete / Ready for Batch 2: Model Integration.")
        return 0

    result = pipeline.run(args.image)

    if args.json:
        print(result.to_json())
        return 0 if result.status == AnalysisStatus.OK else 1

    # Minimal human-readable summary
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

    if result.visualization:
        v = result.visualization
        if v.processed_path:
            print(f"  Processed img: {v.processed_path}")
        if v.comparison_path:
            print(f"  Comparison   : {v.comparison_path}")

    if result.warnings:
        print(f"  Warnings     : {'; '.join(result.warnings)}")

    if result.errors:
        print(f"  Errors       : {'; '.join(result.errors)}")

    print("  Model        : No medical model loaded.")

    return 0 if result.status == AnalysisStatus.OK else 1


if __name__ == "__main__":
    sys.exit(main())
