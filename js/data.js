/**
 * MediSight AI - Clinical Demo Data Model
 * Demo and reference data for the hospital landing page.
 */

export const hospitalData = {
  system: {
    name: "MediSight AI",
    subname: "Multimodal Medical Image Intelligence",
    heroHeading: "AI-Assisted Medical Intelligence",
    tagline: "Helping doctors see more, with AI-powered medical image intelligence.",
    supportingText: "An explainable second-opinion assistant that combines medical images, clinical notes, and test information to support better-informed clinical decisions.",
    corePrinciple: "Built to support doctors, not replace them.",
    clinicalSafetyStatement: "AI is a clinical decision-support tool, not a replacement for medical professionals."
  },

  workflowSteps: [
    {
      step: "01",
      title: "Patient Consultation",
      subtitle: "Clinical Intake & Context",
      description: "Care teams record patient history, presenting symptoms, vital signs, and EHR documentation during the initial clinical examination."
    },
    {
      step: "02",
      title: "Medical Imaging",
      subtitle: "Diagnostic Acquisition",
      description: "Standard high-resolution scans (Chest X-Ray, CT, MRI) are acquired following hospital protocol and archived directly into PACS."
    },
    {
      step: "03",
      title: "AI Medical Image Intelligence",
      subtitle: "Multimodal Pattern Analysis",
      description: "Our neural model analyzes image features correlated with clinical notes and laboratory metrics to flag subtle patterns with confidence scores."
    },
    {
      step: "04",
      title: "Doctor Verification",
      subtitle: "Independent Clinical Review",
      description: "Attending physicians and radiologists review localized regions, examine multimodal evidence, and determine definitive diagnostic conclusions."
    }
  ],

  features: [
    {
      id: "imaging",
      title: "AI Medical Imaging",
      description: "High-precision computer vision trained on standardized radiology benchmarks to highlight opacities, consolidations, and structural anomalies.",
      bullets: [
        "Digital Radiography (X-Ray) and CT support",
        "Subtle opacity and nodule detection",
        "Consistent PACS DICOM integration"
      ]
    },
    {
      id: "multimodal",
      title: "Multimodal Evidence",
      description: "Analyzes clinical notes, patient symptoms, and laboratory markers alongside imaging pixels for comprehensive diagnostic context.",
      bullets: [
        "Natural language correlation with EHR notes",
        "Integrates vital signs & lab biomarkers",
        "Holistic clinical decision support"
      ]
    },
    {
      id: "explainable",
      title: "Explainable Findings",
      description: "Replaces 'black box' predictions with transparent bounding regions, anatomical coordinates, confidence ratings, and rationale summaries.",
      bullets: [
        "Anatomically localized region of interest",
        "Calibrated confidence score percentages",
        "Differential diagnostic context"
      ]
    },
    {
      id: "records",
      title: "Patient Records",
      description: "Longitudinal patient record tracking that links historical diagnostic imaging with current clinical episodes for trend tracking.",
      bullets: [
        "Side-by-side historical scan comparison",
        "Timeline of clinical interventions",
        "Interoperable with major EHR standards"
      ]
    },
    {
      id: "security",
      title: "Secure Medical Data",
      description: "Enterprise-level data security compliant with HIPAA and international hospital data protection standards.",
      bullets: [
        "End-to-end AES-256 data encryption",
        "Strict role-based access control (RBAC)",
        "Immutable clinical audit logging"
      ]
    }
  ],

  sampleCase: {
    patientId: "MS-89241",
    scanType: "PA Chest Radiograph",
    finding: "Possible abnormal opacity",
    location: "Right upper lung region",
    confidence: "87%",
    status: "Requires physician review",
    clinicalNotes: "Patient presents with persistent cough (5 days), evening pyrexia (38.2°C), and fatigue.",
    laboratoryMarkers: "WBC: 11.4 × 10⁹/L | CRP: 18.2 mg/L (Elevated) | SpO2: 96% on room air",
    differentialConsiderations: "Focal consolidation consistent with early community-acquired pneumonia vs localized atelectasis."
  },

  trustPillars: [
    {
      title: "Explainable AI",
      description: "Transparent visual bounding and contextual evidence eliminate opaque 'black box' predictions."
    },
    {
      title: "Doctor Verification",
      description: "Strict human-in-the-loop clinical workflow ensuring doctors retain complete diagnostic authority."
    },
    {
      title: "Evidence-Based Findings",
      description: "Findings are corroborated by multi-source clinical data, vital statistics, and laboratory markers."
    },
    {
      title: "Uncertainty-Aware Results",
      description: "Calculates calibrated confidence intervals and explicitly surfaces ambiguity when present."
    },
    {
      title: "Secure Medical Records",
      description: "Hospital-grade encryption, HIPAA compliance, and strict multi-factor authentication controls."
    }
  ]
};
