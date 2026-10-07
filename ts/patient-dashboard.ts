/**
 * MediSight AI - Patient Dashboard TypeScript Implementation
 * Strictly 4 Tabs: Book an Appointment | Records | Reports | About Us.
 */

import {
  PatientPortalTab,
  ReportDisplayMode,
  AppointmentBookingRequest,
  PatientRecordSummary,
  PatientMedicalReport
} from './patient-types';

export const defaultPatientSummary: PatientRecordSummary = {
  lastDateOfVisit: 'October 06, 2026',
  patientName: 'Arun Kumar',
  mrNo: 'MR001',
  previousDiagnosis: 'Early Hypertensive Cardiac Strain • Borderline Cardiomegaly'
};

export const defaultMedicalReport: PatientMedicalReport = {
  mrNo: 'MR001',
  patientName: 'Arun Kumar',
  age: 45,
  gender: 'Male',
  investigationType: 'Digital Chest Radiography (PA View)',
  investigationDate: 'October 06, 2026',
  doctorComments: 'Evaluated digital chest radiograph alongside clinical presentation of exertional chest discomfort and borderline hypertension (138/86 mmHg). Cardiothoracic ratio calculated at ~0.52. Subtle perihilar prominence noted without acute focal consolidation or pneumothorax.',
  diagnosis: 'Clinical findings suggestive of early hypertensive cardiac strain. Borderline cardiomegaly (Cardiothoracic ratio ~0.52).',
  medications: 'Tab. Amlodipine 5mg OD (morning), Tab. Aspirin 75mg OD (post-meal), Tab. Sorbitrate 5mg SL PRN for acute chest discomfort.',
  recommendations: '2D Echocardiogram with Doppler study within 48 hours, Low sodium cardiac diet, 24-hour ambulatory blood pressure monitoring.',
  attendingDoctor: 'Dr. Joison, MD',
  doctorLicense: 'MED-REG-84920-KA',
  status: 'Doctor Approved'
};

export class PatientDashboardManager {
  private currentTab: PatientPortalTab = 'book-appointment';
  private reportMode: ReportDisplayMode = 'initial';

  public switchTab(tab: PatientPortalTab): void {
    this.currentTab = tab;
  }

  public getCurrentTab(): PatientPortalTab {
    return this.currentTab;
  }

  public setReportMode(mode: ReportDisplayMode): void {
    this.reportMode = mode;
  }

  public getReportMode(): ReportDisplayMode {
    return this.reportMode;
  }

  public getRecordSummary(): PatientRecordSummary {
    return defaultPatientSummary;
  }

  public getMedicalReport(): PatientMedicalReport {
    return defaultMedicalReport;
  }

  public bookAppointment(request: AppointmentBookingRequest): boolean {
    return Boolean(request.patientName && request.preferredDate && request.contactNumber);
  }
}
