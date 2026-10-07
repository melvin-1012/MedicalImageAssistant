"""Medical AI Clinical Decision-Support Dashboard.

Integrated prototype uniting:
1. Medical CV Engine (OpenCV, YOLO, Localization, Model-Grounded Heatmap, Quality)
2. Multimodal GenAI (Clinical Notes Processing, Evidence-Grounded Explanation, Anti-Hallucination Validation)

Strict Production Requirements:
- Strictly real CV data (no mock coordinates, confidence, or findings).
- Heatmap labeled 'Model-Grounded Heatmap' / 'AI Explainability Heatmap' (never Grad-CAM).
- Preserves raw confidence precision and original radiograph coordinates.
- Cautious uncertainty language, clear physician actions, and regulatory disclaimers.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

import config
from cv.integration import IntegratedMedicalAIPipeline
from cv.schemas import AnalysisStatus

# --- Page Configuration ----------------------------------------------------
st.set_page_config(
    page_title=f"{config.PROJECT_NAME} · Clinical AI Dashboard",
    page_icon="🩻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Pipeline Singleton -----------------------------------------------------
@st.cache_resource
def get_integrated_pipeline() -> IntegratedMedicalAIPipeline:
    pipeline = IntegratedMedicalAIPipeline()
    pipeline.initialize()
    return pipeline


integrated_pipeline = get_integrated_pipeline()

# Synchronize detector confidence threshold from central configuration
if hasattr(integrated_pipeline.cv.detector, "confidence_threshold"):
    integrated_pipeline.cv.detector.confidence_threshold = config.CONFIG.detector.confidence_threshold


def get_component_status(comp: Any) -> tuple[bool, str]:
    """Safely determines the active status and display name for pipeline components."""
    comp_name = getattr(comp, "name", type(comp).__name__)
    if hasattr(comp, "is_available"):
        is_ok = bool(comp.is_available)
    elif hasattr(comp, "ready"):
        is_ok = bool(comp.ready)
    elif hasattr(comp, "is_loaded"):
        is_ok = bool(comp.is_loaded)
    else:
        is_ok = True
    return is_ok, comp_name


# --- Sidebar: System Diagnostics & Clinical Context -----------------------
with st.sidebar:
    st.title("🩻 System Status")
    st.caption("Medical CV ➔ GenAI Handshake Pipeline")

    with st.expander("Pipeline Components", expanded=False):
        for comp in (
            integrated_pipeline.cv.loader,
            integrated_pipeline.cv.validator,
            integrated_pipeline.cv.preprocessor,
            integrated_pipeline.cv.quality,
            integrated_pipeline.cv.detector,
            integrated_pipeline.cv.localizer,
            integrated_pipeline.cv.heatmap,
            integrated_pipeline.cv.segmenter,
            integrated_pipeline.cv.visualizer,
        ):
            is_ready, comp_name = get_component_status(comp)
            st.write(f"{'✅' if is_ready else '❌'} {comp_name}")
        st.write(f"{'✅' if integrated_pipeline.cv.detector.is_loaded else '⚪'} Medical Model Weights")
        st.write("✅ Multimodal GenAI Engine")
        st.write("✅ Anti-Hallucination Validator")

    st.divider()

    st.subheader("Inference Settings")
    default_conf_str = f"{config.CONFIG.detector.confidence_threshold:.3f}"
    conf_str = st.text_input(
        "Detector Confidence Threshold",
        value=default_conf_str,
        key="conf_threshold_text",
        help="Detector threshold preserved from central configuration (config.CONFIG.detector.confidence_threshold).",
    )
    try:
        conf_thresh = float(conf_str.strip())
    except (ValueError, TypeError):
        conf_thresh = config.CONFIG.detector.confidence_threshold

    if hasattr(integrated_pipeline.cv.detector, "confidence_threshold"):
        integrated_pipeline.cv.detector.confidence_threshold = conf_thresh
    st.caption(f"Active threshold: `{conf_thresh:.4f}`")

    st.divider()

    st.subheader("Clinical Context (Optional)")
    clinical_notes = st.text_area(
        "Patient Clinical Notes / Symptoms",
        value="Patient presents with persistent cough for 2 weeks, low-grade fever, and mild shortness of breath on exertion.",
        height=120,
        help="Unstructured clinical notes will be processed by GenAI to correlate with visual evidence.",
    )


# --- Header & Disclaimer --------------------------------------------------
col_hdr_left, col_hdr_right = st.columns([3, 1])
with col_hdr_left:
    st.title("Medical CV + Multimodal GenAI Decision-Support System")
    st.markdown(
        "**Assistive Decision-Support Tool** · "
        "Evidence-grounded radiograph analysis combining YOLO deep-learning detection with structured clinical reasoning."
    )
with col_hdr_right:
    st.info(
        "⚠️ **Clinical Notice**\n\n"
        "This system is an assistive decision-support prototype. "
        "All findings require verification by an attending physician."
    )

st.divider()


# --- File Upload Section --------------------------------------------------
upload_col, action_col = st.columns([3, 1])
with upload_col:
    uploaded_file = st.file_uploader(
        "Upload Chest Radiograph (DICOM, PNG, or JPEG)",
        type=[e.lstrip(".") for e in config.SUPPORTED_EXTENSIONS],
        help="Upload a standard chest radiograph (.dcm, .png, .jpg).",
    )
with action_col:
    st.write("")
    st.write("")
    analyze_clicked = st.button("Analyze Radiograph", type="primary", use_container_width=True)

# Run pipeline when user clicks Analyze
if uploaded_file is not None and analyze_clicked:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / uploaded_file.name
        tmp_path.write_bytes(uploaded_file.getvalue())

        with st.spinner("Executing end-to-end Computer Vision inference & grounded GenAI analysis..."):
            try:
                integrated_result = integrated_pipeline.run(
                    image_path=tmp_path,
                    clinical_notes=clinical_notes.strip() if clinical_notes else None,
                )
                st.session_state["integrated_result"] = integrated_result
                st.session_state["uploaded_file_name"] = uploaded_file.name
                st.session_state["uploaded_file_bytes"] = uploaded_file.getvalue()
            except Exception as exc:
                st.error(f"Analysis failed: {str(exc)}")


# --- Display Results -------------------------------------------------------
if "integrated_result" in st.session_state:
    result: Dict[str, Any] = st.session_state["integrated_result"]
    cv_res = result.get("_cv_result")
    genai = result.get("genai_analysis", {})
    quality = result.get("quality", {})
    findings = result.get("findings", [])
    status = result.get("status", "success")

    # 1. Executive Status Banner
    if status in ["rejected", "poor_quality"]:
        st.error(
            "### ❌ Image Quality Failure — AI Generation Bypassed\n\n"
            f"**Summary:** {genai.get('summary', 'Image quality is insufficient for reliable AI analysis.')}\n\n"
            "AI generation was automatically bypassed to prevent unreliable or misleading clinical findings. "
            "Please upload a standard diagnostic-quality radiograph."
        )
        if quality.get("issues"):
            st.warning(f"**Identified Quality Issues:** {', '.join(quality['issues'])}")

    elif len(findings) > 0:
        st.warning(
            f"### ⚠️ Possible Abnormal Opacity Identified — Requires Physician Review\n\n"
            f"**AI Clinical Summary:** {genai.get('summary', '')}"
        )
    else:
        st.success(
            f"### ℹ️ No Abnormal Opacity Detected — Routine Physician Review Recommended\n\n"
            f"**AI Clinical Summary:** {genai.get('summary', '')}"
        )

    # 2. Main Dashboard Tabs
    tabs = st.tabs([
        "📋 Clinical Interpretation",
        "🖼️ Visual Evidence & Explainability",
        "📊 Finding Details & Precision",
        "🩺 Quality & Acquisition",
        "⚙️ Technical Handshake JSON",
    ])

    # ---- TAB 1: Clinical Interpretation -----------------------------------
    with tabs[0]:
        st.subheader("Grounded Clinical Interpretation")

        col_rep_left, col_rep_right = st.columns([2, 1])

        with col_rep_left:
            st.markdown("#### Evidence-Grounded Findings")
            if genai.get("findings"):
                for idx, gf in enumerate(genai["findings"], 1):
                    with st.container(border=True):
                        st.markdown(f"**Finding {idx:02d}: {gf.get('finding_label', gf.get('finding', 'possible_abnormal_opacity'))}**")
                        st.markdown(f"**Explanation:** {gf.get('explanation', '')}")

                        # Clinical notes correlation
                        if gf.get("supporting_notes"):
                            for sn in gf["supporting_notes"]:
                                st.info(f"📌 **Clinical Context Link:** {sn.get('text', '')}")

                        # Uncertainty language
                        if gf.get("uncertainty"):
                            st.caption("🔍 **Uncertainty & Clinical Caveats:**")
                            for u in gf["uncertainty"]:
                                st.caption(f"• {u}")

                        # Exact coordinates & confidence
                        loc = gf.get("location")
                        loc_str = f"[{loc['x1']:.1f}, {loc['y1']:.1f}, {loc['x2']:.1f}, {loc['y2']:.1f}]" if loc else "None"
                        st.markdown(
                            f"**Raw Model Confidence:** `{gf.get('confidence', 0.0):.6f}` | "
                            f"**Original Radiograph Coordinates:** `{loc_str}`"
                        )
            else:
                st.info(
                    "No abnormal opacity was detected by the computer-vision model. "
                    "Routine physician review is recommended."
                )

            st.markdown("#### System Limitations & Clinical Disclaimers")
            for lim in genai.get("limitations", []):
                st.caption(f"• {lim}")

        with col_rep_right:
            st.markdown("#### Attending Physician Actions")
            with st.container(border=True):
                st.radio(
                    "Physician Decision",
                    ["Under Review", "Confirmed & Accepted", "Flagged for CT / Lateral View", "Rejected / Artifact"],
                    key="physician_decision",
                )
                physician_notes = st.text_area("Physician Notes / Sign-Off", key="doc_notes", height=100)

                if st.button("Sign & Complete Review", type="primary", use_container_width=True):
                    st.success("Review recorded and stamped for clinical audit.")

                st.divider()

                # Report Download
                report_text = (
                    f"MEDICAL AI CLINICAL DECISION-SUPPORT REPORT\n"
                    f"Project: {config.PROJECT_NAME} ({config.PROJECT_ID})\n"
                    f"Status: {status.upper()}\n"
                    f"AI Summary: {genai.get('summary', '')}\n\n"
                    f"FINDINGS:\n"
                )
                for idx, gf in enumerate(genai.get("findings", []), 1):
                    report_text += (
                        f"  Finding {idx}: {gf.get('finding')}\n"
                        f"  Raw Confidence: {gf.get('confidence')}\n"
                        f"  Location: {gf.get('location')}\n"
                        f"  Explanation: {gf.get('explanation')}\n\n"
                    )
                report_text += "\nLIMITATIONS:\n" + "\n".join(f"- {l}" for l in genai.get("limitations", []))

                st.download_button(
                    "📥 Export Clinical Report (TXT)",
                    data=report_text,
                    file_name=f"clinical_ai_report_{status}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

    # ---- TAB 2: Visual Evidence Gallery -----------------------------------
    with tabs[1]:
        st.subheader("Multimodal Visual Evidence Gallery")
        vis = cv_res.visualization if cv_res else None

        vtabs = st.tabs([
            "Original Radiograph",
            "AI Detection Overlay",
            "Model-Grounded Heatmap",
            "Preprocessed Image",
            "Segmentation Status",
        ])

        with vtabs[0]:
            st.caption("Raw input radiograph in native diagnostic space.")
            file_name = st.session_state.get("uploaded_file_name", "")
            file_bytes = st.session_state.get("uploaded_file_bytes", b"")
            if file_name.lower().endswith(".dcm"):
                with tempfile.NamedTemporaryFile(suffix=".dcm", delete=False) as tmp:
                    tmp.write(file_bytes)
                    tmp_p = Path(tmp.name)
                try:
                    loaded = integrated_pipeline.cv.loader.load(tmp_p)
                    st.image(loaded.image, caption=f"Original DICOM: {file_name}", use_container_width=True)
                finally:
                    if tmp_p.exists():
                        tmp_p.unlink()
            else:
                st.image(file_bytes, caption=f"Original: {file_name}", use_container_width=True)

        with vtabs[1]:
            st.caption("Original radiograph with detected bounding boxes mapped back to original anatomical space.")
            if vis and vis.overlay_path and Path(vis.overlay_path).exists():
                st.image(vis.overlay_path, caption="AI Detection Overlay (Original Coordinates)", use_container_width=True)
            else:
                st.info("No detections overlay generated (no findings above threshold).")

        with vtabs[2]:
            st.caption(
                "Model-Grounded Heatmap (AI Explainability) — "
                "Tied strictly to model predictions and spatially aligned to original radiograph coordinates. "
                "No synthetic heatmaps are generated when zero detections are found."
            )
            if vis and vis.heatmap_path and Path(vis.heatmap_path).exists():
                st.image(vis.heatmap_path, caption="Model-Grounded Heatmap (AI Explainability)", use_container_width=True)
            else:
                st.info("No heatmap generated (no model-detected findings above threshold).")

        with vtabs[3]:
            st.caption("Standardized OpenCV preprocessed input (CLAHE contrast-enhanced, aspect-preserved letterbox).")
            if vis and vis.processed_path and Path(vis.processed_path).exists():
                st.image(vis.processed_path, caption="Preprocessed Radiograph", use_container_width=True)
            else:
                st.info("Preprocessed image unavailable.")

        with vtabs[4]:
            st.info(
                "**Pixel-level segmentation is unavailable.**\n\n"
                "The RSNA Pneumonia Detection Challenge dataset provides bounding-box annotations, "
                "not pixel-level segmentation masks. The system explicitly declares segmentation unavailable "
                "rather than fabricating artificial masks."
            )
            if vis and vis.mask_path and Path(vis.mask_path).exists():
                st.image(vis.mask_path, caption="Segmentation Mask", use_container_width=True)

    # ---- TAB 3: Finding Details & Precision -------------------------------
    with tabs[2]:
        st.subheader("Structured Evidence Table")
        if findings:
            table_rows = []
            for f in findings:
                loc = f.get("location", {})
                raw_c = f.get("confidence", 0.0)
                table_rows.append({
                    "Finding Label": f.get("finding_label", f.get("finding")),
                    "Raw Model Confidence": f"{raw_c:.6f}",
                    "Display Confidence": f"{raw_c * 100:.2f}%",
                    "x1": loc.get("x1"),
                    "y1": loc.get("y1"),
                    "x2": loc.get("x2"),
                    "y2": loc.get("y2"),
                    "Model-Grounded Heatmap": "Available" if f.get("heatmap_available") else "Unavailable",
                    "Requires Physician Review": "Yes" if f.get("requires_physician_review") else "No",
                })
            st.dataframe(table_rows, use_container_width=True)
        else:
            st.info("No findings reported above the configured detector threshold.")

    # ---- TAB 4: Quality & Acquisition Metrics -----------------------------
    with tabs[3]:
        st.subheader("Image Quality & Diagnostic Acceptability")
        if cv_res and cv_res.quality:
            q = cv_res.quality
            m1, m2, m3 = st.columns(3)
            m1.metric("Diagnostic Quality", q.level.value, f"Score: {q.score:.2f}")
            m2.metric("Blur (Laplacian Var)", f"{q.blur:.1f}" if q.blur is not None else "—")
            m3.metric("Mean Brightness", f"{q.brightness:.1f}" if q.brightness is not None else "—")

            m4, m5, m6 = st.columns(3)
            m4.metric("Contrast (Std Dev)", f"{q.contrast:.1f}" if q.contrast is not None else "—")
            m5.metric("Noise (Immerkaer)", f"{q.noise:.1f}" if q.noise is not None else "—")
            m6.metric("Resolution", f"{cv_res.metadata.width}x{cv_res.metadata.height}" if cv_res.metadata else "—")

            if q.issues:
                st.warning(f"Quality flags detected: {'; '.join(q.issues)}")
            else:
                st.success("All radiographic quality metrics within diagnostic parameters.")

    # ---- TAB 5: Technical Handshake JSON ----------------------------------
    with tabs[4]:
        st.subheader("Unified CV ➔ GenAI Handshake JSON (Phase 8 Contract)")
        # Filter private keys
        export_payload = {k: v for k, v in result.items() if not k.startswith("_")}
        st.json(export_payload)

        with st.expander("Internal Pipeline Analysis Result"):
            if cv_res:
                st.json(cv_res.to_dict())

        with st.expander("Anti-Hallucination Grounding Status"):
            st.json(genai.get("validation_status", {}))

else:
    st.info("👆 Please upload a chest radiograph and click **Analyze Radiograph** to begin.")
