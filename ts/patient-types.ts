/**
 * MediSight AI - Patient Dashboard Type Definitions
 * TypeScript interfaces and types for the hospital patient information portal.
 */

export type PatientPortalTab =
  | 'dashboard'
  | 'profile'
  | 'appointments'
  | 'medical-records'
  | 'investigations'
  | 'reports'
  | 'notifications';

export type AppointmentStatus = 'Upcoming' | 'Completed' | 'Cancelled';

export type InvestigationStatus = 'Requested' | 'In Progress' | 'Completed';

/** Patient Profile model */
export interface PatientProfile {
  readonly mrNo: string;
  name: string;
  age: number;
  gender: string;
  phone: string;
  email: string;
  bloodGroup: string;
  emergencyContact: string;
  address: string;
  primaryDoctor?: string;
  knownAllergies?: string;
}

/** Appointment record model */
export interface PatientAppointment {
  readonly id: string;
  doctor: string;
  department: string;
  date: string;
  time: string;
  status: AppointmentStatus;
  reason: string;
  room?: string;
}

/** Medical consultation & episode record */
export interface PatientMedicalRecord {
  readonly id: string;
  title: string;
  date: string;
  doctor: string;
  department: string;
  diagnosisNotes: string;
  prescriptions: string;
  previousHistory: string;
  isAiAssisted?: boolean;
}

/** Diagnostic investigation order */
export interface PatientInvestigation {
  readonly id: string;
  name: string;
  mrNo: string;
  modality: string;
  requestedBy: string;
  date: string;
  status: InvestigationStatus;
  hasResult: boolean;
}

/** Doctor-approved clinical investigation report */
export interface PatientApprovedReport {
  readonly id: string;
  readonly mrNo: string;
  readonly reportName: string;
  readonly investigationType: string;
  readonly date: string;
  readonly aiAnalysisFindings: string;
  readonly aiConfidence: string;
  readonly supportingEvidence: string;
  readonly doctorConclusion: string;
  readonly medications: string;
  readonly recommendations: string;
  readonly reviewingDoctor: string;
  readonly doctorLicense: string;
  readonly isDoctorApproved: boolean;
  readonly approvalDate: string;
}

/** In-app notification item */
export interface PatientNotification {
  readonly id: string;
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  type: 'report' | 'appointment' | 'investigation' | 'general';
}

/** Care Journey Pathway step */
export interface CareJourneyStep {
  readonly stepNumber: number;
  readonly title: string;
  readonly description: string;
  readonly status: 'completed' | 'current' | 'upcoming';
}
