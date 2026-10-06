/**
 * MediSight AI - Specialist Medical Imaging & AI Analysis
 * TypeScript Source for Specialist Imaging Workflow
 */

import { PatientRecord, ClinicalReport, ImagingModality } from './doctor-types';

export const defaultPatients: PatientRecord[] = [
  {
    mrNo: 'MR001',
    name: 'Arun Kumar',
    age: 45,
    gender: 'Male',
    symptoms: 'Chest pain',
    clinicalNotes: 'Patient presents with acute retrosternal chest pain radiating to left shoulder on moderate exertion. BP: 138/86 mmHg, Pulse: 82 bpm. Resting ECG shows sinus rhythm without acute ST changes.',
    investigationStatus: 'Digital Chest Radiography (PA View) Indexed',
    assignedSpecialist: 'Dr. Joseph (Cardiology)',
    aiAnalysisStatus: 'AI Preliminary Analysis Complete • Requires Physician Review',
    status: 'Pending'
  },
  {
    mrNo: 'MR002',
    name: 'Priya Devi',
    age: 32,
    gender: 'Female',
    symptoms: 'Persistent cough',
    clinicalNotes: 'Patient reports 3-week dry cough worsening at night. Low-grade evening fever (37.9°C). Non-smoker, no hemoptysis. Normal vesicular breath sounds bilaterally with occasional expiratory rhonchi.',
    investigationStatus: 'High-Resolution Digital Chest X-Ray Completed',
    assignedSpecialist: 'Dr. Melvin (Pulmonology)',
    aiAnalysisStatus: 'AI Preliminary Analysis Complete • Physician Verified',
    status: 'Completed'
  },
  {
    mrNo: 'MR003',
    name: 'Rahul S',
    age: 58,
    gender: 'Male',
    symptoms: 'Shortness of breath',
    clinicalNotes: 'Progressive exertional dyspnea (NYHA Class II) for 2 months. 15 pack-years smoking history (quit 3 years ago). SpO2: 94% on room air. Scattered bilateral basal crepitations.',
    investigationStatus: 'Digital Chest Radiography Completed • PFT Scheduled',
    assignedSpecialist: 'Dr. Ilakkiya (Respiratory & Thoracic Imaging)',
    aiAnalysisStatus: 'AI Preliminary Analysis Complete • Requires Physician Review',
    status: 'Pending'
  }
];

