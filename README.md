# MediSight AI — Multimodal Medical Image Intelligence

An AI-assisted clinical decision-support system designed to help doctors analyze medical images together with patient clinical information.

> **Clinical Principle:** Built to support doctors, not replace them. AI is a clinical decision-support tool, not a replacement for medical professionals.

---

## 🏥 Landing Page Architecture

The landing page provides a clean, hospital-grade user experience with zero external build dependencies:

```
The-Unscripted/
├── index.html              # Core landing page (semantic, accessible HTML5)
├── css/
│   ├── variables.css       # Clinical color palette, typography & design tokens
│   ├── styles.css          # Layout grids, hero styling, responsive breakpoints
│   └── components.css      # Navbar, medical HUD, feature cards, modals, footer
├── js/
│   ├── main.js             # Standalone application script & accessible modal handlers
│   ├── data.js             # Clinical demo data model
│   ├── modal.js            # Reusable modal manager
│   └── app.js              # Modular ES6 entry point
├── assets/
│   └── images/
│       ├── chest_xray.jpg  # Clinical chest radiograph (PA view)
│       └── doctor_consultation.jpg # Clinical team consultation visual
├── serve.py                # Lightweight development server (Python)
└── README.md               # Documentation and future roadmap
```

---

## 🚀 How to Run and Preview

### Option 1: Open Directly in Browser (No Server Needed)
Double-click [index.html](file:///c:/Users/ilakk/Documents/The-Unscripted/index.html) or open it directly in Google Chrome, Microsoft Edge, Firefox, or Safari. All styles, SVG icons, and interactive elements run standalone.

### Option 2: Run Local Python Web Server
```bash
py serve.py
# or
python serve.py
```
Then navigate to: **[http://localhost:8000](http://localhost:8000)**

---

## 🩺 Landing Page Features Included

1. **Header / Navbar:**
   - MediSight AI clinical branding mark & logo
   - Quick navigation links: *How It Works*, *AI Imaging*, *Patient Records*, *Security*
   - Access portal buttons: *Patient Login*, *Doctor Login*, *Register*
   - Accessible mobile drawer navigation

2. **Hero Section:**
   - Heading: *“AI-Assisted Medical Intelligence”*
   - Tagline: *“Helping doctors see more, with AI-powered medical image intelligence.”*
   - Supporting text: *“An explainable second-opinion assistant that combines medical images, clinical notes, and test information to support better-informed clinical decisions.”*
   - Core badge: *“Built to support doctors, not replace them.”*
   - Interactive Radiology Console HUD featuring chest X-ray PA view with toggleable ROI bounding box and telemetry.

3. **How It Works (4 Clinical Steps):**
   - **Step 01:** Patient Consultation
   - **Step 02:** Medical Imaging
   - **Step 03:** AI Medical Image Intelligence
   - **Step 04:** Doctor Verification

4. **Features (Hospital-Grade Feature Cards):**
   - AI Medical Imaging
   - Multimodal Evidence
   - Explainable Findings
   - Patient Records
   - Secure Medical Data

5. **AI Explainability Workflow:**
   - Transparent step-by-step pipeline:  
     `X-Ray Image → Highlighted Region → AI Finding → Confidence → Supporting Evidence → Doctor Review`
   - Clinical Case Demonstration:
     - Finding: *“Possible abnormal opacity”*
     - Location: *“Right upper lung region”*
     - Confidence: *“Confidence: 87%”*
     - Action: *“Requires physician review”*
   - Multimodal correlation (Clinical notes + Laboratory CRP/WBC markers)
   - Prominent clinical advisory banner stating that AI does not definitively diagnose diseases.

6. **Trust / Safety:**
   - Statement: *“AI is a clinical decision-support tool, not a replacement for medical professionals.”*
   - 5 core pillars: *Explainable AI*, *Doctor verification*, *Evidence-based findings*, *Uncertainty-aware results*, and *Secure medical records*.

7. **Accessible Demo Modals:**
   - Interactive preview dialogs for *Doctor Login*, *Patient Login*, and *Hospital Registration*.

8. **Footer:**
   - MediSight AI branding, mission statement, system navigation links, hospital contact information, and medical device disclaimer.

---

## 🔮 Future Phases (Ready for Component Integration)
The codebase has been designed with clean component boundaries so subsequent modules can be added easily:
- **Doctor Dashboard:** PACS image viewer, case queue, differential diagnosis tools, and physician reporting sign-off.
- **Patient Dashboard:** Diagnostic summaries, historical visit timeline, and doctor recommendations.
- **Specialist Upload Workflow:** DICOM/image ingestion, metadata tagging, and clinical note attachments.
- **Reports Module:** Printable and exportable PDF clinical consultation reports with audit timestamps.
