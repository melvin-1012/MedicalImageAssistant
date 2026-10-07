# medical_cv — Medical Computer Vision Engine (HNX26PSI05)

Standalone computer vision engine for **Multimodal Medical Image Intelligence** (Hackathon Project HNX26PSI05).
Responsible strictly for medical image intake, decodability validation, quality assessment, OpenCV preprocessing, deep-learning abnormality detection, coordinate localization, explainability heatmaps, segmentation handling, confidence/evidence preservation, and structured JSON contracts. Authentication, database, LLM orchestration, and frontend clinical UI are maintained separately.

---

## Architecture & End-to-End Pipeline (Batch 1 + Batch 2 + Batch 3)

```
Input Image (DICOM / PNG / JPG)
  │
  ▼
[Phase 1: ImageLoader] ──────► Reads via cv2.imdecode(np.fromfile) / pydicom
  │                            Preserves bit depth, normalizes channels, scrubs PHI
  ▼
[Phase 1: ImageValidator] ───► Rejects blank, corrupted, or out-of-spec scans
  │                            Collects all failures; rejects without crashing
  ▼
[Phase 3: QualityAnalyzer] ──► Evaluated on ORIGINAL 8-bit image (never on CLAHE)
  │                            Resolution-invariant blur, exposure, contrast, noise
  ▼
[Phase 2: Preprocessor] ─────► Non-mutating copy: grayscale, letterbox (640x640), CLAHE
  │                            Produces display uint8 + normalized float32 [0, 1]
  ▼
[Phase 4: MedicalDetector] ──► YOLO11n fine-tuned on real RSNA Pneumonia dataset
  │                            Outputs candidate boxes in 640x640 model coordinates
  ▼
[Phase 5: Localizer] ────────► Unpads letterbox margins, scales back to original DICOM (1024x1024)
  │                            Clips to boundary; guarantees <0.1px round-trip accuracy
  ▼
[Phase 6: HeatmapGenerator] ─► Model-grounded localization heatmap aligned to original scan
  │                            Returns None on zero detections (no fabricated overlays)
  ▼
[Phase 7: Segmenter] ────────► BaseSegmenter interface + NullSegmenter graceful fallback
  │                            Distinguishes unavailable vs completed; no fake masks
  ▼
[Phase 8: Evidence Layer] ───► Preserves genuine CV confidence, orig coords, conservative labels
  │                            Mandates physician review flag on all findings
  ▼
[Phase 9: Structured JSON] ──► Stable, deterministic CV → GenAI handshake JSON contract
```

---

## Batch Status Summary

| Batch | Phase | Module | Status | Description |
|---|---|---|---|---|
| **Batch 1** | **Phase 1** | `image_loader`, `validator` | **Complete** | DICOM (.dcm), PNG, JPG loading, MONOCHROME inversion, bit-depth scaling, PHI scrubbing, decodability checks. |
| | **Phase 2** | `preprocessing`, `coordinates` | **Complete** | Aspect-preserving letterboxing to 640x640, CLAHE contrast enhancement, bidirectional coordinate transforms. |
| | **Phase 3** | `quality` | **Complete** | Resolution-invariant blur, brightness, clipped fraction, contrast, Immerkaer noise on original radiographs. |
| **Batch 2** | **Phase 4** | `dataset`, `detector` | **Complete** | RSNA dataset conversion, YOLO11n detector training on real RSNA data, `MedicalDetector` abstraction. |
| | **Phase 5** | `localization`, `visualization`| **Complete** | Letterbox offset removal, coordinate restoration to original 1024x1024 space, amber bounding-box overlays. |
| | **Phase 6** | `heatmap` | **Complete** | Model-grounded localization heatmap strictly tied to predictions, letterbox unpadding, no fake overlays. |
| **Batch 3** | **Phase 7** | `segmentation` | **Complete** | `BaseSegmenter` interface, `NullSegmenter` honest fallback (RSNA has no pixel masks), `MaskProcessor`. |
| | **Phase 8** | `schemas` (Evidence) | **Complete** | Evidence preservation: genuine CV confidence, original DICOM $\{x_1, y_1, x_2, y_2\}$, physician review flag. |
| | **Phase 9** | `schemas` (Contract) | **Complete** | Deterministic CV → GenAI handshake JSON contract (`to_genai_dict`, `to_genai_json`). |
| **Batch 4** | **Phase 10**| `integration` | Pending | End-to-end web platform and external API integration. |

