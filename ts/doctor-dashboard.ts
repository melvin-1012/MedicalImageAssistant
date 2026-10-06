/**
 * MediSight AI - Doctor Dashboard Logic (TypeScript Source)
 * Clinical Decision-Support System - Doctor Workspace
 */

export interface TeamDoctor {
  id: string;
  name: string;
  credentials: string;
  role: string;
  department: string;
  specialization: string;
  licenseNo: string;
  experienceYears: number;
  avatarText: string;
  email: string;
}

export interface PatientRecord {
  mrNo: string;
  name: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  symptoms: string;
  clinicalNotes: string;
  investigationStatus: string;
  assignedSpecialist: string;
  aiAnalysisStatus: string;
  status: 'Pending' | 'Completed';
}

export interface DiagnosticReport {
  mrNo: string;
  patientName: string;
  age: number;
  gender: string;
  investigationType: string;
  modality?: 'XRay' | 'CT Scan' | 'MRI' | string;
  aiPreliminaryReportStatus: string;
  doctorReviewStatus: string;
  finalReportStatus: string;
  aiFindings: string;
  confidence: string;
  evidenceExplanation: string;
  doctorConclusion: string;
  medications: string;
  recommendations?: string;
  additionalNotes?: string;
  reviewedBy?: string;
  isApproved: boolean;
  isFinalSent?: boolean;
  approvalTimestamp?: string;
}

export type DashboardTab = 'patients' | 'patient-status' | 'reports' | 'profile';

export class DoctorDashboardApp {
  private activeTab: DashboardTab = 'patients';
  private patients: PatientRecord[] = [];
  private reports: Record<string, DiagnosticReport> = {};
  private selectedPatientMrNo: string = 'MR001';

  public teamDoctors: TeamDoctor[] = [
    {
      id: 'doc-joison',
      name: 'Dr. Joison',
      credentials: 'MD (Radiology), FRCR',
      role: 'Chief Medical Officer & Consultant Radiologist',
      department: 'Division of Diagnostic Imaging & Thoracic Medicine',
      specialization: 'AI-Assisted Thoracic CT/X-Ray Interpretation, Cross-Modal Imaging Diagnostics',
      licenseNo: 'MED-REG-84920-KA',
      experienceYears: 16,
      avatarText: 'DJ',
      email: 'dr.joison@medisight.health'
    },
    {
      id: 'doc-melvin',
      name: 'Dr. Melvin',
      credentials: 'MD (Pulmonology), FCCP',
      role: 'Consultant Pulmonologist & Critical Care Specialist',
      department: 'Division of Pulmonary & Respiratory Medicine',
      specialization: 'High-Resolution Chest CT, Chronic Obstructive Airway Disease, Interventional Bronchoscopy',
      licenseNo: 'MED-REG-91042-KA',
      experienceYears: 14,
      avatarText: 'DM',
      email: 'dr.melvin@medisight.health'
    },
    {
      id: 'doc-joseph',
      name: 'Dr. Joseph',
      credentials: 'MD, DM (Cardiology), FACC',
      role: 'Consultant Cardiologist & Cardiovascular Imaging Lead',
      department: 'Division of Cardiovascular Medicine & Triage',
      specialization: 'Cardiothoracic Ratio Radiomics, Multimodal Echocardiography, Ischemic Risk Stratification',
      licenseNo: 'MED-REG-77419-KA',
      experienceYears: 15,
      avatarText: 'DJ',
      email: 'dr.joseph@medisight.health'
    },
    {
      id: 'doc-ilakkiya',
      name: 'Dr. Ilakkiya',
      credentials: 'MD (Radiodiagnosis), PhD (Clinical AI)',
      role: 'Consultant Diagnostic AI & Imaging Specialist',
      department: 'Division of Multimodal Medical Intelligence & Triage',
      specialization: 'Deep Learning ROI Localization, Neural Radiomics, Explainable Clinical Decision Support',
      licenseNo: 'MED-REG-63851-KA',
      experienceYears: 12,
      avatarText: 'DI',
      email: 'dr.ilakkiya@medisight.health'
    }
  ];

  constructor() {
    this.init();
  }

