# medical_cv — Medical Computer Vision Engine (HNX26PSI05)

Standalone computer vision engine for **Multimodal Medical Image Intelligence** (Hackathon Project HNX26PSI05).
Responsible strictly for medical image intake, decodability validation, quality assessment, OpenCV preprocessing, and visual artifact generation. Auth, database, LLM orchestration, and frontend clinical UI are maintained separately.

---

## Architecture & Separation of Concerns

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
[Phase 2: Preprocessor] ─────► Non-mutating copy: grayscale, letterbox, CLAHE
  │                            Produces display uint8 + normalized float32 [0, 1]
  ▼
[Visualizer & Output] ───────► Saves <stem>_processed.png and <stem>_comparison.png
  │
  ▼
[CVAnalysisResult] ──────────► Standardized JSON-serializable clinical data contract
```

### Three Separated Concerns

| Concern | Modules | Status | Behavior in Batch 1 |
|---|---|---|---|
| **1. Image Processing** | `image_loader`, `validator`, `preprocessing`, `quality` | **Phases 1–3 Complete** | Pure OpenCV & NumPy operations; zero model dependency. |
| **2. Model Inference** | `detector` (`BaseDetector`) | Stubbed (Phase 4) | `NullDetector` (`is_loaded = False`). No fake detections or artificial scores. |
| **3. Visual Explainability**| `visualization`, `coordinates`, `localization` | Partially active | Side-by-side comparison renderer active; bounding-box & heatmap layers ready for Phases 5–7. |

---

## Conventions & Standards

- **In-Memory Channel Order:** RGB for color images, 2D single-channel `uint8` for grayscale medical radiographs.
- **Path Handling:** All disk I/O uses `np.fromfile` + `cv2.imdecode` to ensure compatibility with Windows paths containing spaces or non-ASCII characters.
- **Image Immutability:** The input image array is **never modified in-place**. Every processing step creates a copy.
- **HIPAA / PHI De-identification:** DICOM loader strictly strips all Protected Health Information (`PatientName`, `PatientID`, `PatientBirthDate`, `PatientAge`, `PatientSex`). `patientId` is used solely as a filename stem and is never logged.
- **Lazy Dependencies:** `pydicom` is imported lazily inside `cv/image_loader.py` so standard PNG/JPG processing functions even if DICOM libraries are not installed.

---

## Phase Breakdown

### Phase 1: Image Loading & Validation
- **Formats:** Supports `.dcm`, `.png`, `.jpg`, `.jpeg`.
- **Bit Depths:** Native 8-bit and 16-bit grayscale. Multi-channel RGBA (alpha stripped) and BGR (converted to RGB).
- **DICOM Handling:**
  - Rescale slope and intercept applied when present: `pixel * slope + intercept`.
  - `MONOCHROME1` inverted to standard radiologic `MONOCHROME2` representation (air=dark, bone=bright).
  - VOI LUT Windowing via `WindowCenter` and `WindowWidth` scaled to 8-bit `uint8`.
  - Missing optional tags handled gracefully.
- **Validation Constraints:**
  - File existence, regular file check, and non-empty size.
  - Dimensions bounded within `[min_width, max_width]` and `[min_height, max_height]` (128px to 10000px).
  - Channel validation (1 or 3 channels).
  - Blank / flat image detection (`std < 2.0`).
  - Saturation check (> 98% pixels saturated black or white).
  - Aggregates **all** failure reasons into `result.errors`.

### Phase 2: OpenCV Preprocessing & Coordinate Math
- **Grayscale Conversion:** Standardizes multi-channel images to 8-bit single-channel arrays.
- **Letterbox Resize:** Generic aspect-preserving resize with zero-padding (black borders) to model input size (default: `640x640`). Works across square, landscape, and portrait inputs.
- **CLAHE Enhancement:** Contrast Limited Adaptive Histogram Equalization (`clip_limit=2.0`, `tile_grid=(8, 8)`).
- **Dual Outputs:**
  - `image`: Display-safe `uint8` image for visualization and reporting.
  - `model_input`: Normalized `float32` array in `[0.0, 1.0]` ready for downstream neural networks.
- **Coordinate Transformations (`cv/coordinates.py`):**
  - `ResizeTransform` tracks exact scale and `(pad_x, pad_y)` offsets.
  - Bidirectional mappings `to_model` and `to_original` guarantee box reconstruction within 1 pixel.

### Phase 3: Image Quality Assessment & Calibration
- **Strict Rule:** Quality is evaluated on the **ORIGINAL** 8-bit grayscale image, never on CLAHE-enhanced outputs.
- **Metrics Evaluated:**
  - **Blur / Sharpness:** Laplacian variance computed on a fixed reference resolution (`512x512`) to ensure resolution-invariant thresholding.
  - **Brightness & Exposure:** Mean pixel intensity, with clipped pixel fraction tracking under- and over-exposure.
  - **Contrast:** Pixel standard deviation and 2nd–98th percentile dynamic range.
  - **Noise:** Immerkaer robust noise standard deviation estimation.
  - **Resolution:** Spatial pixel dimensions against minimum diagnostic thresholds (`256x256`).
- **Scoring & Classification:**
  - Composite score (0.0 to 1.0) combining weighted sub-scores.
  - Mapped to `GOOD` (score ≥ 0.75, no issues), `MODERATE` (score ≥ 0.50), or `POOR` (score < 0.50 or critical defects).
  - `POOR` quality logs diagnostic warnings in `result.warnings` but **does not reject** the image.

---

## Dataset & Quality Calibration (RSNA Pneumonia Challenge)

- Configured via `config.DATASET_DIR` or the `DATASET_DIR` environment variable.
- Run the dataset calibration and degradation verification suite:
  ```bash
  python -m tests.calibrate_quality input/sample_images
  ```
- Or run the inspection script across any DICOM directory:
  ```bash
  python tests/inspect_dataset.py [path_to_dicom_folder]
  ```

### Calibrated Threshold Values

| Metric | Threshold | Justification |
|---|---|---|
| **Blur (Laplacian Var)** | `80.0` (on 512x512) | Sharp radiographs score > 200–500; heavy motion blur drops < 30. |
| **Brightness Range** | `[40.0, 215.0]` | Typical chest X-rays center at ~80–120; values < 40 indicate severe underexposure. |
| **Clipping Fraction** | `0.20` (20%) | Flags overexposed burnout or severe border saturation. |
| **Contrast (Std Dev)** | `25.0` | Standard diagnostic chest dynamic range yields std of 50–70; < 25 indicates flat, low-contrast scans. |
| **Noise (Sigma)** | `18.0` | Normal radiographic noise is < 5–8; excessive quantum mottle or sensor noise exceeds 18. |

---

## Verification & Commands

### 1. Run Complete Test Suite
```bash
pytest -v
```
All **47 tests** cover loader edge cases, validation, letterboxing, coordinate roundtrips, quality degradations, and end-to-end pipeline execution.

### 2. Run CLI
```bash
# Display initialization banner
python main.py

# Analyze a sample image and view readable summary
python main.py input/sample_images/sample_01.dcm

# Export full structured JSON result
python main.py input/sample_images/sample_01.dcm --json
```

### 3. Launch Development UI
```bash
streamlit run app.py
```
Provides visual inspection across Original, Processed, Quality, and JSON tabs.

---

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 0 | Project Foundation & Stubs | Completed |
| 1 | Image Loading + Decodability Validation | **Completed** |
| 2 | OpenCV Preprocessing & Coordinate Transforms | **Completed** |
| 3 | Image Quality Assessment & Calibration | **Completed** |
| 4 | Model Integration (`BaseDetector` Subclass) | Ready for Batch 2 |
| 5 | Bounding-Box Localization & Restoring Coordinates | Batch 2 |
| 6 | Heatmap Generation (Grad-CAM) | Batch 2 |
| 7 | Lung & Lesion Segmentation | Batch 3 |
| 8 | Confidence & Multi-Evidence Integration | Batch 3 |
| 9 | Structured Clinical JSON Schema Delivery | Batch 3 |
| 10 | Backend / Database Integration | Final Integration |
