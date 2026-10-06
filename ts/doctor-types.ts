/**
 * MediSight AI - Doctor Dashboard & Specialist Imaging Type Definitions
 * TypeScript interfaces and types for the clinical decision-support doctor dashboard and specialist workflow.
 */

export type PatientGender = 'Male' | 'Female' | 'Other';
export type PatientInvestigationStatus = 'Pending' | 'Completed';
export type DashboardTab = 'patients' | 'patient-status' | 'reports' | 'profile';
export type ImagingModality = 'XRay' | 'CT Scan' | 'MRI';

/** Basic patient summary record for the patient directory table */
export interface PatientRecord {
  readonly mrNo: string;
  readonly name: string;
  readonly age: number;
  readonly gender: PatientGender;
  readonly symptoms: string;
  readonly clinicalNotes: string;
  readonly investigationStatus: string;
  readonly assignedSpecialist: string;
  readonly aiAnalysisStatus: string;
  status: PatientInvestigationStatus;
}

/** Full clinical report model for investigation reviews */
export interface ClinicalReport {
  readonly mrNo: string;
  readonly patientName: string;
  readonly age: number;
  readonly gender: PatientGender;
  investigationType: string;
  modality?: ImagingModality;
  aiPreliminaryReportStatus: string;
  doctorReviewStatus: string;
  finalReportStatus: string;
  readonly aiFindings: string;
  readonly confidence: string;
  readonly evidenceExplanation: string;
  doctorConclusion: string;
  medications: string;
  recommendations?: string;
  additionalNotes?: string;
  reviewedBy?: string;
  isApproved: boolean;
  isFinalSent?: boolean;
  approvalTimestamp?: string;
}

/** Team Doctor profile information model */
export interface TeamDoctorProfile {
  readonly id: string;
  readonly name: string;
  readonly credentials: string;
  readonly role: string;
  readonly department: string;
  readonly specialization: string;
  readonly licenseNo: string;
  readonly experienceYears: number;
  readonly avatarText: string;
  readonly email: string;
}

/** Toast feedback alert model */
export interface ToastNotification {
  readonly id: string;
  readonly type: 'success' | 'info' | 'warning';
  readonly title: string;
  readonly message: string;
}