export const defaultReports: Record<string, ClinicalReport> = {
  'MR001': {
    mrNo: 'MR001',
    patientName: 'Arun Kumar',
    age: 45,
    gender: 'Male',
    investigationType: 'Digital Chest Radiography (PA View)',
    modality: 'XRay',
    aiPreliminaryReportStatus: 'AI Preliminary Analysis Available',
    doctorReviewStatus: 'In Review by Attending Physician',
    finalReportStatus: 'Pending Final Physician Approval',
    aiFindings: 'Possible mild cardiomegaly with subtle perihilar vascular prominence. No acute pneumothorax or focal consolidations detected.',
    confidence: 'Confidence: 86% (Uncertainty margin: ±3%)',
    evidenceExplanation: 'Cardiothoracic ratio calculated at ~0.52. Correlated with clinical presentation of exertional chest discomfort and borderline hypertension. Suggestive of early hypertensive cardiac strain.',
    doctorConclusion: 'Findings suggestive of hypertensive cardiac strain. Advised 2D Echocardiogram, serial troponin-I monitoring, and immediate cardiology consultation.',
    medications: 'Tab. Amlodipine 5mg OD (morning), Tab. Aspirin 75mg OD (post-meal), Tab. Sorbitrate 5mg SL PRN for acute chest discomfort.',
    recommendations: '2D Echocardiogram with Doppler study within 48 hours, Low sodium cardiac diet, Continuous ambulatory Holter monitoring for 24 hours.',
    additionalNotes: 'Patient instructed to report to emergency immediately if retrosternal pain exceeds 15 minutes or radiates to jaw/arm.',
    reviewedBy: 'Dr. Joison',
    isApproved: false,
    isFinalSent: false
  },
  'MR002': {
    mrNo: 'MR002',
    patientName: 'Priya Devi',
    age: 32,
    gender: 'Female',
    investigationType: 'High-Resolution Digital Chest X-Ray',
    modality: 'XRay',
    aiPreliminaryReportStatus: 'AI Preliminary Analysis Verified',
    doctorReviewStatus: 'Reviewed & Confirmed by Dr. Melvin',
    finalReportStatus: 'Approved & Finalized by Physician',
    aiFindings: 'Possible patchy opacity in right middle lobe region suggestive of localized subacute bronchitic / inflammatory changes.',
    confidence: 'Confidence: 89% (Uncertainty margin: ±2%)',
    evidenceExplanation: 'Multimodal correlation with 3-week dry cough duration, elevated Serum CRP (14.2 mg/L), and mild expiratory wheeze. Normal costophrenic angles bilaterally.',
    doctorConclusion: 'Clinical findings suggestive of post-viral subacute bronchitis with mild reactive airway component. Responding favorably to inhaled bronchodilator therapy.',
    medications: 'Budesonide + Formoterol Inhaler (200/6 mcg) 1 puff BID x 14 days, Tab. Montelukast 10mg OD at bedtime, Steam inhalation BID.',
    recommendations: 'Avoid cold exposure and airborne irritants. Follow-up spirometry if cough persists beyond 2 weeks.',
    additionalNotes: 'Complete blood count shows mild leukocytosis consistent with resolving subacute respiratory tract inflammation.',
    reviewedBy: 'Dr. Melvin',
    isApproved: true,
    isFinalSent: true,
    approvalTimestamp: '2026-10-06 14:30 IST'
  },
  'MR003': {
    mrNo: 'MR003',
    patientName: 'Rahul S',
    age: 58,
    gender: 'Male',
    investigationType: 'Digital Chest Radiography (PA & Lateral Views)',
    modality: 'CT Scan',
    aiPreliminaryReportStatus: 'AI Preliminary Analysis Available',
    doctorReviewStatus: 'Awaiting Attending Physician Review',
    finalReportStatus: 'Pending Final Physician Approval',
    aiFindings: 'Possible hyperinflation of bilateral lung fields with flattened diaphragms suggestive of chronic obstructive pulmonary pattern.',
    confidence: 'Confidence: 85% (Uncertainty margin: ±4%)',
    evidenceExplanation: 'Widened intercostal spaces and increased retrosternal clear space correlated with 15 pack-year smoking history and progressive exertional dyspnea.',
    doctorConclusion: 'Radiological appearance suggestive of early chronic obstructive pulmonary disease (COPD). Spirometry with post-bronchodilator reversibility test recommended.',
    medications: 'Tiotropium Inhaler 18 mcg OD, Salbutamol MDI 100 mcg PRN for sudden breathlessness, Pulmonary rehabilitation breathing exercises.',
    recommendations: 'Comprehensive Pulmonary Function Testing (PFT), Smoking cessation counselling, Annual influenza vaccination.',
    additionalNotes: 'Patient has been scheduled for follow-up evaluation with Dr. Ilakkiya.',
    reviewedBy: 'Dr. Ilakkiya',
    isApproved: false,
    isFinalSent: false
  }
};

export class SpecialistImagingService {
  private currentMrNo: string = 'MR001';

  constructor() {
    this.init();
  }

  private loadPatients(): PatientRecord[] {
    try {
      const stored = localStorage.getItem('medisight_patients');
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return JSON.parse(JSON.stringify(defaultPatients));
  }

  private savePatients(patients: PatientRecord[]): void {
    try {
      localStorage.setItem('medisight_patients', JSON.stringify(patients));
    } catch (e) {}
  }

  private loadReports(): Record<string, ClinicalReport> {
    try {
      const stored = localStorage.getItem('medisight_reports');
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return JSON.parse(JSON.stringify(defaultReports));
  }

  private saveReports(reports: Record<string, ClinicalReport>): void {
    try {
      localStorage.setItem('medisight_reports', JSON.stringify(reports));
    } catch (e) {}
  }

  public getPatient(mrNo: string): PatientRecord | undefined {
    return this.loadPatients().find(p => p.mrNo === mrNo);
  }

  public getReport(mrNo: string): ClinicalReport | undefined {
    return this.loadReports()[mrNo];
  }

  public submitAnalysis(mrNo: string, modality: ImagingModality): void {
    const patients = this.loadPatients();
    const patient = patients.find(p => p.mrNo === mrNo);
    if (patient) {
      patient.status = 'Completed';
      patient.investigationStatus = `${modality} Completed • AI Analyzed`;
      patient.aiAnalysisStatus = 'AI Analysis Completed • Report Generated';
      this.savePatients(patients);
    }

    const reports = this.loadReports();
    if (reports[mrNo]) {
      reports[mrNo].modality = modality;
      reports[mrNo].investigationType = `${modality} Examination`;
      reports[mrNo].aiPreliminaryReportStatus = 'AI Preliminary Analysis Available';
      reports[mrNo].finalReportStatus = 'Pending Final Physician Approval';
    }
    this.saveReports(reports);
  }

  public init(): void {
    const params = new URLSearchParams(window.location.search);
    const mrNo = params.get('mrNo');
    if (mrNo) {
      this.currentMrNo = mrNo.toUpperCase();
    }
  }
}