---

## Conventions & Medical Safety Standards

- **Conservative Medical Terminology:** Findings are strictly designated `"Possible abnormal opacity"` (`"possible_abnormal_opacity"`) rather than asserting diagnostic certainty ("Pneumonia confirmed").
- **No Ground-Truth Fabrication:** The RSNA Pneumonia Detection Challenge provides bounding boxes, not pixel masks. We strictly report segmentation as unavailable (`segmentation_available: false`, `segmentation: null`) instead of rasterizing bounding boxes into fake masks.
- **HIPAA / PHI De-identification:** The DICOM loader strictly strips all Protected Health Information (`PatientName`, `PatientID`, `PatientBirthDate`, `PatientAge`, `PatientSex`). `patientId` is used solely as a filename stem and is never logged.
- **Image Immutability:** Input image arrays are **never modified in-place**. Every processing step creates an explicit, isolated copy.
- **Coordinate Space Authority:** Bounding boxes always refer to the **original** full-resolution DICOM coordinates ($1024 \times 1024$), never to resized or letterboxed model space.
- **Confidence Authority:** Model confidences originate strictly from CV head predictions. Downstream LLMs/GenAI modules cannot alter coordinates or confidence values.
- **Mandatory Physician Review:** Every finding sets `requires_physician_review: true` and `no_confirmed_diagnosis: true`.
- **Confidence Threshold Calibration (Hackathon Demo Operating Point):** The detector's default confidence threshold is set to `0.016` in `DetectorConfig` (`config.py`). This operating threshold is tuned specifically for hackathon demo workflows with preliminary model checkpoints (raw confidence outputs cluster around `~0.015 - 0.018`). It is **not** a clinically validated diagnostic cut-off. The threshold is dynamically adjustable via the Streamlit slider (`step=0.001`), the CLI (`--conf`), and detector parameters.
- **Non-Clinical Disclaimer:** This software is developed strictly for research and hackathon exploration (`HNX26PSI05`). It is **not** validated for clinical diagnostic use.

---

## Phase Details

### Phase 1: Image Loading & Validation
- **Formats:** `.dcm`, `.png`, `.jpg`, `.jpeg`.
- **DICOM Handling:** Rescale slope/intercept applied, `MONOCHROME1` inverted to standard `MONOCHROME2` (air=dark, bone=bright), VOI LUT windowing scaled to 8-bit.
- **Validation:** File integrity, non-empty bytes, dimension bounds (`128x128` to `10000x10000`), channel validation, flat/blank scan detection (`std < 2.0`), saturation check (`> 98%`). Rejection occurs gracefully without exceptions.

### Phase 2: OpenCV Preprocessing & Coordinate Math
- **Letterbox Resize:** Preserves aspect ratio with zero-padding (black borders) to model input dimensions (`640x640`).
- **CLAHE:** Contrast Limited Adaptive Histogram Equalization (`clip_limit=2.0`, `tile_grid=(8, 8)`).
- **Coordinate Math (`cv/coordinates.py`):** `ResizeTransform` tracks exact scaling factor and `(pad_x, pad_y)` offsets for lossless bidirectional coordinate translation between original scan space and model input space.

### Phase 3: Image Quality Assessment & Calibration
- Evaluated strictly on the **original** 8-bit image prior to CLAHE or normalization.
- Evaluates:
  - Laplacian variance blur score on a normalized `512x512` reference grid.
  - Mean brightness and over/under-exposure clipping fraction (`<= 1` or `>= 254`).
  - Pixel standard deviation contrast.
  - Immerkaer noise standard deviation estimation.
