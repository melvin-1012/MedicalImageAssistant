# MediSight AI - Clinical Decision Support System

MediSight AI is a comprehensive, full-stack medical imaging and clinical decision support system. It provides an end-to-end workflow for hospitals, allowing doctors to request imaging studies, specialists to upload X-rays/CTs/MRIs, and advanced AI pipelines to automatically analyze those images. 

The AI does not replace the doctor; instead, it acts as a "second pair of eyes," providing high-confidence findings, bounding-box localizations, and multimodal clinical explanations. The attending physician then reviews the AI's findings alongside the patient's medical history to submit a final clinical assessment and generate a secure PDF report.

---

## 🛠️ Technologies, Libraries, and Models Used

### Frontend (UI/UX)
* **HTML5 / CSS3 / Vanilla JavaScript**: A lightweight, dependency-free frontend ensuring lightning-fast load times.
* **Responsive CSS Grid/Flexbox**: Mobile-friendly clinical dashboards.

### Backend (API & Orchestration)
* **Python 3.10+**: Core programming language.
* **FastAPI**: High-performance asynchronous web framework for building the RESTful API.
* **Pydantic (v2)**: Robust data validation and schema definitions.
* **Pytest**: Comprehensive automated test suite (47+ tests ensuring pipeline integrity).

### Database, Authentication & Storage
* **Supabase**: Managed backend-as-a-service.
* **PostgreSQL**: Relational database with 11 normalized tables.
* **Supabase Auth**: Secure JWT-based authentication preventing plaintext password storage.
* **Row Level Security (RLS)**: Strict database-level security ensuring patients only see their own records, and specialists cannot alter doctor assessments.
* **Supabase Storage**: Secure, private buckets for medical images and PDF reports, accessed via time-limited signed URLs.

### AI & Machine Learning Pipelines
* **Vision AI (Computer Vision)**: Uses `numpy`, `opencv-python`, and `pydicom` to process medical imagery. Identifies focal opacities, generates confidence scores, and creates heatmaps (bounding boxes). *Fallback mock models are included for testing without heavy weights.*
* **Multimodal GenAI**: Integrated via the **Groq API** using the **LLaMA 3.2 90B Vision** model. It correlates the Vision AI's structural findings with the patient's clinical history (age, symptoms, medical alerts) to generate a grounded clinical explanation and explicit AI limitations.

---

## 📦 How to Install Dependencies

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/MedicalImageAssistant.git
   cd MedicalImageAssistant
   ```

2. **Create a Python Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Backend Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
   *(Ensure you also install the dependencies in `genai_module/requirements.txt` if testing the GenAI pipeline independently).*

---

## ⚙️ How to Configure and Run the System

### 1. Database Setup
Execute the following SQL scripts (located in the `database/` folder) in your Supabase SQL Editor in this exact order:
1. `schema.sql` (Creates the 11 tables and triggers)
2. `rls_policies.sql` (Applies strict Row Level Security)
3. `storage_setup.sql` (Creates private buckets for images and reports)
4. `seed_data.sql` *(Optional: seeds demo patients and doctors)*

### 2. Environment Variables
In the `backend/` directory, copy the example environment file and fill in your keys:
```bash
cp .env.example .env
```
Edit `.env` to include:
* `SUPABASE_URL`: Your Supabase project URL.
* `SUPABASE_KEY`: Your Supabase Anon Key.
* `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase Service Role Key (Required for admin DB overrides).
* `GROQ_API_KEY`: Your Groq API key (for the Multimodal GenAI LLaMA model).

### 3. Run the Backend API
Start the FastAPI server from the `backend/` directory:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
* Interactive API Documentation is available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run the Frontend UI
Open a new terminal, navigate to the repository root, and start a simple HTTP server:
```bash
python serve.py
```
* Access the web portal at: [http://localhost:8080](http://localhost:8080)

---

## 🧪 How to Reproduce the Demonstrated Results

To experience the full end-to-end clinical workflow, follow these steps:

### Step 1: Authentication
1. Navigate to `http://localhost:8080`.
2. Click **Patient Login** or **Hospital Staff Registration** to create a new Patient account. (The system will automatically generate a unique MR Number, e.g., `MR-2024-1234`).
3. To log in as a doctor, you must manually create a user in your Supabase Auth dashboard, assign their `profiles` row the role of `doctor`, and link them in the `doctors` table.

### Step 2: Requesting an Image (Doctor)
1. Log in via the **Doctor Login** modal.
2. In the Doctor Dashboard, locate a patient in the registry and click **Refer to Specialist**.
3. Fill out the symptoms and select the imaging type (e.g., Chest X-Ray).

### Step 3: Uploading the Scan (Specialist)
1. Log in via the **Staff Registration/Login** as a `specialist`.
2. You will see the Doctor's pending imaging request in your queue.
3. Upload a sample medical image (JPEG/PNG/DICOM). 
4. The system securely uploads this to the Supabase `medical-images` bucket and updates the request status.

### Step 4: AI Analysis Pipeline
1. The backend automatically triggers the `imaging_service.py` pipeline.
2. **Vision AI** scans the image, returning a clinical finding (e.g., "Focal alveolar consolidation") and a confidence score.
3. **Multimodal GenAI** securely processes this finding alongside the patient's symptoms to generate a cohesive clinical summary.
4. The combined AI results are saved to the `ai_analysis_results` table.

### Step 5: Doctor Review & PDF Generation
1. Switch back to the **Doctor Dashboard**.
2. Open the patient's pending report. You will see the AI's structural findings and clinical context displayed clearly.
3. Write your final **Human Physician Conclusion** and submit the assessment.
4. The backend merges the patient data, AI findings, and your assessment, generates a secure **PDF Medical Report**, and stores it in the `medical-reports` bucket.
5. The Patient can now log into their portal and securely view/download their finalized PDF report.
