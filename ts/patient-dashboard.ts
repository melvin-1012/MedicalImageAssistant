/**
 * MediSight AI - Patient Dashboard TypeScript Source
 * TypeScript implementation matching js/patient-dashboard.js
 */

import {
  PatientProfile,
  PatientAppointment,
  PatientMedicalRecord,
  PatientInvestigation,
  PatientApprovedReport,
  PatientNotification,
  PatientPortalTab
} from './patient-types';

export const defaultProfile: PatientProfile = {
  mrNo: 'MR001',
  name: 'Arun Kumar',
  age: 45,
  gender: 'Male',
  phone: '+91 98451 23098',
  email: 'arun.kumar@gmail.com',
  bloodGroup: 'O+ Positive',
  emergencyContact: 'Sunita Kumar (Spouse) - +91 98451 23099',
  address: '#42, 4th Cross, Indiranagar, Bengaluru, Karnataka 560038',
  primaryDoctor: 'Dr. Joison, MD',
  knownAllergies: 'Penicillin (Mild urticaria), Dust mites'
};

export const defaultAppointments: PatientAppointment[] = [
  {
    id: 'apt-101',
    doctor: 'Dr. Joison, MD',
    department: 'Radiology & Thoracic Medicine',
    date: 'Oct 12, 2026',
    time: '10:30 AM',
    status: 'Upcoming',
    reason: 'Follow-up clinical consultation regarding chest radiograph findings and blood pressure medication review.',
    room: 'OPD Room 204, Main Block'
  },
  {
    id: 'apt-102',
    doctor: 'Dr. Joseph, MD',
    department: 'Division of Cardiovascular Medicine',
    date: 'Oct 18, 2026',
    time: '02:00 PM',
    status: 'Upcoming',
    reason: 'Specialist cardiology evaluation & 2D Echocardiogram Doppler review.',
    room: 'Cardiology Clinic, 3rd Floor'
  },
  {
    id: 'apt-103',
    doctor: 'Dr. Melvin, MD',
    department: 'Pulmonary & Respiratory Medicine',
    date: 'Sep 24, 2026',
    time: '11:00 AM',
    status: 'Completed',
    reason: 'Respiratory symptom evaluation & spirometry baseline assessment.',
    room: 'Chest Clinic Room 108'
  },
  {
    id: 'apt-104',
    doctor: 'Dr. Ilakkiya, MD',
    department: 'Clinical Diagnostic AI & Triage',
    date: 'Aug 15, 2026',
    time: '09:30 AM',
    status: 'Cancelled',
    reason: 'Annual preventive multimodal imaging intake screening.',
    room: 'Imaging Suite B'
  }
];

export const defaultMedicalRecords: PatientMedicalRecord[] = [
  {
    id: 'rec-001',
    title: 'Acute Episode Consultation & Diagnostic Triage',
    date: 'Oct 06, 2026',
    doctor: 'Dr. Joison, MD',
    department: 'Radiology & Thoracic Medicine',
    diagnosisNotes: 'Patient presented with acute retrosternal chest pain radiating to left shoulder on moderate exertion. Blood pressure: 138/86 mmHg, Pulse: 82 bpm. Resting ECG showed normal sinus rhythm without acute ST depression. Ordered Digital Chest Radiography (PA View) to evaluate cardiothoracic ratio.',
    prescriptions: 'Tab. Amlodipine 5mg OD (morning), Tab. Aspirin 75mg OD (post-meal), Tab. Sorbitrate 5mg SL PRN for acute discomfort.',
    previousHistory: 'Borderline essential hypertension documented since 2024. Non-smoker. No prior cardiac events.',
    isAiAssisted: true
  },
  {
    id: 'rec-002',
    title: 'Annual Preventative Health & Respiratory Check',
    date: 'Mar 14, 2026',
    doctor: 'Dr. Melvin, MD',
    department: 'Pulmonary & Critical Care',
    diagnosisNotes: 'Routine annual corporate health evaluation. Vitals within normal limits. Spirometry demonstrated preserved pulmonary mechanics (FEV1/FVC ratio 82%). Fasting lipid panel demonstrated borderline elevated LDL cholesterol (134 mg/dL).',
    prescriptions: 'Tab. Atorvastatin 10mg HS, Dietary lifestyle modifications advised.',
    previousHistory: 'Family history of ischemic heart disease (father).',
    isAiAssisted: false
  },
  {
    id: 'rec-003',
    title: 'Post-Viral Subacute Respiratory Episode',
    date: 'Nov 19, 2025',
    doctor: 'Dr. Melvin, MD',
    department: 'Pulmonary & Critical Care',
    diagnosisNotes: 'Dry irritating cough of 10 days duration post-influenza. Clear breath sounds bilaterally without rhonchi. Complete blood count showed mild lymphocytosis consistent with resolving viral bronchitis.',
    prescriptions: 'Budesonide Inhaler 200mcg 1 puff BID x 7 days, Steam inhalation.',
    previousHistory: 'Resolved satisfactorily within 1 week.',
    isAiAssisted: false
  }
];

