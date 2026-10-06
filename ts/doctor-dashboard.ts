/**
 * MediSight AI - Doctor Dashboard Logic (TypeScript)
 * Clinical Decision-Support System - Doctor Workspace
 */

import { DashboardTab, PatientRecord, ClinicalReport, DoctorProfile } from './doctor-types';

// ============================================================================
// Mock Clinical Data Store
// ============================================================================
export const initialPatients: PatientRecord[] = [
  {
    mrNo: 'MR001',
    name: 'Arun Kumar',
    age: 45,
    gender: 'Male',
    symptoms: 'Chest pain',
    clinicalNotes: 'Patient presents with acute retrosternal chest pain radiating to left shoulder on moderate exertion. BP: 138/86 mmHg, Pulse: 82 bpm. Resting ECG shows sinus rhythm without acute ST changes.',
    investigationStatus: 'Digital Chest Radiography (PA View) Indexed',
    assignedSpecialist: 'Dr. Sunita Rao, MD (Cardiology)',
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
    assignedSpecialist: 'Dr. Rajesh Sharma, MD (Pulmonology)',
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
    assignedSpecialist: 'Dr. Anand Verma, MD (Respiratory Medicine)',
    aiAnalysisStatus: 'AI Preliminary Analysis Complete • Requires Physician Review',
    status: 'Pending'
  }
];

export const initialReports: Record<string, ClinicalReport> = {
  'MR001': {
    mrNo: 'MR001',
    patientName: 'Arun Kumar',
    age: 45,
    gender: 'Male',
    investigationType: 'Digital Chest Radiography (PA View)',
    aiPreliminaryReportStatus: 'AI Preliminary Analysis Available',
    doctorReviewStatus: 'In Review by Attending Physician',
    finalReportStatus: 'Pending Final Physician Approval',
    aiFindings: 'Possible mild cardiomegaly with subtle perihilar vascular prominence. No acute pneumothorax or focal consolidations detected.',
    confidence: 'Confidence: 86% (Uncertainty margin: ±3%)',
    evidenceExplanation: 'Cardiothoracic ratio calculated at ~0.52. Correlated with clinical presentation of exertional chest discomfort and borderline hypertension. Suggestive of early hypertensive cardiac strain.',
    doctorConclusion: 'Findings suggestive of hypertensive cardiac strain. Advised 2D Echocardiogram, serial troponin-I monitoring, and immediate cardiology consultation.',
    medications: 'Tab. Amlodipine 5mg OD (morning), Tab. Aspirin 75mg OD (post-meal), Tab. Sorbitrate 5mg SL PRN for acute chest discomfort.',
    isApproved: false
  },
  'MR002': {
    mrNo: 'MR002',
    patientName: 'Priya Devi',
    age: 32,
    gender: 'Female',
    investigationType: 'Digital Chest Radiography (PA View)',
    aiPreliminaryReportStatus: 'AI Preliminary Analysis Verified',
    doctorReviewStatus: 'Reviewed & Confirmed by Dr. Rajesh Sharma, MD',
    finalReportStatus: 'Approved & Signed by Attending Physician',
    aiFindings: 'Possible patchy opacity in right middle lobe region suggestive of localized subacute bronchitic / inflammatory changes.',
    confidence: 'Confidence: 89% (Uncertainty margin: ±2%)',
    evidenceExplanation: 'Multimodal correlation with 3-week dry cough duration, elevated Serum CRP (14.2 mg/L), and mild expiratory wheeze. Normal costophrenic angles bilaterally.',
    doctorConclusion: 'Clinical findings suggestive of post-viral subacute bronchitis with mild reactive airway component. Responding favorably to inhaled bronchodilator therapy.',
    medications: 'Budesonide + Formoterol Inhaler (200/6 mcg) 1 puff BID x 14 days, Tab. Montelukast 10mg OD at bedtime, Steam inhalation BID.',
    isApproved: true,
    approvalTimestamp: '2026-10-06 14:30 IST'
  },
  'MR003': {
    mrNo: 'MR003',
    patientName: 'Rahul S',
    age: 58,
    gender: 'Male',
    investigationType: 'Digital Chest Radiography (PA & Lateral Views)',
    aiPreliminaryReportStatus: 'AI Preliminary Analysis Available',
    doctorReviewStatus: 'Awaiting Attending Physician Review',
    finalReportStatus: 'Pending Final Physician Approval',
    aiFindings: 'Possible hyperinflation of bilateral lung fields with flattened diaphragms suggestive of chronic obstructive pulmonary pattern.',
    confidence: 'Confidence: 85% (Uncertainty margin: ±4%)',
    evidenceExplanation: 'Widened intercostal spaces and increased retrosternal clear space correlated with 15 pack-year smoking history and progressive exertional dyspnea.',
    doctorConclusion: 'Radiological appearance suggestive of early chronic obstructive pulmonary disease (COPD). Spirometry with post-bronchodilator reversibility test recommended.',
    medications: 'Tiotropium Inhaler 18 mcg OD, Salbutamol MDI 100 mcg PRN for sudden breathlessness, Pulmonary rehabilitation breathing exercises.',
    isApproved: false
  }
};

