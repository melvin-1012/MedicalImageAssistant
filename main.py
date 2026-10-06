"""Command-line entry point for the Medical CV engine.

    python main.py                                   # verify structure
    python main.py input/sample_images/chest_xray.png  # (Phase 1+)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import config
from cv.pipeline import MedicalCVPipeline
from utils.logger import get_logger

BAR = "=" * 40


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=config.PROJECT_NAME)
    parser.add_argument("image", nargs="?", type=Path, help="path to an image")
    args = parser.parse_args(argv)

    print(f"{BAR}\n{config.PROJECT_NAME}\n{config.PROJECT_ID}\n{BAR}\n")
    logger = get_logger("main")

    pipeline = MedicalCVPipeline()
    pipeline.initialize()
    print("\nMedical CV pipeline initialized successfully.\n")

    if not pipeline.detector.is_loaded:
        print("No medical model loaded.")

    if args.image is None:
        print("Ready for Phase 1: Image Loading & Validation.")
        return 0

    try:
        result = pipeline.run(args.image)
        print(result.to_json())
        return 0
    except NotImplementedError as exc:
        logger.warning("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
