/**
 * MediSight AI - TypeScript Type Definitions
 * Clean and beginner-friendly interfaces for hospital decision support.
 */

/** Metadata regarding the hospital system and core clinical statements */
export interface SystemMetadata {
  readonly name: string;
  readonly subname: string;
  readonly heroHeading: string;
  readonly tagline: string;
  readonly supportingText: string;
  readonly corePrinciple: string;
  readonly clinicalSafetyStatement: string;
}

/** Individual clinical workflow step in the patient journey */
export interface WorkflowStep {
  readonly step: string;
  readonly title: string;
  readonly subtitle: string;
  readonly description: string;
}

/** Feature card highlighting clinical capabilities */
export interface FeatureItem {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly bullets: readonly string[];
}

/** Clinical reference case demonstrating explainable AI findings */
export interface ClinicalSampleCase {
  readonly patientId: string;
  readonly scanType: string;
  readonly finding: string;
  readonly location: string;
  readonly confidence: string;
  readonly status: string;
  readonly clinicalNotes: string;
  readonly laboratoryMarkers: string;
  readonly differentialConsiderations: string;
}

/** Trust & safety pillar */
export interface TrustPillar {
  readonly title: string;
  readonly description: string;
}

/** Interactive explainability pipeline phase description */
export interface PipelinePhase {
  readonly title: string;
  readonly text: string;
  readonly metric: string;
}

/** Complete hospital clinical dataset contract */
export interface HospitalDataset {
  readonly system: SystemMetadata;
  readonly workflowSteps: readonly WorkflowStep[];
  readonly features: readonly FeatureItem[];
  readonly sampleCase: ClinicalSampleCase;
  readonly trustPillars: readonly TrustPillar[];
}

/** Supported modal view identifiers */
export type ModalType = 'doctor-login' | 'patient-login' | 'register';
