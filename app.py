"""Minimal Streamlit UI for the Medical CV engine (dev harness).

    streamlit run app.py

Reads only `CVAnalysisResult`; tabs fill in automatically as phases land.
No logic from cv/ is duplicated here.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

import config
from cv.pipeline import MedicalCVPipeline

PHASES = [
    (0, "Project foundation", True),
    (1, "Image loading + validation", True),
    (2, "OpenCV preprocessing", True),
    (3, "Image quality assessment", True),
    (4, "Model integration", True),
    (5, "Bounding-box localization", True),
    (6, "Heatmap / Explainability", True),
    (7, "Segmentation (Unavailable - BBoxes only)", True),
    (8, "Confidence + evidence", True),
    (9, "Structured JSON output", True),
]


st.set_page_config(page_title=config.PROJECT_NAME, page_icon="🩻", layout="wide")


@st.cache_resource
def get_pipeline() -> MedicalCVPipeline:
    pipeline = MedicalCVPipeline()
    pipeline.initialize()
    return pipeline


def pending(phase: int, text: str) -> None:
    st.caption(f"{text} — available in Phase {phase}.")


def show_image(path: str | None, phase: int, text: str) -> None:
    if path and Path(path).exists():
        st.image(path, use_container_width=True)
    else:
        pending(phase, text)


pipeline = get_pipeline()

# ---- Sidebar: status ------------------------------------------------------
with st.sidebar:
    st.subheader("Pipeline")
    for comp in (pipeline.loader, pipeline.validator, pipeline.preprocessor,
                 pipeline.quality, pipeline.detector, pipeline.localizer,
                 pipeline.heatmap, pipeline.segmenter, pipeline.visualizer):
        is_ready = getattr(comp, "ready", getattr(comp, "is_available", True))
        comp_name = getattr(comp, "name", type(comp).__name__)
        st.write(f"{'✅' if is_ready else '❌'} {comp_name}")
    st.write(f"{'✅' if pipeline.detector.is_loaded else '⚪'} Medical model")
    st.divider()
    st.subheader("Phases")
    for num, name, done in PHASES:
        st.write(f"{'✅' if done else '⬜'} {num}. {name}")

# ---- Main -----------------------------------------------------------------
st.title(config.PROJECT_NAME)
st.caption(f"{config.PROJECT_ID} · standalone prototype")

upload = st.file_uploader("Upload an X-ray",
                          type=[e.lstrip(".") for e in config.SUPPORTED_EXTENSIONS])

result = None
notice = None
if upload is not None and st.button("Analyze", type="primary"):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / upload.name
        path.write_bytes(upload.getvalue())
        try:
            result = pipeline.run(path)
        except NotImplementedError as exc:
            notice = str(exc)
        except Exception as exc:  # surface errors in the UI, not a stack trace
            st.error(str(exc))

if notice:
    st.info(f"Not implemented yet: {notice}")

tabs = st.tabs(["Original", "Processed", "Quality", "Detections",
                "Heatmap", "Segmentation", "JSON"])

with tabs[0]:
    if upload is not None:
        if upload.name.lower().endswith(".dcm"):
            with tempfile.NamedTemporaryFile(suffix=".dcm", delete=False) as tmp:
                tmp.write(upload.getvalue())
                tmp_path = Path(tmp.name)
            try:
                loaded = pipeline.loader.load(tmp_path)
                st.image(loaded.image, caption=f"Original DICOM: {upload.name}", use_container_width=True)
            except Exception as e:
                st.error(f"Failed to display DICOM: {e}")
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()
        else:
            st.image(upload, use_container_width=True)
    else:
        st.caption("Upload an image to begin.")


with tabs[1]:
    show_image(result.visualization.processed_path if result and result.visualization else None,
               2, "Preprocessed image")

with tabs[2]:
    if result and result.quality:
        q = result.quality
        st.metric("Quality", q.level.value, f"score {q.score:.2f}")
        cols = st.columns(4)
        for col, (label, val) in zip(cols, [("Blur", q.blur), ("Brightness", q.brightness),
                                            ("Contrast", q.contrast), ("Noise", q.noise)]):
            col.metric(label, "—" if val is None else f"{val:.1f}")
        for issue in q.issues:
            st.warning(issue)
    else:
        pending(3, "Quality report")

with tabs[3]:
    if not pipeline.detector.is_loaded:
        st.caption("No medical model loaded — detections available in Phase 4/5.")
    elif result and result.detections:
        st.dataframe([{"label": d.label, "confidence": round(d.confidence, 3)}
                      for d in result.detections])
        show_image(result.visualization.overlay_path if result.visualization else None,
                   5, "Overlay")
    else:
        st.caption("No findings reported.")

with tabs[4]:
    show_image(result.visualization.heatmap_path if result and result.visualization else None,
               6, "Heatmap")

with tabs[5]:
    st.info(
        "Pixel-level segmentation is unavailable because the RSNA Pneumonia Detection "
        "Challenge dataset provides bounding-box annotations, not pixel-level masks. "
        "The system explicitly declares segmentation unavailable rather than fabricating artificial masks."
    )
    show_image(result.visualization.mask_path if result and result.visualization else None,
               7, "Segmentation mask")

with tabs[6]:
    if result:
        st.subheader("CV ➔ GenAI Handshake Schema (Phase 9)")
        st.json(result.to_genai_dict())
        with st.expander("Complete Internal Pipeline Result"):
            st.json(result.to_dict())
    else:
        pending(9, "Structured JSON result")