- Classifies into `GOOD` (≥ 0.75), `MODERATE` (≥ 0.50), or `POOR` (< 0.50).

### Phase 4: Model Integration & RSNA Dataset Training
- **Dataset Inspector & Converter (`cv/dataset.py`):**
  - Parses `stage_2_train_labels.csv` (26,684 patients, 6,012 positive, 9,555 boxes).
  - Creates deterministic, patient-level 80/10/10 train/val/test splits with **zero patient leakage**.
  - Converts balanced cohorts into standard YOLO format (`images/{train,val,test}` and `labels/{train,val,test}`).
- **Detector Abstraction (`cv/detector.py`):**
  - Model-agnostic `MedicalDetector` interface (`load_model`, `predict`, `train`, `get_model_info`).
  - `YOLOMedicalDetector` implementing Ultralytics YOLO11n.
  - Auto-discovers weights from `models/model.pt` or falls back safely to `NullDetector`.
  - Configurable confidence threshold (default: `0.016` demo threshold, configurable via config/CLI/UI) and IoU threshold (`0.45`).
- **Training & Calibration Pipeline (`scripts/`):**
  - `train_yolo.py`: Trains YOLO11n on converted RSNA cohorts with AdamW optimizer, mixed precision (AMP), and configurable epochs/batch size.
  - `evaluate_and_calibrate.py`: Evaluates validation metrics (Precision, Recall, mAP@0.5, mAP@0.5:0.95), computes BoxF1 optimal confidence threshold, and verifies known positive and negative test radiographs.

### Phase 5: Bounding-Box Localization & Coordinate Restoration
- **Localization Engine (`cv/localization.py`):**
  - Maps model-space bounding boxes (640x640) back to original radiograph coordinates (e.g. 1024x1024).
  - Inverts letterbox padding offsets and scales by inverse factor.
  - Clips bounding coordinates to original image bounds `[0, orig_w]` and `[0, orig_h]`.
  - Rejects degenerate boxes; verified `<0.1px` coordinate round-trip accuracy.
- **Visual Overlays (`cv/visualization.py`):**
  - Renders amber/orange bounding boxes with text banners showing confidence (e.g., `Possible abnormal opacity (85%)`).

### Phase 6: Model-Grounded Heatmap Generation
- **Explainability Engine (`cv/heatmap.py`):**
  - `ModelHeatmapGenerator`: Produces 2D spatial attribution maps anchored to model detection regions and confidence weights.
  - Unpads letterbox borders and aligns heatmap to original radiograph dimensions (1024x1024).
  - Blends `COLORMAP_JET` false-color overlay with original radiograph while maintaining anatomical visibility.
  - Returns `None` on scans with 0 detections.

### Phase 7: Segmentation Interface & Graceful Fallback
- **Interface & Alignment (`cv/segmentation.py`):**
  - `BaseSegmenter`: Defines standard methods `segment()`, `is_available`, `ready`, and `align_to_original()`.
  - `NullSegmenter`: Correctly and transparently declares `is_available = False` with clinical justification:
    *"Pixel-level segmentation is unavailable because the RSNA dataset provides bounding-box annotations, not pixel-level masks."*
  - `MaskProcessor`: Morphological opening/closing (`cv2.morphologyEx`), contour extraction (`cv2.findContours`), and pixel area calculation for future mask sources.

### Phase 8: Confidence & Evidence Aggregation
- **Evidence Layer (`cv/schemas.py`):**
  - `FindingLocation`: Explicit $\{x_1, y_1, x_2, y_2\}$ pixel bounds in original radiograph space.
  - `FindingEvidence`: Structured evidence container preserving:
    - Genuine CV confidence directly from detector head
    - Heatmap and segmentation availability flags
    - Conservative label `"Possible abnormal opacity"`
    - Mandatory `requires_physician_review = True`