  private loadPatients(): PatientRecord[] {
    try {
      const stored = localStorage.getItem('medisight_patients');
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return [
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
  }

  private savePatients(data: PatientRecord[]): void {
    try {
      localStorage.setItem('medisight_patients', JSON.stringify(data));
    } catch (e) {}
  }

  private loadReports(): Record<string, DiagnosticReport> {
    try {
      const stored = localStorage.getItem('medisight_reports');
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return {
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
  }

  private saveReports(data: Record<string, DiagnosticReport>): void {
    try {
      localStorage.setItem('medisight_reports', JSON.stringify(data));
    } catch (e) {}
  }

  private init(): void {
    this.patients = this.loadPatients();
    this.reports = this.loadReports();

    const params = new URLSearchParams(window.location.search);
    const paramMrNo = params.get('mrNo');
    const paramView = params.get('view') as DashboardTab | null;
    if (paramMrNo && this.reports[paramMrNo]) {
      this.selectedPatientMrNo = paramMrNo;
    }

    this.renderPatientsTable();
    this.renderPatientStatusTable();
    this.renderReportView(this.selectedPatientMrNo);
    this.renderDoctorProfile();
    this.bindEvents();
    this.handleUrlHash();

    if (paramView) {
      this.switchTab(paramView);
    }
  }

  public switchTab(tabId: DashboardTab): void {
    this.activeTab = tabId;

    document.querySelectorAll('.dash-nav-tab').forEach((tab) => {
      if (tab.getAttribute('data-tab') === tabId) {
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
      } else {
        tab.classList.remove('active');
        tab.setAttribute('aria-selected', 'false');
      }
    });

    document.querySelectorAll('.dash-view-panel').forEach((panel) => {
      if (panel.id === `view-${tabId}`) {
        panel.classList.add('active');
      } else {
        panel.classList.remove('active');
      }
    });

    this.patients = this.loadPatients();
    this.reports = this.loadReports();

    if (tabId === 'patients') {
      this.renderPatientsTable();
    } else if (tabId === 'patient-status') {
      this.renderPatientStatusTable();
    } else if (tabId === 'reports') {
      this.renderReportView(this.selectedPatientMrNo);
    } else if (tabId === 'profile') {
      this.renderDoctorProfile();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

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
          <div class="patient-actions-group">
            <button type="button" class="btn btn-outline-primary btn-sm btn-view-patient" data-mrno="${p.mrNo}">View</button>
            <a href="specialist-imaging.html?mrNo=${p.mrNo}" class="btn btn-teal btn-sm btn-refer-specialist-link" data-mrno="${p.mrNo}" title="Refer ${p.name} to Specialist Imaging">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <polyline points="17 11 19 13 23 9"></polyline>
              </svg>
              Refer to Specialist
            </a>
          </div>
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

  public openPatientDetails(mrNo: string): void {
    const patient = this.patients.find(p => p.mrNo === mrNo);
    if (!patient) return;

    const modal = document.getElementById('patient-detail-modal');
    const container = document.getElementById('patient-detail-content');
    if (!modal || !container) return;

    const statusBadgeClass = patient.status === 'Completed' ? 'badge-success' : 'badge-warning';

    container.innerHTML = `
      <div class="patient-detail-card">
        <div class="detail-header-strip">
          <div>
            <span class="badge badge-primary font-mono">${patient.mrNo}</span>
            <h3 class="detail-title">${patient.name}</h3>
            <p class="detail-sub">${patient.age} yrs • ${patient.gender}</p>
          </div>
          <span class="badge ${statusBadgeClass}">${patient.status}</span>
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
          <a href="specialist-imaging.html?mrNo=${patient.mrNo}" class="btn btn-teal btn-refer-specialist" data-mrno="${patient.mrNo}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <polyline points="17 11 19 13 23 9"></polyline>
            </svg>
            Refer to Specialist
          </a>
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

  private renderPatientStatusTable(): void {
    const tbody = document.getElementById('patient-status-tbody');
    if (!tbody) return;

    this.patients = this.loadPatients();

    tbody.innerHTML = this.patients.map((p) => {
      const isCompleted = p.status === 'Completed';
      const statusClass = isCompleted ? 'badge-success' : 'badge-warning';

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
            <span class="badge ${statusClass}">
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
              <span class="text-muted text-sm font-medium">Pending Analysis</span>
            `}
          </td>
        </tr>
      `;
    }).join('');
  }

  public renderReportView(mrNo: string): void {
    this.selectedPatientMrNo = mrNo;
    this.reports = this.loadReports();
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

    document.querySelectorAll('.mr-quick-btn').forEach((btn) => {
      if (btn.getAttribute('data-mrno') === mrNo) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    const statusPill = report.isFinalSent
      ? '<span class="text-success font-semibold">FINAL REPORT TRANSMITTED TO PATIENT</span>'
      : (report.isApproved
          ? '<span class="text-success font-semibold">APPROVED BY PHYSICIAN</span>'
          : '<span class="text-warning font-semibold">PRELIMINARY REVIEW</span>');

    const finalBadge = report.isFinalSent ? 'badge-success' : (report.isApproved ? 'badge-teal' : 'badge-warning');
    const reviewerDoctor = report.reviewedBy || 'Dr. Joison, MD';

    container.innerHTML = `
      <div class="clinical-report-sheet">
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
            <div class="text-xs text-muted">Status: ${statusPill}</div>
          </div>
        </div>

        <div class="clinical-safety-alert-banner" role="alert">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2" style="flex-shrink: 0; margin-top: 2px;">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <div>
            <strong>AI Preliminary Analysis – Requires Physician Review</strong>
            <p class="mb-0 text-sm">
              This report contains assistive multimodal imaging observations. AI findings are non-definitive clinical decision-support markers and do not replace professional physician diagnosis or clinical judgment.
            </p>
          </div>
        </div>

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
            <span class="meta-label">Investigation Modality</span>
            <span class="meta-value font-semibold text-primary">${report.modality ? report.modality + ' • ' : ''}${report.investigationType}</span>
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
              <span class="badge ${finalBadge}">${report.isFinalSent ? 'Final Report Transmitted to Patient' : report.finalReportStatus}</span>
            </span>
          </div>
        </div>

        <!-- SECTION: AI / IMAGING ANALYSIS -->
        <div style="margin-top: 1.25rem;">
          <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--color-primary-dark); margin: 0 0 0.85rem 0; display: flex; align-items: center; gap: 0.5rem;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"></circle><path d="m4.93 4.93 4.24 4.24"></path><path d="m14.83 9.17 4.24-4.24"></path><path d="m14.83 14.83 4.24 4.24"></path><path d="m9.17 14.83-4.24 4.24"></path></svg>
            AI / Imaging Analysis
          </h3>

          <div class="report-section-block">
            <h4 class="report-section-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              AI Observations &amp; Confidence Calibration
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
              Multimodal Evidence &amp; Explainable Radiomics
            </h4>
            <div class="report-text-box">${report.evidenceExplanation}</div>
          </div>
        </div>

        <!-- SECTION: DOCTOR'S FINAL REVIEW -->
        <div class="review-section-divider">
          <span>Doctor's Final Review &bull; Physician Sign-Off</span>
        </div>

        <div class="doctor-review-form" style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: var(--radius-lg); padding: 1.5rem;">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span class="badge badge-primary font-mono text-xs">Attending Physician: ${reviewerDoctor}</span>
            <span class="badge badge-warning text-xs">Physician Final Decision Authority</span>
          </div>

          <div class="doctor-review-group">
            <label class="doctor-review-label" for="doctor-conclusion-field">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
              1. Doctor Conclusion <span class="required-star">*</span>
            </label>
            <textarea class="doctor-review-textarea" id="doctor-conclusion-field" rows="3" placeholder="Enter clinical diagnosis and physician conclusion...">${report.doctorConclusion || ''}</textarea>
          </div>

          <div class="doctor-review-group">
            <label class="doctor-review-label" for="doctor-medications-field">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
              2. Prescribed Medications &amp; Dosage <span class="required-star">*</span>
            </label>
            <textarea class="doctor-review-textarea" id="doctor-medications-field" rows="2" placeholder="Enter medications and prescription details...">${report.medications || ''}</textarea>
          </div>

          <div class="doctor-review-group">
            <label class="doctor-review-label" for="doctor-recommendations-field">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
              3. Clinical Recommendations
            </label>
            <textarea class="doctor-review-textarea" id="doctor-recommendations-field" rows="2" placeholder="Enter follow-up investigations, dietary advice, lifestyle recommendations...">${report.recommendations || 'Regular monitoring of vitals; schedule repeat clinical check in 2 weeks.'}</textarea>
          </div>

          <div class="doctor-review-group">
            <label class="doctor-review-label" for="doctor-notes-field">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
              4. Additional Clinical Notes
            </label>
            <textarea class="doctor-review-textarea" id="doctor-notes-field" rows="2" placeholder="Enter additional clinical notes for patient records...">${report.additionalNotes || 'Patient educated on early warning symptoms and emergency contact details provided.'}</textarea>
          </div>
        </div>

        <div class="report-footer-actions">
          <div class="report-approval-meta">
            ${report.isFinalSent ? `
              <span class="text-success font-semibold flex items-center gap-1">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Final report successfully sent to patient (${report.approvalTimestamp || 'Transmitted'})
              </span>
            ` : `
              <span class="text-muted text-sm">
                Doctor is the final decision-maker. Review all fields before sending final report to patient.
              </span>
            `}
          </div>

          <div>
            <button type="button" class="btn btn-primary btn-lg" id="btn-send-final-report" data-mrno="${report.mrNo}">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
              ${report.isFinalSent ? ' Update & Re-send Final Report' : ' Send Final Report to Patient'}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  public sendFinalReportToPatient(mrNo: string): void {
    this.reports = this.loadReports();
    const report = this.reports[mrNo];
    if (!report) return;

    const conclusionEl = document.getElementById('doctor-conclusion-field') as HTMLTextAreaElement | null;
    const medsEl = document.getElementById('doctor-medications-field') as HTMLTextAreaElement | null;
    const recsEl = document.getElementById('doctor-recommendations-field') as HTMLTextAreaElement | null;
    const notesEl = document.getElementById('doctor-notes-field') as HTMLTextAreaElement | null;

    if (conclusionEl) report.doctorConclusion = conclusionEl.value.trim();
    if (medsEl) report.medications = medsEl.value.trim();
    if (recsEl) report.recommendations = recsEl.value.trim();
    if (notesEl) report.additionalNotes = notesEl.value.trim();

    report.isApproved = true;
    report.isFinalSent = true;
    report.doctorReviewStatus = 'Reviewed & Signed by Dr. Joison';
    report.finalReportStatus = 'Final Report Transmitted to Patient';
    report.approvalTimestamp = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST';

    this.patients = this.loadPatients();
    const patient = this.patients.find(p => p.mrNo === mrNo);
    if (patient) {
      patient.status = 'Completed';
    }

    this.saveReports(this.reports);
    this.savePatients(this.patients);

    this.showToast(
      'Report Sent',
      'Final report sent to patient.',
      'success'
    );

    this.renderReportView(mrNo);
    this.renderPatientStatusTable();
  }

  public searchReport(query: string): void {
    const trimmed = (query || '').trim().toUpperCase();
    if (!trimmed) return;

    this.reports = this.loadReports();
    this.patients = this.loadPatients();

    let matchedMrNo = '';
    if (this.reports[trimmed]) {
      matchedMrNo = trimmed;
    } else {
      const patient = this.patients.find(p =>
        p.mrNo.toUpperCase().includes(trimmed) || p.name.toUpperCase().includes(trimmed)
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

  private renderDoctorProfile(): void {
    const container = document.getElementById('doctor-profile-container');
    if (!container) return;

    container.innerHTML = `
      <div class="profile-card-wrapper" style="max-width: 1040px;">
        <div class="card-table-header" style="background: #ffffff; padding: 1.5rem 1.75rem; border-radius: var(--radius-xl); border: 1px solid var(--color-border); box-shadow: var(--shadow-sm);">
          <div>
            <h2 class="table-header-title" id="heading-doctor-profile">MediSight AI Clinical Doctor Team</h2>
            <p class="table-header-sub">Board-certified clinical specialists and diagnostic AI review panel for MediSight Hospital.</p>
          </div>
          <span class="badge badge-teal">4 Attending Physicians Active</span>
        </div>

        <div class="team-doctors-grid">
          ${this.teamDoctors.map(doc => `
            <div class="team-doctor-card">
              <div class="team-doctor-header">
                <div class="team-doctor-avatar">${doc.avatarText}</div>
                <div class="team-doctor-info">
                  <h3 class="team-doctor-name">${doc.name}, MD</h3>
                  <span class="team-doctor-role">${doc.role}</span>
                  <span class="team-doctor-dept">${doc.department}</span>
                </div>
              </div>
              <div class="team-doctor-details">
                <div class="team-doctor-detail-row">
                  <span class="team-doctor-detail-label">License</span>
                  <span class="team-doctor-detail-val font-mono text-primary">${doc.licenseNo}</span>
                </div>
                <div class="team-doctor-detail-row">
                  <span class="team-doctor-detail-label">Experience</span>
                  <span class="team-doctor-detail-val">${doc.experienceYears} Years Clinical Practice</span>
                </div>
                <div class="team-doctor-detail-row">
                  <span class="team-doctor-detail-label">Contact</span>
                  <span class="team-doctor-detail-val text-xs">${doc.email}</span>
                </div>
              </div>
              <p class="team-doctor-specialization">${doc.specialization}</p>
              <div class="team-doctor-badge-strip">
                <span class="badge badge-success"><span class="badge-dot"></span>Attending Physician</span>
                <span class="badge badge-subtle font-mono text-xs">MediSight AI</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  public handleLogout(): void {
    this.showToast(
      'Doctor Session Concluded',
      'MediSight AI doctor workspace session ended. Returning to landing page...',
      'info'
    );

    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1200);
  }

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

  private bindEvents(): void {
    document.querySelectorAll('.dash-nav-tab').forEach((tab) => {
      tab.addEventListener('click', (e) => {
        e.preventDefault();
        const targetTab = tab.getAttribute('data-tab') as DashboardTab | null;
        if (targetTab) {
          this.switchTab(targetTab);
          window.location.hash = targetTab;
        }
      });
    });

    document.querySelectorAll('.btn-doctor-logout').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleLogout();
      });
    });

    const mobileToggle = document.getElementById('doctor-mobile-toggle');
    const mobilePanel = document.getElementById('doctor-mobile-panel');
    if (mobileToggle && mobilePanel) {
      mobileToggle.addEventListener('click', () => {
        const isOpen = mobilePanel.classList.toggle('is-open');
        mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });

      mobilePanel.querySelectorAll('.mobile-nav-link').forEach((link) => {
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

    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement | null;
      if (!target) return;

      const viewBtn = target.closest('.btn-view-patient');
      if (viewBtn) {
        const mrNo = viewBtn.getAttribute('data-mrno');
        if (mrNo) this.openPatientDetails(mrNo);
        return;
      }

      if (target.id === 'btn-close-detail' || target.closest('#btn-close-detail')) {
        this.closePatientDetails();
        return;
      }

      const statusReportBtn = target.closest('.btn-status-view-report');
      if (statusReportBtn) {
        const mrNo = statusReportBtn.getAttribute('data-mrno');
        if (mrNo) {
          this.switchTab('reports');
          window.location.hash = 'reports';
          this.renderReportView(mrNo);
          const searchInput = document.getElementById('search-mrno-input') as HTMLInputElement | null;
          if (searchInput) searchInput.value = mrNo;
        }
        return;
      }

      const sendReportBtn = target.closest('#btn-send-final-report');
      if (sendReportBtn) {
        const mrNo = sendReportBtn.getAttribute('data-mrno');
        if (mrNo) this.sendFinalReportToPatient(mrNo);
        return;
      }

      const quickBtn = target.closest('.mr-quick-btn');
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

    const detailModal = document.getElementById('patient-detail-modal');
    if (detailModal) {
      detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) {
          this.closePatientDetails();
        }
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closePatientDetails();
      }
    });

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

    window.addEventListener('storage', () => {
      this.patients = this.loadPatients();
      this.reports = this.loadReports();
      this.renderPatientsTable();
      this.renderPatientStatusTable();
      this.renderReportView(this.selectedPatientMrNo);
    });

    window.addEventListener('focus', () => {
      this.patients = this.loadPatients();
      this.reports = this.loadReports();
      this.renderPatientStatusTable();
      if (this.activeTab === 'reports') {
        this.renderReportView(this.selectedPatientMrNo);
      }
    });
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
    (window as any).sendFinalReportToPatient = (mrNo: string) => appInstance?.sendFinalReportToPatient(mrNo);
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
