# MediSight AI  Frontend & Integration
## Multimodal Medical Image Intelligence (Hospital Web Application)

A modern, responsive, clinical decision-support web application for **MediSight AI**, designed to assist healthcare professionals in analyzing diagnostic medical images alongside patient clinical history.

> **Project Scope & Attribution Notice:**
> This README documents **strictly the Frontend Development and Client-Side Workflow Integration** for the MediSight AI project. Backend APIs, database infrastructure, user authentication services, and live machine learning model deployments are separate system components currently mocked or planned for subsequent integration phases.

---

##  Role & Contribution: Frontend + Integration

As the **Frontend & Integration Developer** on this project, my core contributions encompass:
- **Clinical User Experience Architecture:** Designing and implementing four cohesive medical web portals (Landing Page, Doctor Dashboard, Specialist Imaging Portal, and Patient Dashboard).
- **Interactive Medical Workflows:** Building end-to-end user journeys connecting doctor consultations, specialist image uploads, assistive AI analysis previews, and patient record access.
- **Client-Side State Synchronization:** Architecting a zero-dependency, browser-native state bridge using `localStorage` and URL query parameters to synchronize patient case updates, investigation statuses, and physician sign-offs across separate dashboard interfaces.
- **Hospital Design System:** Establishing a consistent, accessible clinical design system with customized CSS variables, medical color palettes, typography, responsive breakpoints, and mobile navigation drawers.
- **TypeScript & Native JavaScript Implementation:** Authoring both browser-executable vanilla JavaScript runtime files and strongly typed TypeScript source interfaces for clinical data models.

---

##  Implemented Frontend Modules

The frontend is divided into four primary modules:

### 1. Landing Page (`index.html`)
The public-facing portal for hospital information and clinical triage:
- **Hospital Navbar:** MediSight AI branding, navigation links (*How It Works*, *AI Imaging*, *Patient Records*, *Security*), and quick-access portal buttons.
- **Hero Radiology Console HUD:** Interactive medical imaging console featuring a digital chest radiograph (PA view) with a toggleable Region of Interest (ROI) bounding box and telemetry strip.
- **Four-Step Clinical Pipeline:** Visual progression showing *Patient Consultation &rarr; Medical Imaging &rarr; AI Medical Image Intelligence &rarr; Doctor Verification*.
- **Feature Cards:** Highlights multimodal evidence, explainable findings, secure records, and radiology tooling.
- **Explainability Workflow:** Clear pipeline mapping scan intake to highlighted regions, probabilistic findings, confidence indicators, and physician review.
- **Trust & Safety Principles:** Explicit disclaimers highlighting that AI is an assistive decision-support tool, not a diagnostic replacement for doctors.
- **Accessible Authentication Modals:** Interactive modal dialogs for Doctor Login, Patient Login, and Registration, complete with simulated redirection to the respective dashboards.

---

### 2. Doctor Dashboard (`doctor-dashboard.html`)
The primary clinical workspace for attending physicians:
- **Doctor Team Directory:** Pre-configured profiles and credentials for hospital team physicians (**Dr. Joison**, **Dr. Melvin**, **Dr. Joseph**, and **Dr. Ilakkiya**).
- **Patients Directory:** Dynamic patient roster (MR001 Arun Kumar, MR002 Priya Devi, MR003 Rahul S) displaying MR numbers, demographic data, symptoms, and an action column.
- **Patient Details Modal:** Interactive slide-over modal displaying presenting complaints, vitals, preliminary examination notes, and a **"Refer to Specialist"** button that seamlessly transfers the case to the imaging portal.
- **Patient Status Board:** Real-time tracking of patient investigations (*Pending* vs. *Completed* status badges), with instant *"View Report"* actions for finalized cases.
- **Clinical Report & Sign-Off Workspace:**
  - Case lookup by MR Number.
  - Displays patient demographics, investigation type, and AI preliminary findings.
  - Probabilistic confidence estimates separated from supporting multimodal clinical evidence.
  - Clinical editor for attending doctor conclusions, prescription medications, and follow-up advice.
  - **"Approve & Send to Patient"** workflow that updates local storage and marks the report ready for the patient portal.

---

