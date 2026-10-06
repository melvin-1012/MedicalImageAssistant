"""Unit tests for Visualizer component (Phases 1, 5, 6)."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest

from cv.schemas import BoundingBox, Detection
from cv.visualization import Visualizer


def test_visualizer_ready() -> None:
    vis = Visualizer()
    assert vis.ready
    assert vis.name == "Visualization engine"


def test_draw_detections() -> None:
    vis = Visualizer()
    orig = np.full((500, 500), 100, dtype=np.uint8)

    det = Detection(
        label="Possible abnormal opacity",
        confidence=0.82,
        bbox=BoundingBox(x_min=50.0, y_min=60.0, x_max=200.0, y_max=250.0),
    )

    overlay = vis.draw_detections(orig, [det])

    assert overlay.shape == (500, 500, 3)
    assert overlay.dtype == np.uint8
    # Input image was not mutated
    assert orig[100, 100] == 100


def test_visualizer_render_end_to_end(tmp_path: Path) -> None:
    vis = Visualizer()
    orig = np.full((400, 400), 120, dtype=np.uint8)
    proc = np.full((640, 640), 120, dtype=np.uint8)

    det = Detection(
        label="Possible abnormal opacity",
        confidence=0.79,
        bbox=BoundingBox(x_min=100.0, y_min=100.0, x_max=250.0, y_max=250.0),
    )
    heatmap = np.zeros((400, 400), dtype=np.float32)
    heatmap[100:250, 100:250] = 1.0

    res = vis.render(
        original=orig,
        processed=proc,
        detections=[det],
        heatmap=heatmap,
        output_dir=tmp_path,
        stem="sample_test",
    )

    assert res.processed_path is not None
    assert Path(res.processed_path).exists()
    assert res.comparison_path is not None
    assert Path(res.comparison_path).exists()
    assert res.overlay_path is not None
    assert Path(res.overlay_path).exists()
    assert res.heatmap_path is not None
    assert Path(res.heatmap_path).exists()
