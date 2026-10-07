# Multimodal Medical Image Intelligence System

**HNX26 · Team: The Unscripted · Hackathon: Hacknex 2026**

> An end-to-end AI-powered clinical decision support system that analyzes chest X-rays, detects suspected abnormalities, classifies pathologies, and generates evidence-grounded explanations for physicians — combining Computer Vision and Large Language Models in a single unified pipeline.

---

## What This Project Does

This system assists radiologists and physicians by automatically processing chest X-ray images alongside patient clinical notes and returning a structured, physician-readable analysis. It is **not a diagnostic tool** — it is a decision support system that flags findings for human review.

### Full System Pipeline

```
Doctor uploads X-ray + Patient Notes
              ↓
     Backend API (Person 2)
         ↙           ↘
 CV Module          GenAI Module
 (Person 3)         (Person 4)
   YOLO               DenseNet-121
   detects            classifies
   bounding           pathology
   boxes              probabilities
         ↘           ↙
     Backend combines results
              ↓
     Frontend displays to Doctor
     (Person 1)
```

### What Each AI Model Does

| Model | Type | Output |
|-------|------|--------|
| **YOLO** | Object Detection | Bounding boxes showing *where* the abnormality is |
| **DenseNet-121** (TorchXRayVision) | Image Classification | Probabilities for 18 chest pathologies |
| **LLaMA 3 / GPT-OSS-120B** (via Groq) | Language Model | Evidence-grounded explanation linking findings to patient notes |

---

## Repository Branch Structure

| Branch | Owner | Description |
|--------|-------|-------------|
| `main` | All | Merged, stable code |
| `Multimodal-AI` | Person 4 | GenAI reasoning module (this branch) |
| `Computer-Vision-V1` | Person 3 | YOLO + DenseNet-121 CV pipeline |
| `ilakkiya-frontend` | Person 1 | React/Next.js frontend UI |
| `Database` | Person 2 | Backend API + database integration |

---

## Technologies Used

### GenAI Module (`Multimodal-AI` branch)
| Component | Technology |
|-----------|-----------|
| LLM Provider | [Groq Cloud](https://console.groq.com/) |
| LLM Model | `openai/gpt-oss-120b` |
| Structured Output | `instructor` + `pydantic` v2 |
| API Framework | `fastapi` + `uvicorn` |
| Retry Logic | `tenacity` |

### Computer Vision Module (`Computer-Vision-V1` branch)
| Component | Technology |
|-----------|-----------|
| Object Detection | YOLO (Ultralytics) |
| Classification | DenseNet-121 via [TorchXRayVision](https://github.com/mlmed/torchxrayvision) |
| Image Processing | OpenCV, NumPy |
| UI | Streamlit |
| Deep Learning | PyTorch, TorchVision |

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/melvin-1012/MedicalImageAssistant.git
cd MedicalImageAssistant
```

### 2. Run the GenAI Module (Multimodal-AI branch)

```bash
git checkout Multimodal-AI
pip install -r genai_module/requirements.txt
```

Create `genai_module/.env`:
```
GROQ_API_KEY="your-groq-api-key-here"
```

Run the full test suite:
```bash
python -m genai_module.test_cases
```

> See [`genai_module/README.md`](genai_module/README.md) for the complete GenAI module documentation.

### 3. Run the Computer Vision Module (Computer-Vision-V1 branch)

```bash
git checkout Computer-Vision-V1
pip install -r requirements.txt
pip install torch torchvision torchxrayvision
```

Run inference on a single X-ray:
```bash
python main.py test_xray.png
```

Launch the visual web interface:
```bash
python -m streamlit run app.py
```

---

## How to Reproduce the Demonstrated Results

### GenAI Pipeline (all 4 test scenarios)

```bash
git checkout Multimodal-AI
python -m genai_module.test_cases
```

**Expected:** 4 structured JSON responses, all with `"is_valid": true`.

### Computer Vision Pipeline

```bash
git checkout Computer-Vision-V1
python test_classifier.py
```

**Expected:** A ranked JSON dictionary of 18 chest pathology probabilities from DenseNet-121.

```bash
python main.py test_xray.png
```

**Expected:** Full analysis summary including quality assessment, YOLO detections, and DenseNet classification probabilities.

---

## Medical Safety Principles

This system is designed from the ground up with the following safety guarantees:

- ✅ **No hallucination** — The LLM cannot add findings not detected by the CV model
- ✅ **Confidence scores preserved** — The AI never alters the numeric confidence from the vision model
- ✅ **Physician review required** — Every output explicitly requires human review
- ✅ **Quality gate** — Poor quality images are rejected before any AI model is called
- ✅ **Schema validation** — All outputs are validated against strict Pydantic schemas

> This tool is intended to assist physicians, not replace them.

---

## Team

| Person | Role |
|--------|------|
| Person 1 | Frontend (React UI) |
| Person 2 | Backend API + Database |
| Person 3 | Computer Vision (YOLO + DenseNet) |
| Person 4 | GenAI Reasoning Module |