### 3. Specialist Imaging Portal (`specialist-imaging.html`)
The diagnostic intake portal for radiology specialists:
- **Patient Case Intake Card:** Displays patient demographics, reported symptoms, assigned specialist, and clinical notes with a quick patient switcher (MR001, MR002, MR003).
- **Modality Selection:** Selection interface supporting *X-Ray*, *CT Scan*, and *MRI* modalities.
- **Diagnostic Dropzone Interface:** Accessible drag-and-drop zone and file picker supporting DICOM (.dcm), JPG, PNG, and TIFF formats.
- **One-Click Sample Loader:** Button to instantly load a sample digital chest radiograph for fast demonstration.
- **Scan Preview HUD:** Image inspection box with animated scanning line and DICOM readiness indicator.
- **Simulated AI Processing Pipeline:** Visual multi-stage progress tracking (radiomic calibration, dense segmentation, confidence calculation).
- **AI Analysis Results Card:** Displays generated findings, modality details, PACS status, and confidence levels.
- **Printable Analysis Report Modal:** Medical report sheet with hospital letterhead, demographics, AI findings, and browser print/save trigger.
- **Navigation Shortcuts:** Direct links to transition back to the Doctor Workspace reports.

---

### 4. Patient Dashboard (`patient-dashboard.html`)
A minimal, realistic hospital patient portal with strictly four sections:
- **1. Book an Appointment:** Clinical booking form collecting Patient Name, MR No., Age, Gender, Contact Number, Preferred Date, Preferred Time, Department/Specialist, Reason for Visit, and Clinical Notes, featuring an instant booking confirmation card.
- **2. Records:** Clean medical history row displaying Last Date of Visit, Patient Name, and a clickable **Previous Diagnosis** link that immediately routes to the Reports section.
- **3. Reports:** Formal clinical report sheet displaying patient demographics and investigation details. Initially displays a clear *"Awaiting Physician Review"* notice without diagnosis; once finalized by the physician, it updates to display doctor comments, diagnosis, prescribed medications, and clinical recommendations.
- **4. About Us:** Hospital History, Contact Information (24/7 emergency helpline, outpatient desk, address, email), Terms & Conditions, and Basic Hospital Information (accreditations & facilities).

---

##  End-to-End Demo Workflow (How to Reproduce)

You can reproduce the complete clinical workflow in a browser without any backend setup:

```
[Landing Page] (index.html)

       Doctor Login  [Doctor Dashboard] (doctor-dashboard.html)

                                 1. View Patient Details (MR001 Arun Kumar)

                                 2. Click "Refer to Specialist"


                                [Specialist Imaging Portal] (specialist-imaging.html)

                                              3. Click "Load Sample Chest Radiography"
                                              4. Click "Submit for AI Analysis"
                                              5. Review AI Findings & Click "Doctor Reports & Sign-off"


                                [Doctor Dashboard Reports] (doctor-dashboard.html#reports)

                                              6. Review AI preliminary observations
                                              7. Edit doctor conclusion & prescriptions
                                              8. Click "Approve & Send to Patient"


       Patient Login  [Patient Dashboard] (patient-dashboard.html)

                                  9. Book an Appointment (Fill form & submit)
                                  10. Click "Records" & click "Previous Diagnosis"
                                  11. View finalized report with Doctor Diagnosis & Meds
```

---

##  UI Design System & Responsiveness

- **Clean Hospital Aesthetic:** Built with a clean white/light medical background, high-contrast typography, and hospital blue (`#0284c7`) and teal (`#0d9488`) accents.
- **Design Tokens (`variables.css`):** Centralized CSS custom properties for colors, elevation shadows, border radii, and transitions.
- **Responsive Layouts:** Grid and Flexbox layouts optimized for desktop workstations, clinical tablets, and mobile smartphones.
- **Mobile Navigation:** Sliding drawer navigation bars for smaller screens across all four portals.
- **Accessibility:** Uses semantic HTML5, keyboard navigation (`Enter`/`Space` handlers on dropzones), `aria-*` attributes, and high-visibility status tags.

---

##  Technologies Actually Used

