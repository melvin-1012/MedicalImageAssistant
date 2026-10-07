# GenAI Module — Multimodal Medical Image Intelligence

**HNX26 · Person 4 (GenAI) · Branch: `Multimodal-AI`**

> This module is the AI reasoning layer of the Multimodal Medical Image Intelligence system. It takes structured vision model output (bounding boxes, confidence scores) and unstructured patient clinical notes, and returns a fully validated, evidence-grounded clinical explanation in JSON format — ready for the backend to serve to the frontend.

---

## What This Module Does

The GenAI module sits between the **Computer Vision model** (Person 3) and the **Backend API** (Person 2). It performs three critical jobs:

1. **Notes Processing** — Extracts structured symptoms and medical history from raw, unstructured patient clinical notes using an LLM.
2. **Evidence-Grounded Explanation** — Generates a cautious, physician-facing explanation that links the CV model's findings to the patient's clinical context. The AI never diagnoses — it only correlates evidence.
3. **Safety Validation** — Validates the LLM output against strict Pydantic schemas to ensure:
   - Confidence scores are never altered by the LLM
   - Bounding box coordinates are preserved exactly
   - Every output explicitly requires physician review
   - Image quality failures cannot be overridden

### What It Does NOT Do
- It does not generate bounding boxes or confidence scores (those come from the CV model)
- It does not confirm a diagnosis
- It does not allow the LLM to hallucinate findings

---

## System Architecture

```
Frontend (Person 1)
        ↓  (HTTP request)
Backend API (Person 2)
        ↓  (calls CV model + GenAI module)
┌───────────────────────────────────────────┐
│              GenAI Module                 │
│                                           │
│  1. NotesProcessor                        │
│     └─ Extracts symptoms from raw notes   │
│                                           │
│  2. ExplanationGenerator                  │
│     └─ Links CV findings to patient notes │
│                                           │
│  3. EvidenceValidator                     │
│     └─ Validates output safety            │
│                                           │
│  4. GenAIPipeline (orchestrates all 3)    │
└───────────────────────────────────────────┘
        ↓  (returns structured JSON)
Backend API (Person 2)
        ↓  (sends to Frontend)
Frontend (Person 1)
```

---

## Technologies, Libraries, and Models

