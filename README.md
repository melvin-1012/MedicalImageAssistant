# medical_cv — Medical Computer Vision Engine (HNX26PSI05)

Standalone prototype for the image-processing half of *Multimodal Medical
Image Intelligence*. No frontend, auth, database, LLM or reporting.

## Run

```bash
pip install -r requirements.txt
python main.py
pytest
streamlit run app.py   # minimal UI
```

## Pipeline

```
Image -> Loader -> Validator -> Quality -> Preprocessing
      -> Detector -> Localization -> Heatmap / Segmentation
      -> Visualization -> CVAnalysisResult (JSON)
```

## Three separated concerns

| Concern | Modules | Replaceable? |
|---|---|---|
| 1. Image processing | `image_loader`, `validator`, `preprocessing`, `quality` | OpenCV only, no model dependency |
| 2. Model inference | `detector` (`BaseDetector`) | Swap in any model by subclassing |
| 3. Visual explainability | `localization`, `heatmap`, `segmentation`, `visualization`, `coordinates` | Consumes detections + original image |

The pipeline talks to the detector only through `BaseDetector`, so replacing
the AI model never touches the OpenCV code.

## Key rules

- The original image is never modified; preprocessing returns a copy plus a
  `ResizeTransform` so boxes map back to original coordinates.
- No fake detections, heatmaps or masks. With no model, the detector is
  `NullDetector` (`is_loaded == False`).
- All paths and thresholds live in `config.py`.

## Phases

| Phase | Scope | Status |
|---|---|---|
| 0 | Project foundation | done |
| 1 | Image loading + validation | next |
| 2 | OpenCV preprocessing | |
| 3 | Image quality assessment | |
| 4 | Model integration | |
| 5 | Bounding-box localization | |
| 6 | Heatmap / Grad-CAM | |
| 7 | Segmentation | |
| 8 | Confidence + evidence | |
| 9 | Structured JSON output | |
| 10 | Backend/API integration | |
