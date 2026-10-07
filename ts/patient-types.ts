/**
 * MediSight AI - Patient Dashboard Type Definitions
 * TypeScript interfaces and types for the 4-tab hospital patient portal:
 * 1. Book an Appointment
 * 2. Records
 * 3. Reports
 * 4. About Us
 */

export type PatientPortalTab =
  | 'book-appointment'
  | 'records'
  | 'reports'
  | 'about-us';

export type ReportDisplayMode = 'initial' | 'doctor-approved';

/** Appointment booking request model */
export interface AppointmentBookingRequest {
  patientName: string;
  mrNo: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  contactNumber: string;
  preferredDate: string;
  preferredTime: string;
  departmentSpecialist: string;
  reasonForVisit: string;
  symptomsNotes: string;
}

/** Records tab summary */
export interface PatientRecordSummary {
  lastDateOfVisit: string;
  patientName: string;
  mrNo: string;
  previousDiagnosis: string;
}

/** Reports tab medical report model */
export interface PatientMedicalReport {
  mrNo: string;
  patientName: string;
  age: number;
  gender: string;
  investigationType: string;
  investigationDate: string;
  doctorComments?: string;
  diagnosis?: string;
  medications?: string;
  recommendations?: string;
  attendingDoctor: string;
  doctorLicense: string;
  status: 'Pending' | 'Doctor Approved';
}