| Component | Technology |
|-----------|-----------|
| **LLM Provider** | [Groq Cloud](https://console.groq.com/) |
| **LLM Model** | `openai/gpt-oss-120b` (via Groq) |
| **Structured Output** | [`instructor`](https://github.com/jxnl/instructor) — enforces strict Pydantic JSON schema from the LLM |
| **Schema Validation** | [`pydantic`](https://docs.pydantic.dev/) v2 |
| **API Framework** | [`fastapi`](https://fastapi.tiangolo.com/) + [`uvicorn`](https://www.uvicorn.org/) |
| **Retry Logic** | [`tenacity`](https://tenacity.readthedocs.io/) — exponential backoff on API failures |
| **Environment Config** | [`python-dotenv`](https://pypi.org/project/python-dotenv/) |
| **Testing** | `pytest` + custom mock pipeline |

---

## Project Structure

```
genai_module/
├── pipeline.py              # Main orchestrator — runs the full GenAI pipeline
├── notes_processor.py       # Extracts structured symptoms from raw clinical notes
├── explanation_generator.py # Generates evidence-grounded clinical explanations
├── evidence_validator.py    # Validates LLM output safety and schema compliance
├── ai_response_schema.py    # All Pydantic input/output schemas (data contracts)
├── api_router.py            # FastAPI router — plug into Person 2's backend
├── app.py                   # Standalone FastAPI app for local Swagger UI testing
├── mock_data.py             # Standardized mock test scenarios
├── test_cases.py            # End-to-end pipeline tests (4 scenarios)
├── requirements.txt         # Python dependencies
├── .env.example             # Template for environment variables
└── README.md                # This file
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- A free [Groq Cloud](https://console.groq.com/) API key

### Step 1: Clone and switch to the correct branch

```bash
git clone https://github.com/melvin-1012/MedicalImageAssistant.git
cd MedicalImageAssistant
git checkout Multimodal-AI
```

### Step 2: Install dependencies

```bash
pip install -r genai_module/requirements.txt
```

### Step 3: Configure your API key

Create a `.env` file inside the `genai_module/` folder:

```bash
# genai_module/.env
GROQ_API_KEY="your-groq-api-key-here"
```

> Get a free API key at [https://console.groq.com/](https://console.groq.com/)

---

## Running the System

### Option A: Run the Test Suite (Recommended First Step)

This verifies the full pipeline end-to-end against 4 test scenarios:

```bash
python -m genai_module.test_cases
```

**Expected output:** 4 JSON responses printed to the terminal:
- **Test 1** — Standard successful run (X-ray with findings + clinical notes)
- **Test 2** — Poor quality image (fast-fail, no LLM called)
- **Test 3** — Normal image with no findings (empty findings array)
- **Test 4** — Multiple findings with no clinical notes

### Option B: Run the Standalone API (Swagger UI)

```bash
uvicorn genai_module.app:app --reload
```

Then open your browser at [http://localhost:8000/docs](http://localhost:8000/docs) to interact with the live API using the Swagger interface.

### Option C: Integrate into Person 2's Backend

In Person 2's main FastAPI file (e.g. `main.py`), add two lines:

```python
from genai_module.api_router import router as genai_router

app.include_router(genai_router)
```

This exposes a live endpoint at `POST /genai/analyze`.

---

## API Reference

### `POST /genai/analyze`

**Request Body:**
```json
{
  "vision_data": {
    "status": "success",
    "modality": "X-Ray",
    "findings": [
      {
        "finding": "possible_abnormal_opacity",
        "confidence": 0.82,
        "location": { "x1": 320, "y1": 240, "x2": 610, "y2": 520 },
        "heatmap_available": true,
        "requires_physician_review": true
      }
    ]
  },
  "raw_notes": "Patient presents with a 2-week persistent cough and mild fever."
}
```

**Response:**
```json
{
  "summary": "Imaging finding requires physician review and clinical correlation.",
  "findings": [
    {
      "finding": "possible_abnormal_opacity",
      "location": { "x1": 320.0, "y1": 240.0, "x2": 610.0, "y2": 520.0 },
      "confidence": 0.82,
      "supporting_notes": [],
      "explanation": "The chest X-ray demonstrates a possible abnormal opacity...",
      "uncertainty": [],
      "status": "review_required"
    }
  ],
  "limitations": ["AI-generated analysis is not a confirmed diagnosis."],
  "validation_status": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  }
}
```

---

## Reproducing the Demonstrated Results

### Run all 4 test cases

```bash
python -m genai_module.test_cases
```

You should see 4 passing `is_valid: true` JSON responses. The key things to verify:

| Test | What to verify |
|------|---------------|
| Test 1 | `confidence: 0.82` is preserved exactly, `status: "review_required"` present |
| Test 2 | `is_valid: true`, `findings: []`, no LLM called |
| Test 3 | `findings: []` when CV model reports no detections |
| Test 4 | Two separate findings with independent bounding boxes and confidence scores |

---

## Medical Safety Guarantees

This module enforces the following safety rules at the **code level** (not just the prompt):

- ✅ Confidence scores from the CV model are **never altered** by the LLM
- ✅ Bounding box coordinates are **preserved exactly** as received
- ✅ Every finding **always** includes `"requires_physician_review": true`  
- ✅ Poor quality images are **rejected before** the LLM is ever called
- ✅ The LLM **cannot** add new findings not present in the CV output
- ✅ All outputs are validated against strict Pydantic schemas before being returned

---

## Team Integration

| Person | Role | Depends On |
|--------|------|-----------|
| Person 1 | Frontend UI | Person 2's API response |
| Person 2 | Backend API | GenAI Module (`api_router.py`) + CV Module |
| Person 3 | Computer Vision | Provides `vision_data` JSON to Person 2 |
| **Person 4 (this module)** | **GenAI Module** | Receives from Person 2, returns enriched JSON |
