# medical_cv — Medical Computer Vision Engine (HNX26PSI05)

Standalone computer vision engine for **Multimodal Medical Image Intelligence** (Hackathon Project HNX26PSI05).
Responsible strictly for medical image intake, decodability validation, quality assessment, OpenCV preprocessing, deep-learning abnormality detection, coordinate localization, and explainability heatmaps. Authentication, database, LLM orchestration, and frontend clinical UI are maintained separately.

---

## Architecture & End-to-End Pipeline (Batch 1 + Batch 2)

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
[Visualizer & Output] ───────► Saves original, processed, comparison, bbox overlay, heatmap
  │
  ▼
[CVAnalysisResult] ──────────► Standardized JSON-serializable clinical data contract
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
| **Batch 3** | **Phase 7** | `segmentation` | Pending | Lung field and lesion anatomical segmentation. |
| | **Phase 8** | `confidence` | Pending | Multi-evidence aggregation and uncertainty calibration. |
| | **Phase 9** | `schemas` | Pending | Final structured clinical JSON schema delivery. |
| **Batch 4** | **Phase 10**| `integration` | Pending | End-to-end web platform and external API integration. |

---

## Conventions & Medical Safety Standards

- **Conservative Medical Terminology:** Findings are strictly designated `"Possible abnormal opacity"` rather than asserting diagnostic certainty ("Pneumonia confirmed").
- **HIPAA / PHI De-identification:** The DICOM loader strictly strips all Protected Health Information (`PatientName`, `PatientID`, `PatientBirthDate`, `PatientAge`, `PatientSex`). `patientId` is used solely as a filename stem and is never logged.
- **Image Immutability:** Input image arrays are **never modified in-place**. Every processing step creates an explicit, isolated copy.
- **Path Handling:** All disk I/O uses `np.fromfile` + `cv2.imdecode` to guarantee Windows path compatibility (spaces and non-ASCII paths).
- **Explainability Integrity:** Heatmaps are generated only when the model predicts actual candidate regions (`len(detections) > 0`). When zero detections exist, the heatmap generator returns `None`. We do not label bounding-box heatmaps as "Grad-CAM" because YOLO's anchor-free multi-scale detection head is mathematically incompatible with classification bottleneck Grad-CAM.
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
- **Training Pipeline (`scripts/train_yolo.py`):**
  - Fine-tunes YOLO on converted RSNA radiographs.
  - Saves weights to `models/pneumonia_yolo/train_run/weights/best.pt` and deploys to `models/model.pt`.

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

---

## Project Structure

```
medical_cv/
├── config.py                 # Central configuration constants and paths
├── main.py                   # Command-line interface
├── app.py                    # Streamlit web interface
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
├── cv/                       # Core CV engine
│   ├── __init__.py
│   ├── schemas.py            # Dataclasses & data contracts
│   ├── image_loader.py       # Phase 1: Image & DICOM loader + PHI scrubbing
│   ├── validator.py          # Phase 1: Decodability & integrity validation
│   ├── preprocessing.py      # Phase 2: Letterboxing, CLAHE, 8-bit scaling
│   ├── coordinates.py        # Phase 2: Bidirectional coordinate transforms
│   ├── quality.py            # Phase 3: Resolution-invariant quality assessment
│   ├── dataset.py            # Phase 4: RSNA dataset inspector & YOLO converter
│   ├── detector.py           # Phase 4: MedicalDetector & YOLOMedicalDetector
│   ├── localization.py       # Phase 5: Bounding-box coordinate restoration
│   ├── heatmap.py            # Phase 6: Model-grounded localization heatmaps
│   ├── visualization.py      # Comparison, bounding box overlay & heatmap blending
│   ├── segmentation.py       # Phase 7: Stubbed for Batch 3
│   └── pipeline.py           # End-to-end orchestration pipeline
├── scripts/                  # Workflow scripts
│   ├── prepare_yolo_dataset.py  # Convert RSNA DICOM to YOLO dataset
│   ├── train_yolo.py            # Train YOLO detector on RSNA dataset
│   └── verify_real_batch2.py    # Verify inference, localization & heatmaps on DICOMs
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
└── tests/                    # Complete pytest suite (86 tests)
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
    └── test_pipeline_batch2.py
```

---

## Verification & Usage

### 1. Run Complete Test Suite
```bash
python -m pytest tests/
```
**86 unit tests passing (100% green)** covering:
- DICOM loader edge cases, MONOCHROME inversion, bit-depth scaling, PHI scrubbing
- Validator boundary conditions, blank/saturated rejection
- Letterbox resizing, CLAHE preprocessing, and coordinate math
- Resolution-invariant quality metrics (blur, exposure, contrast, noise)
- RSNA dataset CSV parsing, annotation validation, and patient leakage checks
- MedicalDetector lifecycle, NullDetector fallback, and YOLOMedicalDetector loading
- Phase 5 localization, box clipping, and coordinate restoration
- Phase 6 heatmap generation, letterbox unpadding, and overlay rendering
- End-to-end pipeline execution with 0-detection, single-detection, and multi-detection findings

### 2. Run Batch 2 Verification Script
```bash
python scripts/verify_real_batch2.py
```
Executes real DICOM inference on positive and negative RSNA radiographs, verifies Phase 5 localization to original `1024x1024` space, generates Phase 6 model-grounded heatmaps, and writes visual artifacts and `verification_report.json` to `output/batch2_verification/`.

### 3. Run Command-Line Interface (CLI)
```bash
# Display initialization status and active detector
python main.py

# Analyze a medical radiograph with terminal summary
python main.py input/sample_images/sample_01.dcm

# Output structured JSON result
python main.py input/sample_images/sample_01.dcm --json
```

### 4. Launch Development UI
```bash
streamlit run app.py
```
Interactive multi-tab interface:
- **Original & Processed:** Side-by-side radiograph inspection with CLAHE toggle
- **Quality Assessment:** Blur, brightness, contrast, and noise metrics with traffic-light status
- **Detections:** Bounding box overlays on the original scan with confidence percentages
- **Heatmap:** Model-grounded localization heatmap overlay
- **Structured JSON:** Full clinical JSON data contract output

---

## Real Model Training (Reproducibility)

To reproduce the RSNA dataset conversion and YOLO model training:

```bash
# 1. Convert RSNA dataset to YOLO format (balanced cohort of 2,000 scans)
python scripts/prepare_yolo_dataset.py --dataset-dir datasets/rsna --limit 2000

# 2. Train YOLO detector
python scripts/train_yolo.py --epochs 25 --batch 8 --imgsz 640
```
Trained weights are automatically saved to `models/pneumonia_yolo/train_run/weights/best.pt` and deployed to `models/model.pt`.