### Phase 9: Structured JSON Output (CV → GenAI Contract)
- **Deterministic Serialization (`cv/schemas.py`):**
  - `to_genai_dict()` and `to_genai_json()` implement the exact handshake contract consumed by the downstream GenAI module.
  - Guaranteed fields: `image`, `quality`, `findings`, `artifacts`, `safety`.

```json
{
  "image": {
    "source": "datasets/rsna/stage_2_train_images/05212f46-32b5-4350-812b-2bab7509d93f.dcm",
    "width": 1024,
    "height": 1024,
    "modality": "X-Ray"
  },
  "quality": {
    "status": "GOOD",
    "score": 1.0,
    "issues": []
  },
  "findings": [
    {
      "finding": "possible_abnormal_opacity",
      "finding_label": "Possible abnormal opacity",
      "confidence": 0.018,
      "location": {
        "x1": 109.6,
        "y1": 419.8,
        "x2": 333.6,
        "y2": 821.4
      },
      "heatmap_available": true,
      "segmentation_available": false,
      "requires_physician_review": true
    }
  ],
  "artifacts": {
    "original": "datasets/rsna/stage_2_train_images/05212f46-32b5-4350-812b-2bab7509d93f.dcm",
    "processed": "output/processed/05212f46-32b5-4350-812b-2bab7509d93f_processed.png",
    "detections": "output/processed/05212f46-32b5-4350-812b-2bab7509d93f_overlay.png",
    "heatmap": "output/processed/05212f46-32b5-4350-812b-2bab7509d93f_heatmap.png",
    "segmentation": null
  },
  "safety": {
    "physician_review_required": true,
    "no_confirmed_diagnosis": true
  }
}
```

---

## Project Structure

```
medical_cv/
├── config.py                 # Central configuration constants and paths
├── main.py                   # Command-line interface with --json and --genai
├── app.py                    # Streamlit web interface (Phases 1-9 status & outputs)
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules (weights, data, caches excluded)
├── README.md                 # Project architecture & documentation
├── cv/                       # Core CV engine
│   ├── __init__.py
│   ├── schemas.py            # Dataclasses, FindingEvidence, CVAnalysisResult, GenAI contract
│   ├── image_loader.py       # Phase 1: Image & DICOM loader + PHI scrubbing
│   ├── validator.py          # Phase 1: Decodability & integrity validation
│   ├── preprocessing.py      # Phase 2: Letterboxing, CLAHE, 8-bit scaling
│   ├── coordinates.py        # Phase 2: Bidirectional coordinate transforms
│   ├── quality.py            # Phase 3: Resolution-invariant quality assessment
│   ├── dataset.py            # Phase 4: RSNA dataset inspector & YOLO converter
│   ├── detector.py           # Phase 4: MedicalDetector & YOLOMedicalDetector
│   ├── localization.py       # Phase 5: Bounding-box coordinate restoration
│   ├── heatmap.py            # Phase 6: Model-grounded localization heatmaps
│   ├── visualization.py      # Phase 5/6: Overlays, heatmaps, mask blending
│   ├── segmentation.py       # Phase 7: BaseSegmenter, NullSegmenter, MaskProcessor
│   └── pipeline.py           # End-to-end orchestration pipeline
├── scripts/                  # Workflow scripts
│   ├── download_rsna.py         # Download RSNA dataset via Kaggle API
│   ├── evaluate_and_calibrate.py# Evaluate metrics & calibrate F1 confidence threshold
│   ├── prepare_yolo_dataset.py  # Convert RSNA DICOM to YOLO dataset
│   ├── train_yolo.py            # Train YOLO detector on RSNA dataset
│   └── verify_real_batch2.py    # Verify Batch 2 pipeline on DICOMs
├── models/                   # Model weight storage
│   ├── README.md
│   └── model.pt              # Trained real detector weights (excluded from git)
├── input/
│   └── sample_images/        # Sample DICOM and test radiographs
├── output/                   # Generated visual artifacts
│   ├── processed/
│   ├── overlays/
│   ├── heatmaps/
│   └── masks/
└── tests/                    # Complete pytest suite (96 tests)
    ├── conftest.py
    ├── check_cuda.py
    ├── inspect_dataset.py
    ├── calibrate_quality.py
    ├── test_loader.py
    ├── test_validator.py
    ├── test_preprocessing.py
    ├── test_coordinates.py
    ├── test_quality.py
    ├── test_dataset.py
    ├── test_detector.py
    ├── test_localization.py
    ├── test_heatmap.py
    ├── test_visualization.py
    ├── test_pipeline.py
    ├── test_pipeline_batch2.py
    └── test_batch3.py        # Phase 7, 8, 9 unit & contract tests
```