export const defaultInvestigations: PatientInvestigation[] = [
  {
    id: 'inv-001',
    name: 'Digital Chest Radiography (PA View)',
    mrNo: 'MR001',
    modality: 'XRay',
    requestedBy: 'Dr. Joison, MD',
    date: 'Oct 06, 2026',
    status: 'Completed',
    hasResult: true
  },
  {
    id: 'inv-002',
    name: 'High-Resolution Computed Tomography (Thorax)',
    mrNo: 'MR001',
    modality: 'CT Scan',
    requestedBy: 'Dr. Melvin, MD',
    date: 'Oct 08, 2026',
    status: 'In Progress',
    hasResult: false
  },
  {
    id: 'inv-003',
    name: '2D Echocardiogram with Color Doppler',
    mrNo: 'MR001',
    modality: 'MRI / Echo',
    requestedBy: 'Dr. Joseph, MD',
    date: 'Oct 14, 2026',
    status: 'Requested',
    hasResult: false
  }
];

export const defaultNotifications: PatientNotification[] = [
  {
    id: 'notif-1',
    title: 'Your final medical report is available.',
    message: 'Dr. Joison, MD has completed and approved your Digital Chest Radiography report with conclusion and prescribed medications.',
    timestamp: 'Today • 14:45 IST',
    isRead: false,
    type: 'report'
  },
  {
    id: 'notif-2',
    title: 'Your investigation report is now available.',
    message: 'Digital Chest Radiography (PA View) scan and preliminary imaging analysis have been uploaded to your medical records.',
    timestamp: 'Today • 11:20 IST',
    isRead: false,
    type: 'investigation'
  },
  {
    id: 'notif-3',
    title: 'Your appointment has been confirmed.',
    message: 'Follow-up clinical consultation with Dr. Joison, MD is scheduled for Oct 12, 2026 at 10:30 AM in OPD Room 204.',
    timestamp: 'Yesterday • 16:30 IST',
    isRead: true,
    type: 'appointment'
  },
  {
    id: 'notif-4',
    title: 'Your doctor has reviewed your report.',
    message: 'Dr. Joseph (Cardiology) reviewed your clinical records and recommended scheduling a 2D Echocardiogram evaluation.',
    timestamp: 'Oct 05, 2026 • 11:00 IST',
    isRead: true,
    type: 'general'
  }
];

export class PatientPortalService {
  private profile: PatientProfile = defaultProfile;
  private appointments: PatientAppointment[] = defaultAppointments;
  private notifications: PatientNotification[] = defaultNotifications;
  private currentTab: PatientPortalTab = 'dashboard';

  constructor() {
    this.loadState();
  }

  private loadState(): void {
    try {
      const storedProfile = localStorage.getItem('medisight_patient_profile');
      if (storedProfile) {
        this.profile = { ...defaultProfile, ...JSON.parse(storedProfile) };
      }
    } catch (e) {}
  }

  public getProfile(): PatientProfile {
    return this.profile;
  }

  public updateProfile(updated: Partial<PatientProfile>): void {
    this.profile = { ...this.profile, ...updated };
    try {
      localStorage.setItem('medisight_patient_profile', JSON.stringify(this.profile));
    } catch (e) {}
  }

  public getAppointments(): PatientAppointment[] {
    return this.appointments;
  }

  public addAppointment(apt: PatientAppointment): void {
    this.appointments.unshift(apt);
  }

  public getNotifications(): PatientNotification[] {
    return this.notifications;
  }

  public markNotificationsRead(): void {
    this.notifications = this.notifications.map(n => ({ ...n, isRead: true }));
  }

  public getApprovedReport(): PatientApprovedReport {
    return {
      id: 'REP-MR001-2026',
      mrNo: 'MR001',
      reportName: 'Digital Chest Radiography Report',
      investigationType: 'Digital Chest Radiography (PA View)',
      date: 'Oct 06, 2026',
      aiAnalysisFindings: 'Possible mild cardiomegaly with subtle perihilar vascular prominence. No acute pneumothorax or focal consolidations detected.',
      aiConfidence: 'Confidence: 86%',
      supportingEvidence: 'Cardiothoracic ratio calculated at ~0.52. Localized subtle vascular prominence identified in bilateral perihilar regions.',
      doctorConclusion: 'Clinical findings suggestive of early hypertensive cardiac strain. Advised 2D Echocardiogram and cardiology consultation.',
      medications: 'Tab. Amlodipine 5mg OD, Tab. Aspirin 75mg OD, Tab. Sorbitrate 5mg SL PRN.',
      recommendations: 'Low sodium cardiac diet, repeat check in 2 weeks.',
      reviewingDoctor: 'Dr. Joison, MD',
      doctorLicense: 'MED-REG-84920-KA',
      isDoctorApproved: true,
      approvalDate: 'Oct 06, 2026 14:30 IST'
    };
  }

  public switchTab(tab: PatientPortalTab): void {
    this.currentTab = tab;
  }

  public getCurrentTab(): PatientPortalTab {
    return this.currentTab;
  }
}