| Technology | Purpose in Project |
| :--- | :--- |
| **HTML5** | Semantic markup across all 4 portal pages and interactive modal structures |
| **CSS3** | Custom design system (`variables.css`, `styles.css`, `components.css`, dashboard-specific stylesheets), CSS Grid, Flexbox, media queries |
| **JavaScript (ES6+)** | Browser-executable runtime files (`main.js`, `doctor-dashboard.js`, `specialist-imaging.js`, `patient-dashboard.js`, `modal.js`, `data.js`) |
| **TypeScript** | Strongly typed interfaces and classes (`doctor-types.ts`, `doctor-dashboard.ts`, `specialist-imaging.ts`, `patient-types.ts`, `patient-dashboard.ts`, `tsconfig.json`) |
| **Python (`serve.py`)** | Lightweight development HTTP server script for local testing |
| **Local Storage API** | Browser-native client-side state bridge synchronizing data across interfaces |

---

##  Frontend Project Structure

```text
The-Unscripted/
 index.html                     # MediSight AI Landing Page
 doctor-dashboard.html          # Doctor Clinical Workspace
 specialist-imaging.html        # Specialist Diagnostic Intake & AI Analysis Portal
 patient-dashboard.html         # Minimal 4-Section Patient Portal
 serve.py                       # Lightweight local Python development server
 package.json                   # NPM metadata & TypeScript build scripts
 tsconfig.json                  # TypeScript compiler configuration (strict mode)

 assets/
    images/
        chest_xray.jpg         # Sample chest radiograph scan (PA view)
        doctor_consultation.jpg# Clinical team consultation visual

 css/
    variables.css              # Design tokens, color palette, spacing, typography
    styles.css                 # Base resets, typography, global layout grids
    components.css             # Navigation, buttons, badges, modals, HUD console
    doctor-dashboard.css       # Doctor & Specialist tables, slide-overs, report cards
    patient-dashboard.css      # Patient booking form, records table, report sheet

 js/                            # Browser runtime JavaScript files
    main.js                    # Landing page interactions & modal redirection
    doctor-dashboard.js        # Doctor dashboard state, patient reviews & reports
    specialist-imaging.js      # Image dropzone, modality intake & analysis workflow
    patient-dashboard.js       # Minimal 4-tab patient portal logic & storage sync
    data.js                    # Mock patient dataset
    modal.js                   # Accessible modal window manager
    app.js                     # Landing page HUD telemetry scripts

 ts/                            # TypeScript source files
    doctor-types.ts            # Type definitions for patients, reports & doctors
    doctor-dashboard.ts        # Typed Doctor Dashboard manager
    specialist-imaging.ts      # Typed Specialist Imaging manager
    patient-types.ts           # Type definitions for patient portal & appointments
    patient-dashboard.ts       # Typed Patient Dashboard manager
    types.ts                   # Landing page type definitions
    data.ts                    # Strongly-typed clinical demo data
    modal.ts                   # Strongly-typed modal manager
    app.ts                     # Strongly-typed HUD controller
    main.ts                    # Strongly-typed application entry point

 README.md                      # Frontend & Integration Documentation
```

---

##  How to Install and Run the Frontend

The frontend is completely zero-dependency and does not require Node.js or a build step to preview.

### Option 1: Open Directly in Any Web Browser (No Server Needed)
Simply open any of the HTML files directly in your web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Apple Safari):
- Double-click [`index.html`](index.html) to start from the Landing Page.
- Double-click [`doctor-dashboard.html`](doctor-dashboard.html) to enter the Doctor Workspace directly.
- Double-click [`specialist-imaging.html`](specialist-imaging.html) to enter the Specialist Imaging Portal.
- Double-click [`patient-dashboard.html`](patient-dashboard.html) to enter the Patient Portal.

### Option 2: Run Using Local Python Server
If you prefer running through a local web server (recommended for testing clean URLs):
```bash
python serve.py
# or
py serve.py
```
Then open your browser at:
 **`http://localhost:8000`**

---

##  Backend, Database & AI Model Status (Future Work)

The current implementation focuses on client-side interface architecture, clinical user flows, and state coordination. The following areas represent planned future integrations:
- **Backend API Integration:** Connecting REST endpoints to a live backend service for persistent server-side storage and session management.
- **Database & Cloud Storage:** Replacing browser `localStorage` with a persistent relational database (e.g., PostgreSQL / Supabase) and authenticated DICOM cloud storage.
- **Authentication:** Implementing secure, role-based authentication (OAuth2 / JWT) for doctor, specialist, and patient roles.