---

## Verification & Usage

### 1. Run Complete Test Suite
```bash
python -m pytest tests/
```
**96 unit tests passing (100% green)** covering:
- DICOM loader edge cases, MONOCHROME inversion, bit-depth scaling, PHI scrubbing
- Validator boundary conditions, blank/saturated rejection
- Letterbox resizing, CLAHE preprocessing, and coordinate math
- Resolution-invariant quality metrics (blur, exposure, contrast, noise)
- RSNA dataset CSV parsing, annotation validation, and patient leakage checks
- MedicalDetector lifecycle, NullDetector fallback, and YOLOMedicalDetector loading
- Phase 5 localization, box clipping, and coordinate restoration
- Phase 6 heatmap generation, letterbox unpadding, and overlay rendering
- Phase 7 NullSegmenter, MaskProcessor, morphological operations, unpadding alignment
- Phase 8 FindingEvidence, confidence preservation, original coordinate mapping
- Phase 9 CV → GenAI handshake JSON contract, deterministic serialization, safety flags

### 2. Run Command-Line Interface (CLI)
```bash
# Analyze a medical radiograph with terminal summary (uses default 0.016 demo threshold)
python main.py datasets/rsna/stage_2_train_images/00436515-870c-4b36-a041-de91049b9ab4.dcm

# Override detector confidence threshold
python main.py datasets/rsna/stage_2_train_images/00436515-870c-4b36-a041-de91049b9ab4.dcm --conf 0.016

# Output standard JSON result
python main.py datasets/rsna/stage_2_train_images/00436515-870c-4b36-a041-de91049b9ab4.dcm --json

# Output structured CV -> GenAI handshake contract JSON
python main.py datasets/rsna/stage_2_train_images/00436515-870c-4b36-a041-de91049b9ab4.dcm --genai
```

### 3. Launch Development UI
```bash
streamlit run app.py
```
Interactive multi-tab interface:
- **Inference Settings Sidebar:** Dynamic confidence threshold slider (default `0.016`, step `0.001`, range `0.001 - 0.950`) allowing live sensitivity tuning without restarting the server.
- **Original & Processed:** Side-by-side radiograph inspection with CLAHE toggle.
- **Quality Assessment:** Blur, brightness, contrast, and noise metrics with traffic-light status.
- **Detections:** Bounding box overlays on the original scan with confidence percentages.
- **Heatmap:** Model-grounded localization heatmap overlay.
- **Segmentation:** Phase 7 status & clinical rationale (reports honest unavailability).
- **GenAI Handshake:** Full deterministic CV → GenAI JSON contract display.

### 4. Run Model Evaluation & Threshold Calibration
```bash
# Evaluate validation split, compute BoxF1 optimal threshold, and verify cohorts
python scripts/evaluate_and_calibrate.py

# Train / fine-tune YOLO model on RSNA dataset
python scripts/train_yolo.py --epochs 35 --batch 8 --imgsz 640
```
Outputs validation metrics (Precision, Recall, mAP@0.5, mAP@0.5:0.95), calibrated operating threshold, and saves `output/evaluation_summary.json`.

