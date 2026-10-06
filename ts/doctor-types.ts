/**
 * MediSight AI - Doctor Dashboard Type Definitions
 * TypeScript interfaces and types for the clinical decision-support doctor dashboard.
 */

export type PatientGender = 'Male' | 'Female' | 'Other';
export type PatientInvestigationStatus = 'Pending' | 'Completed';
export type DashboardTab = 'patients' | 'patient-status' | 'reports' | 'profile';

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
  readonly investigationType: string;
  aiPreliminaryReportStatus: string;
  doctorReviewStatus: string;
  finalReportStatus: string;
  readonly aiFindings: string;
  readonly confidence: string;
  readonly evidenceExplanation: string;
  doctorConclusion: string;
  medications: string;
  isApproved: boolean;
  approvalTimestamp?: string;
}

/** Doctor profile information model */
export interface DoctorProfile {
  readonly name: string;
  readonly title: string;
  readonly licenseNo: string;
  readonly department: string;
  readonly hospital: string;
  readonly email: string;
  readonly phone: string;
  readonly experienceYears: number;
  readonly specialization: string;
  readonly consultationHours: string;
  readonly verifiedStatus: boolean;
}

/** Toast feedback alert model */
export interface ToastNotification {
  readonly id: string;
  readonly type: 'success' | 'info' | 'warning';
  readonly title: string;
  readonly message: string;
}