export const doctorProfileData: DoctorProfile = {
  name: 'Dr. Rajesh Sharma, MD',
  title: 'Consultant Radiologist & Pulmonologist',
  licenseNo: 'MED-REG-84920-KA',
  department: 'Division of Diagnostic Imaging & Thoracic Medicine',
  hospital: 'MediSight Memorial Teaching Hospital',
  email: 'dr.sharma@medisight.health',
  phone: '+91 (080) 4590-2100 Ext. 402',
  experienceYears: 14,
  specialization: 'High-Resolution Thoracic Imaging, Multimodal Image Diagnostics, Interventional Pulmonology',
  consultationHours: 'Mon – Fri: 09:00 AM – 04:30 PM IST',
  verifiedStatus: true
};

// ============================================================================
// State Management
// ============================================================================
class DoctorDashboardApp {
  private activeTab: DashboardTab = 'patients';
  private patients: PatientRecord[] = [...initialPatients];
  private reports: Record<string, ClinicalReport> = { ...initialReports };
  private selectedPatientMrNo: string = 'MR001';
  private doctorProfile: DoctorProfile = { ...doctorProfileData };

  constructor() {
    this.init();
  }

  private init(): void {
    this.renderPatientsTable();
    this.renderPatientStatusTable();
    this.renderReportView(this.selectedPatientMrNo);
    this.renderDoctorProfile();
    this.bindEvents();
    this.handleUrlHash();
  }

  /**
   * Switch between Dashboard Tabs (Patients, Patient Status, Reports, Doctor Profile)
   */
  public switchTab(tabId: DashboardTab): void {
    this.activeTab = tabId;

    // Update Tab Buttons in Header & Bar
    document.querySelectorAll<HTMLElement>('.dash-nav-tab').forEach((tab) => {
      const target = tab.getAttribute('data-tab');
      if (target === tabId) {
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
      } else {
        tab.classList.remove('active');
        tab.setAttribute('aria-selected', 'false');
      }
    });

    // Update Panels
    document.querySelectorAll<HTMLElement>('.dash-view-panel').forEach((panel) => {
      if (panel.id === `view-${tabId}`) {
        panel.classList.add('active');
      } else {
        panel.classList.remove('active');
      }
    });

    // Refresh view data
    if (tabId === 'patients') {
      this.renderPatientsTable();
    } else if (tabId === 'patient-status') {
      this.renderPatientStatusTable();
    } else if (tabId === 'reports') {
      this.renderReportView(this.selectedPatientMrNo);
    } else if (tabId === 'profile') {
      this.renderDoctorProfile();
    }

    // Scroll smoothly to top of content
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /**
   * 1. Render Patients Table
   */
  private renderPatientsTable(): void {
    const tbody = document.getElementById('patients-tbody');
    if (!tbody) return;

    tbody.innerHTML = this.patients.map((p) => `
      <tr>
        <td class="font-mono text-primary font-bold">${p.mrNo}</td>
        <td>
          <div class="patient-name-cell">
            <span class="patient-avatar-letter">${p.name.charAt(0)}</span>
            <span class="font-semibold">${p.name}</span>
          </div>
        </td>
        <td>${p.age}</td>
        <td>${p.gender}</td>
        <td>
          <span class="badge badge-subtle">${p.symptoms}</span>
        </td>
        <td class="text-right">
          <button type="button" class="btn btn-outline-primary btn-sm btn-view-patient" data-mrno="${p.mrNo}">View</button>
        </td>
      </tr>
    `).join('');

    tbody.querySelectorAll<HTMLButtonElement>('.btn-view-patient').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const mrNo = btn.getAttribute('data-mrno');
        if (mrNo) this.openPatientDetails(mrNo);
      });
    });
  }

  /**
   * Show Patient Detail Slide-Over / Modal
   */
  public openPatientDetails(mrNo: string): void {
    const patient = this.patients.find(p => p.mrNo === mrNo);
    if (!patient) return;

    const modal = document.getElementById('patient-detail-modal');
    const container = document.getElementById('patient-detail-content');
    if (!modal || !container) return;

    container.innerHTML = `
      <div class="patient-detail-card">
        <div class="detail-header-strip">
          <div>
            <span class="badge badge-primary font-mono">${patient.mrNo}</span>
            <h3 class="detail-title">${patient.name}</h3>
            <p class="detail-sub">${patient.age} yrs • ${patient.gender}</p>
          </div>
          <span class="badge ${patient.status === 'Completed' ? 'badge-success' : 'badge-warning'}">
            ${patient.status}
          </span>
        </div>

        <div class="detail-grid">
          <div class="detail-field">
            <span class="detail-label">Reported Symptoms</span>
            <div class="detail-value text-strong">${patient.symptoms}</div>
          </div>

          <div class="detail-field">
            <span class="detail-label">Investigation Status</span>
            <div class="detail-value">${patient.investigationStatus}</div>
          </div>

          <div class="detail-field">
            <span class="detail-label">Assigned Specialist</span>
            <div class="detail-value text-primary font-semibold">${patient.assignedSpecialist}</div>
          </div>

          <div class="detail-field">
            <span class="detail-label">AI Analysis Status</span>
            <div class="detail-value">
              <span class="badge badge-teal">${patient.aiAnalysisStatus}</span>
            </div>
          </div>

          <div class="detail-field col-span-2">
            <span class="detail-label">Clinical Notes</span>
            <div class="detail-notes-box">${patient.clinicalNotes}</div>
          </div>
        </div>

        <div class="detail-actions">
          <button type="button" class="btn btn-teal btn-refer-specialist" data-mrno="${patient.mrNo}" data-name="${patient.name}" data-specialist="${patient.assignedSpecialist}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <polyline points="17 11 19 13 23 9"></polyline>
            </svg>
            Refer to Specialist
          </button>
          <button type="button" class="btn btn-outline" id="btn-close-detail">
            Close
          </button>
        </div>
      </div>
    `;

    modal.classList.add('is-active');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  public closePatientDetails(): void {
    const modal = document.getElementById('patient-detail-modal');
    if (!modal) return;
    modal.classList.remove('is-active');
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  /**
   * Refer to Specialist Action (Frontend-Only Success Notification)
   */
  public referToSpecialist(mrNo: string, patientName: string, specialist: string): void {
    this.showToast(
      'Referral Sent',
      `Patient ${patientName} (${mrNo}) has been successfully referred to ${specialist}. Electronic handover queued for specialist review.`,
      'success'
    );
    this.closePatientDetails();
  }

  /**
   * 2. Render Patient Status Table
   */
  private renderPatientStatusTable(): void {
    const tbody = document.getElementById('patient-status-tbody');
    if (!tbody) return;

    tbody.innerHTML = this.patients.map((p) => {
      const isCompleted = p.status === 'Completed';
      return `
        <tr>
          <td class="font-mono text-primary font-bold">${p.mrNo}</td>
          <td>
            <div class="patient-name-cell">
              <span class="patient-avatar-letter">${p.name.charAt(0)}</span>
              <span class="font-semibold">${p.name}</span>
            </div>
          </td>
          <td>${p.age}</td>
          <td>${p.gender}</td>
          <td>
            <span class="badge ${isCompleted ? 'badge-success' : 'badge-warning'}">
              <span class="badge-dot"></span>
              ${p.status}
            </span>
          </td>
          <td class="text-right">
            ${isCompleted ? `
              <button type="button" class="btn btn-primary btn-sm btn-status-view-report" data-mrno="${p.mrNo}">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                </svg>
                View Report
              </button>
            ` : `
              <span class="text-muted text-sm font-medium">Pending Review</span>
            `}
          </td>
        </tr>
      `;
    }).join('');
  }

  /**
   * 3. Render Reports View
   */
  public renderReportView(mrNo: string): void {
    this.selectedPatientMrNo = mrNo;
    const report = this.reports[mrNo];
    const container = document.getElementById('report-display-container');
    if (!container) return;

    if (!report) {
      container.innerHTML = `
        <div class="empty-report-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <h3>No Report Found for ${mrNo}</h3>
          <p>Please enter a valid Medical Record Number (e.g. MR001, MR002, MR003).</p>
        </div>
      `;
      return;
    }

    // Highlight Quick Select Button
    document.querySelectorAll<HTMLElement>('.mr-quick-btn').forEach(btn => {
      if (btn.getAttribute('data-mrno') === mrNo) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    container.innerHTML = `
      <div class="clinical-report-sheet">
        
        <!-- Hospital Clinical Letterhead -->
        <div class="report-letterhead">
          <div class="report-letterhead-left">
            <div class="brand-group">
              <div class="brand-logo" style="width: 34px; height: 34px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M12 2v20M2 12h20"></path>
                  <circle cx="12" cy="12" r="5" stroke-width="1.8" stroke-dasharray="2 2"></circle>
                </svg>
              </div>
              <div>
                <div class="brand-name" style="font-size: 1.1rem;">MediSight <span>AI</span></div>
                <div class="text-xs text-muted uppercase">Hospital Diagnostic Decision-Support Report</div>
              </div>
            </div>
          </div>
          <div class="report-letterhead-right">
            <div class="font-mono text-sm font-bold text-primary">REPORT REF: REP-${report.mrNo}-2026</div>
            <div class="text-xs text-muted">Status: ${report.isApproved ? '<span class="text-success font-semibold">FINAL SIGNED</span>' : '<span class="text-warning font-semibold">PRELIMINARY REVIEW</span>'}</div>
          </div>
        </div>

        <!-- Mandatory Safety Notice (Strict Medical Compliance) -->
        <div class="clinical-safety-alert-banner" role="alert">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2" style="flex-shrink: 0; margin-top: 2px;">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <div>
            <strong>AI Preliminary Analysis – Requires Physician Review</strong>
            <p class="mb-0 text-sm">
              This report is generated as an assistive clinical decision-support tool. Algorithmic outputs are non-definitive observations and do not replace professional physician diagnosis or clinical judgment.
            </p>
          </div>
        </div>

        <!-- Patient Demographics Strip -->
        <div class="report-patient-meta-grid">
          <div class="meta-item">
            <span class="meta-label">Patient Name</span>
            <span class="meta-value font-bold">${report.patientName}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">MR No</span>
            <span class="meta-value font-mono font-bold text-primary">${report.mrNo}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Age / Gender</span>
            <span class="meta-value">${report.age} Y / ${report.gender}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Investigation Type</span>
            <span class="meta-value">${report.investigationType}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">AI Preliminary Report Status</span>
            <span class="meta-value"><span class="badge badge-teal">${report.aiPreliminaryReportStatus}</span></span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Doctor Review Status</span>
            <span class="meta-value"><span class="badge badge-primary">${report.doctorReviewStatus}</span></span>
          </div>
          <div class="meta-item col-span-2">
            <span class="meta-label">Final Report Status</span>
            <span class="meta-value">
              <span class="badge ${report.isApproved ? 'badge-success' : 'badge-warning'}">
                ${report.finalReportStatus}
              </span>
            </span>
          </div>
        </div>

        <!-- Clinical Findings Content -->
        <div class="report-section-block">
          <h4 class="report-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            AI Findings & Confidence
          </h4>
          <div class="report-findings-card">
            <div class="flex-between">
              <span class="font-semibold text-main">&ldquo;${report.aiFindings}&rdquo;</span>
              <span class="badge badge-primary font-mono">${report.confidence}</span>
            </div>
          </div>
        </div>

        <div class="report-section-block">
          <h4 class="report-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            Evidence / Explanation
          </h4>
          <div class="report-text-box">
            ${report.evidenceExplanation}
          </div>
        </div>

        <div class="report-section-block">
          <h4 class="report-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            Doctor Conclusion
          </h4>
          <div class="report-text-box doctor-note-box">
            ${report.doctorConclusion}
          </div>
        </div>

        <div class="report-section-block">
          <h4 class="report-section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
            Medications & Therapeutic Advice
          </h4>
          <div class="report-meds-box">
            ${report.medications}
          </div>
        </div>

        <!-- Approval Action Strip -->
        <div class="report-footer-actions">
          <div class="report-approval-meta">
            ${report.isApproved ? `
              <span class="text-success font-semibold flex items-center gap-1">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Approved & Signed by Attending Physician (${report.approvalTimestamp || 'Approved'})
              </span>
            ` : `
              <span class="text-muted text-sm">
                Requires physician signature before transmitting to patient health records.
              </span>
            `}
          </div>

          <div>
            ${report.isApproved ? `
              <button type="button" class="btn btn-outline" disabled style="opacity: 0.7; cursor: default;">
                Report Already Finalized
              </button>
            ` : `
              <button type="button" class="btn btn-primary btn-lg" id="btn-approve-report" data-mrno="${report.mrNo}">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Approve & Send Final Report
              </button>
            `}
          </div>
        </div>

      </div>
    `;
  }

  /**
   * 4. Render Doctor Profile View
   */
  public renderDoctorProfile(): void {
    const container = document.getElementById('doctor-profile-container');
    if (!container) return;

    const p = this.doctorProfile;

    container.innerHTML = `
      <div class="profile-card-wrapper">
        <div class="profile-hero-card">
          <div class="profile-avatar-large">
            <span>RS</span>
          </div>
          <div class="profile-main-meta">
            <div class="flex-between">
              <div>
                <h2 class="profile-name">${p.name}</h2>
                <p class="profile-title">${p.title}</p>
                <p class="profile-dept">${p.department}</p>
              </div>
              <span class="badge badge-success">
                <span class="badge-dot"></span>
                Verified Attending Physician
              </span>
            </div>
            <div class="profile-hospital-tag">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v20M2 12h20"></path>
              </svg>
              ${p.hospital}
            </div>
          </div>
        </div>

        <div class="profile-details-grid">
          <div class="profile-field-card">
            <span class="profile-field-label">Medical Registration / License</span>
            <span class="profile-field-value font-mono text-primary font-bold">${p.licenseNo}</span>
          </div>

          <div class="profile-field-card">
            <span class="profile-field-label">Clinical Experience</span>
            <span class="profile-field-value">${p.experienceYears} Years of Clinical Practice</span>
          </div>

          <div class="profile-field-card">
            <span class="profile-field-label">Direct Clinical Contact</span>
            <span class="profile-field-value">${p.email}</span>
            <span class="text-xs text-muted">${p.phone}</span>
          </div>

          <div class="profile-field-card">
            <span class="profile-field-label">Consultation Schedule</span>
            <span class="profile-field-value">${p.consultationHours}</span>
          </div>

          <div class="profile-field-card col-span-2">
            <span class="profile-field-label">Clinical Specialization & Focus</span>
            <span class="profile-field-value">${p.specialization}</span>
          </div>

          <div class="profile-field-card col-span-2" style="background-color: var(--color-bg-subtle);">
            <span class="profile-field-label">Decision-Support Permissions & Governance</span>
            <div class="profile-permissions-list">
              <div class="perm-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Authorized to evaluate AI Preliminary Imaging observations</span>
              </div>
              <div class="perm-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Authorized to formulate, sign, and finalize PACS Diagnostic Reports</span>
              </div>
              <div class="perm-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Institutional cross-department specialist clinical referral authority</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Approve & Send Final Report Action (Frontend Only)
   */
  public approveFinalReport(mrNo: string): void {
    const report = this.reports[mrNo];
    if (!report) return;

    report.isApproved = true;
    report.doctorReviewStatus = 'Reviewed & Confirmed by Dr. Rajesh Sharma, MD';
    report.finalReportStatus = 'Approved & Finalized';
    report.approvalTimestamp = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST';

    // Update patient status in directory
    const patient = this.patients.find(p => p.mrNo === mrNo);
    if (patient) {
      patient.status = 'Completed';
    }

    this.showToast(
      'Report Approved & Finalized',
      `Final report for ${report.patientName} (${report.mrNo}) has been approved by Dr. Rajesh Sharma, MD. Patient status updated to Completed.`,
      'success'
    );

    this.renderReportView(mrNo);
    this.renderPatientStatusTable();
  }

  /**
   * Search Report by MR No or Name
   */
  public searchReport(query: string): void {
    const trimmed = query.trim().toUpperCase();
    if (!trimmed) return;

    // Direct match by MR No or partial name match
    let matchedMrNo = '';
    if (this.reports[trimmed]) {
      matchedMrNo = trimmed;
    } else {
      const patient = this.patients.find(p => 
        p.mrNo.toUpperCase().includes(trimmed) || 
        p.name.toUpperCase().includes(trimmed)
      );
      if (patient) {
        matchedMrNo = patient.mrNo;
      }
    }

    if (matchedMrNo) {
      this.renderReportView(matchedMrNo);
    } else {
      const container = document.getElementById('report-display-container');
      if (container) {
        container.innerHTML = `
          <div class="empty-report-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <h3>No Records Matched "${query}"</h3>
            <p>Try searching with <strong>MR001</strong>, <strong>MR002</strong>, or <strong>MR003</strong>.</p>
          </div>
        `;
      }
    }
  }

  /**
   * 5. Logout Action (Frontend Only)
   */
  public handleLogout(): void {
    this.showToast(
      'Doctor Session Concluded',
      'Dr. Rajesh Sharma has logged out successfully. Returning to MediSight AI landing page...',
      'info'
    );

    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1200);
  }

  /**
   * Toast notification feedback
   */
  public showToast(title: string, message: string, type: 'success' | 'info' | 'warning' = 'success'): void {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-card toast-${type}`;
    toast.innerHTML = `
      <div class="toast-icon">
        ${type === 'success' ? `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        ` : `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        `}
      </div>
      <div class="toast-body">
        <h4 class="toast-title">${title}</h4>
        <p class="toast-message">${message}</p>
      </div>
      <button type="button" class="toast-close" aria-label="Close notification">&times;</button>
    `;

    container.appendChild(toast);

    toast.querySelector('.toast-close')?.addEventListener('click', () => {
      toast.remove();
    });

    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }

  /**
   * Event Listeners
   */
  private bindEvents(): void {
    // Navigation Tabs
    document.querySelectorAll<HTMLElement>('.dash-nav-tab').forEach((tab) => {
      tab.addEventListener('click', (e) => {
        e.preventDefault();
        const targetTab = tab.getAttribute('data-tab') as DashboardTab | null;
        if (targetTab) {
          this.switchTab(targetTab);
          window.location.hash = targetTab;
        }
      });
    });

    // Logout Buttons
    document.querySelectorAll<HTMLElement>('.btn-doctor-logout').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleLogout();
      });
    });

    // Mobile Navbar Drawer
    const mobileToggle = document.getElementById('doctor-mobile-toggle');
    const mobilePanel = document.getElementById('doctor-mobile-panel');
    if (mobileToggle && mobilePanel) {
      mobileToggle.addEventListener('click', () => {
        const isOpen = mobilePanel.classList.toggle('is-open');
        mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });

      mobilePanel.querySelectorAll<HTMLElement>('.mobile-nav-link').forEach(link => {
        link.addEventListener('click', () => {
          mobilePanel.classList.remove('is-open');
          mobileToggle.setAttribute('aria-expanded', 'false');
          const targetTab = link.getAttribute('data-tab') as DashboardTab | null;
          if (targetTab) {
            this.switchTab(targetTab);
            window.location.hash = targetTab;
          }
        });
      });
    }

    // Delegation for Patient View button
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement | null;
      if (!target) return;

      const viewBtn = target.closest<HTMLElement>('.btn-view-patient');
      if (viewBtn) {
        const mrNo = viewBtn.getAttribute('data-mrno');
        if (mrNo) this.openPatientDetails(mrNo);
        return;
      }

      // Close Detail Modal
      if (target.id === 'btn-close-detail' || target.closest('#btn-close-detail')) {
        this.closePatientDetails();
        return;
      }

      // Refer to specialist button
      const referBtn = target.closest<HTMLElement>('.btn-refer-specialist');
      if (referBtn) {
        const mrNo = referBtn.getAttribute('data-mrno') || '';
        const name = referBtn.getAttribute('data-name') || '';
        const specialist = referBtn.getAttribute('data-specialist') || '';
        this.referToSpecialist(mrNo, name, specialist);
        return;
      }

      // View Report button from Patient Status table
      const statusReportBtn = target.closest<HTMLElement>('.btn-status-view-report');
      if (statusReportBtn) {
        const mrNo = statusReportBtn.getAttribute('data-mrno');
        if (mrNo) {
          this.switchTab('reports');
          window.location.hash = 'reports';
          this.renderReportView(mrNo);
        }
        return;
      }

      // Approve & Send Final Report button
      const approveBtn = target.closest<HTMLElement>('#btn-approve-report');
      if (approveBtn) {
        const mrNo = approveBtn.getAttribute('data-mrno');
        if (mrNo) this.approveFinalReport(mrNo);
        return;
      }

      // Quick Select Pills in Reports
      const quickBtn = target.closest<HTMLElement>('.mr-quick-btn');
      if (quickBtn) {
        const mrNo = quickBtn.getAttribute('data-mrno');
        if (mrNo) {
          const searchInput = document.getElementById('search-mrno-input') as HTMLInputElement | null;
          if (searchInput) searchInput.value = mrNo;
          this.renderReportView(mrNo);
        }
        return;
      }
    });

    // Close detail modal on backdrop click
    const detailModal = document.getElementById('patient-detail-modal');
    if (detailModal) {
      detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) {
          this.closePatientDetails();
        }
      });
    }

    // Escape key closes modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closePatientDetails();
      }
    });

    // Search Report Input
    const searchForm = document.getElementById('report-search-form');
    const searchInput = document.getElementById('search-mrno-input') as HTMLInputElement | null;
    if (searchForm && searchInput) {
      searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.searchReport(searchInput.value);
      });

      searchInput.addEventListener('input', () => {
        if (searchInput.value.trim().length >= 3) {
          this.searchReport(searchInput.value);
        }
      });
    }
  }

  private handleUrlHash(): void {
    const hash = window.location.hash.replace('#', '') as DashboardTab;
    if (['patients', 'patient-status', 'reports', 'profile'].includes(hash)) {
      this.switchTab(hash);
    }
  }
}

// Instantiate on DOMContentLoaded or immediately if already ready
let appInstance: DoctorDashboardApp | null = null;
function initDoctorDashboardApp(): DoctorDashboardApp {
  if (!appInstance) {
    appInstance = new DoctorDashboardApp();
    (window as any).openPatientDetails = (mrNo: string) => appInstance?.openPatientDetails(mrNo);
    (window as any).closePatientDetails = () => appInstance?.closePatientDetails();
  }
  return appInstance;
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initDoctorDashboardApp();
  });
} else {
  initDoctorDashboardApp();
}
