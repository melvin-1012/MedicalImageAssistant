/**
 * MediSight AI - Patient Dashboard Logic (Runtime JavaScript)
 * Realistic hospital patient information portal.
 * Zero-dependency, runs natively in all browsers and with file:// or HTTP.
 */

(function () {
  'use strict';

  // ============================================================================
  // Mock Patient Data Store
  // ============================================================================

  const defaultProfile = {
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
    knownAllergies: 'Penicillin (Mild urticaria), Dust mites',
    chronicConditions: 'Borderline Hypertension'
  };

  const defaultAppointments = [
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

  const defaultMedicalRecords = [
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

  const defaultInvestigations = [
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

  const defaultNotifications = [
    {
      id: 'notif-1',
      title: 'Your final medical report is available.',
      message: 'Dr. Joison, MD has completed and approved your Digital Chest Radiography report with conclusion and prescribed medications.',
      timestamp: 'Today &bull; 14:45 IST',
      isRead: false,
      type: 'report'
    },
    {
      id: 'notif-2',
      title: 'Your investigation report is now available.',
      message: 'Digital Chest Radiography (PA View) scan and preliminary imaging analysis have been uploaded to your medical records.',
      timestamp: 'Today &bull; 11:20 IST',
      isRead: false,
      type: 'investigation'
    },
    {
      id: 'notif-3',
      title: 'Your appointment has been confirmed.',
      message: 'Follow-up clinical consultation with Dr. Joison, MD is scheduled for Oct 12, 2026 at 10:30 AM in OPD Room 204.',
      timestamp: 'Yesterday &bull; 16:30 IST',
      isRead: true,
      type: 'appointment'
    },
    {
      id: 'notif-4',
      title: 'Your doctor has reviewed your report.',
      message: 'Dr. Joseph (Cardiology) reviewed your clinical records and recommended scheduling a 2D Echocardiogram evaluation.',
      timestamp: 'Oct 05, 2026 &bull; 11:00 IST',
      isRead: true,
      type: 'general'
    }
  ];

  // Helper: Load doctor-approved report from doctor dashboard localStorage if available
  function getApprovedReportData() {
    let report = null;
    try {
      const stored = localStorage.getItem('medisight_reports');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed['MR001']) {
          report = parsed['MR001'];
        }
      }
    } catch (e) {}

    return {
      mrNo: 'MR001',
      patientName: 'Arun Kumar',
      age: 45,
      gender: 'Male',
      investigation: report && report.investigationType ? report.investigationType : 'Digital Chest Radiography (PA View)',
      modality: report && report.modality ? report.modality : 'XRay',
      date: 'Oct 06, 2026',
      aiAnalysisFindings: (report && report.aiFindings) || 'Possible mild cardiomegaly with subtle perihilar vascular prominence. No acute pneumothorax or focal consolidations detected.',
      aiConfidence: (report && report.confidence) || 'Confidence: 86% (Calibrated Bayesian Metric)',
      supportingEvidence: (report && report.evidenceExplanation) || 'Cardiothoracic ratio calculated at ~0.52. Localized subtle vascular prominence identified in bilateral perihilar regions.',
      doctorConclusion: (report && report.doctorConclusion) || 'Clinical findings suggestive of early hypertensive cardiac strain. Borderline cardiothoracic ratio (0.52). 2D Echocardiogram with Doppler recommended within 48 hours to evaluate left ventricular function.',
      medications: (report && report.medications) || 'Tab. Amlodipine 5mg OD (morning), Tab. Aspirin 75mg OD (post-meal), Tab. Sorbitrate 5mg SL PRN for acute chest discomfort.',
      recommendations: (report && report.recommendations) || 'Low sodium cardiac diet, avoid intense strenuous physical exertion pending echocardiogram, maintain daily blood pressure log, report to emergency immediately if chest pain radiates to arm/jaw or exceeds 15 minutes.',
      reviewingDoctor: (report && report.reviewedBy) ? report.reviewedBy + ', MD' : 'Dr. Joison, MD',
      doctorLicense: 'License: MED-REG-84920-KA',
      status: 'Doctor Approved',
      approvalDate: (report && report.approvalTimestamp) || 'Oct 06, 2026 14:30 IST'
    };
  }

  // State Management with LocalStorage
  let currentProfile = defaultProfile;
  let appointmentsList = defaultAppointments;
  let notificationsList = defaultNotifications;
  let activeTab = 'dashboard';

  function init() {
    loadProfileFromStorage();
    renderAllViews();
    bindEvents();
    handleUrlHash();
  }

  function loadProfileFromStorage() {
    try {
      const stored = localStorage.getItem('medisight_patient_profile');
      if (stored) {
        currentProfile = Object.assign({}, defaultProfile, JSON.parse(stored));
      }
    } catch (e) {}
  }

  function saveProfileToStorage() {
    try {
      localStorage.setItem('medisight_patient_profile', JSON.stringify(currentProfile));
    } catch (e) {}
  }

  function renderAllViews() {
    renderProfileView();
    renderAppointmentsView();
    renderMedicalRecordsView();
    renderInvestigationsView();
    renderReportsView();
    renderNotificationsView();
    updateUnreadBadges();
  }

  // ============================================================================
  // Tab Switching
  // ============================================================================
  function switchTab(tabId) {
    activeTab = tabId;

    // Update Nav Links & Tab Buttons
    document.querySelectorAll('.patient-nav-link, .patient-tab-btn, .mobile-nav-link').forEach(function (el) {
      if (el.getAttribute('data-tab') === tabId) {
        el.classList.add('active');
        el.setAttribute('aria-selected', 'true');
      } else {
        el.classList.remove('active');
        el.setAttribute('aria-selected', 'false');
      }
    });

    // Update View Panels
    document.querySelectorAll('.patient-view-panel').forEach(function (panel) {
      if (panel.id === 'view-' + tabId) {
        panel.classList.add('active');
      } else {
        panel.classList.remove('active');
      }
    });

    if (tabId === 'reports') {
      renderReportsView();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function handleUrlHash() {
    const hash = window.location.hash.replace('#', '');
    const validTabs = ['dashboard', 'profile', 'appointments', 'medical-records', 'investigations', 'reports', 'notifications'];
    if (validTabs.indexOf(hash) !== -1) {
      switchTab(hash);
    }
  }

  // ============================================================================
  // 1. Render Profile
  // ============================================================================
  function renderProfileView() {
    const p = currentProfile;
    const nameEl = document.getElementById('welcome-patient-name');
    const navNameEl = document.getElementById('nav-patient-name');
    const profNameEl = document.getElementById('profile-display-name');
    const profMrnoEl = document.getElementById('profile-display-mrno');
    const profAgeGenderEl = document.getElementById('profile-display-age-gender');

    if (nameEl) nameEl.textContent = p.name;
    if (navNameEl) navNameEl.textContent = p.name;
    if (profNameEl) profNameEl.textContent = p.name;
    if (profMrnoEl) profMrnoEl.textContent = p.mrNo;
    if (profAgeGenderEl) profAgeGenderEl.textContent = p.age + ' Years • ' + p.gender;

    const valMrno = document.getElementById('prof-val-mrno');
    const valName = document.getElementById('prof-val-name');
    const valAgeGender = document.getElementById('prof-val-age-gender');
    const valBlood = document.getElementById('prof-val-blood');
    const valPhone = document.getElementById('prof-val-phone');
    const valEmail = document.getElementById('prof-val-email');
    const valEmergency = document.getElementById('prof-val-emergency');
    const valAddress = document.getElementById('prof-val-address');

    if (valMrno) valMrno.textContent = p.mrNo;
    if (valName) valName.textContent = p.name;
    if (valAgeGender) valAgeGender.textContent = p.age + ' / ' + p.gender;
    if (valBlood) valBlood.textContent = p.bloodGroup;
    if (valPhone) valPhone.textContent = p.phone;
    if (valEmail) valEmail.textContent = p.email;
    if (valEmergency) valEmergency.textContent = p.emergencyContact;
    if (valAddress) valAddress.textContent = p.address;
  }

  // ============================================================================
  // 2. Render Appointments
  // ============================================================================
  function renderAppointmentsView() {
    const container = document.getElementById('appointments-list-container');
    if (!container) return;

    container.innerHTML = appointmentsList.map(function (apt) {
      let badgeClass = 'badge-primary';
      if (apt.status === 'Completed') badgeClass = 'badge-success';
      if (apt.status === 'Cancelled') badgeClass = 'badge-subtle';

      return (
        '<div class="appointment-card">' +
          '<div class="appointment-card-top">' +
            '<div>' +
              '<h3 class="appointment-doctor-name">' + apt.doctor + '</h3>' +
              '<span class="appointment-dept">' + apt.department + '</span>' +
            '</div>' +
            '<span class="badge ' + badgeClass + '">' +
              '<span class="badge-dot"></span>' + apt.status +
            '</span>' +
          '</div>' +
          '<div style="display: flex; flex-direction: column; gap: 0.35rem;">' +
            '<div class="appointment-meta-row">' +
              '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>' +
              '<strong class="text-main">' + apt.date + '</strong> at <span class="font-mono">' + apt.time + '</span>' +
            '</div>' +
            (apt.room ? (
              '<div class="appointment-meta-row text-xs">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>' +
                apt.room +
              '</div>'
            ) : '') +
          '</div>' +
          '<div class="text-xs text-muted" style="background: #f8fafc; padding: 0.6rem 0.75rem; border-radius: var(--radius-md); border: 1px solid #e2e8f0;">' +
            '<strong>Reason:</strong> ' + apt.reason +
          '</div>' +
          '<div style="display: flex; justify-content: flex-end; gap: 0.5rem; border-top: 1px solid #f1f5f9; padding-top: 0.75rem;">' +
            (apt.status === 'Upcoming' ? (
              '<button type="button" class="btn btn-outline btn-xs" onclick="window.showPatientToast && window.showPatientToast(\'Appointment Notice\', \'To reschedule or cancel this hospital visit, please contact the OPD desk at extension 204.\', \'info\')">' +
                'Reschedule' +
              '</button>'
            ) : '') +
            '<button type="button" class="btn btn-primary btn-xs" onclick="window.showPatientToast && window.showPatientToast(\'Appointment Confirmed\', \'Status: ' + apt.status + ' with ' + apt.doctor + ' on ' + apt.date + '\', \'success\')">' +
              'Details' +
            '</button>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  // ============================================================================
  // 3. Render Medical Records
  // ============================================================================
  function renderMedicalRecordsView() {
    const container = document.getElementById('medical-records-list-container');
    if (!container) return;

    container.innerHTML = defaultMedicalRecords.map(function (rec) {
      return (
        '<div class="medical-record-card">' +
          '<div class="medical-record-header">' +
            '<div>' +
              '<h3 style="font-size: 1.1rem; font-weight: 700; color: var(--color-text-main); margin: 0 0 0.2rem 0;">' + rec.title + '</h3>' +
              '<div class="text-xs text-muted">' +
                'Consulting Physician: <strong class="text-primary">' + rec.doctor + '</strong> &bull; ' + rec.department +
              '</div>' +
            '</div>' +
            '<div style="text-align: right;">' +
              '<span class="badge badge-subtle font-mono">' + rec.date + '</span>' +
            '</div>' +
          '</div>' +
          '<div class="medical-record-body">' +
            '<div>' +
              '<span class="text-xs font-bold text-muted uppercase">Physician Diagnosis &amp; Clinical Synthesis</span>' +
              '<p class="text-sm text-main" style="margin: 0.35rem 0 0.75rem 0; line-height: 1.55;">' + rec.diagnosisNotes + '</p>' +
              '<span class="text-xs font-bold text-muted uppercase">Prescribed Medications</span>' +
              '<div class="report-meds-box" style="margin-top: 0.35rem; font-size: 0.85rem; padding: 0.6rem 0.85rem;">' + rec.prescriptions + '</div>' +
            '</div>' +
            '<div style="display: flex; flex-direction: column; justify-content: space-between; gap: 0.75rem; background: #f8fafc; padding: 1rem; border-radius: var(--radius-md); border: 1px solid #e2e8f0;">' +
              '<div>' +
                '<span class="text-xs font-bold text-muted uppercase">Medical History</span>' +
                '<p class="text-xs text-muted" style="margin: 0.25rem 0 0 0;">' + rec.previousHistory + '</p>' +
              '</div>' +
              '<button type="button" class="btn btn-outline-primary btn-sm btn-view-single-record" data-recid="' + rec.id + '" style="width: 100%;">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="10" r="3"></circle></svg>' +
                ' View Full Record' +
              '</button>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  // ============================================================================
  // 4. Render Investigations
  // ============================================================================
  function renderInvestigationsView() {
    const tbody = document.getElementById('investigations-tbody');
    if (!tbody) return;

    tbody.innerHTML = defaultInvestigations.map(function (inv) {
      let badgeClass = 'badge-subtle';
      if (inv.status === 'Completed') badgeClass = 'badge-success';
      if (inv.status === 'In Progress') badgeClass = 'badge-warning';

      return (
        '<tr>' +
          '<td>' +
            '<div style="font-weight: 700; color: var(--color-text-main);">' + inv.name + '</div>' +
            '<span class="badge badge-subtle font-mono text-xs">' + inv.modality + '</span>' +
          '</td>' +
          '<td class="font-mono text-primary font-bold">' + inv.mrNo + '</td>' +
          '<td>' + inv.requestedBy + '</td>' +
          '<td class="font-mono text-sm">' + inv.date + '</td>' +
          '<td>' +
            '<span class="badge ' + badgeClass + '">' +
              '<span class="badge-dot"></span>' + inv.status +
            '</span>' +
          '</td>' +
          '<td class="text-right">' +
            (inv.status === 'Completed' ? (
              '<button type="button" class="btn btn-primary btn-sm btn-inv-view-result">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>' +
                ' View Result' +
              '</button>'
            ) : (
              '<span class="text-muted text-xs font-semibold uppercase">' + inv.status + '</span>'
            )) +
          '</td>' +
        '</tr>'
      );
    }).join('');
  }

  // ============================================================================
  // 5. Render Reports (Doctor-Approved Final Reports)
  // ============================================================================
  function renderReportsView(searchQuery) {
    const reportData = getApprovedReportData();
    const listContainer = document.getElementById('patient-reports-list');
    const viewerContainer = document.getElementById('patient-report-viewer-wrapper');
    if (!listContainer || !viewerContainer) return;

    const query = (searchQuery || '').trim().toLowerCase();

    // Check if matches search
    const matches = !query ||
      reportData.mrNo.toLowerCase().indexOf(query) !== -1 ||
      reportData.investigation.toLowerCase().indexOf(query) !== -1 ||
      reportData.patientName.toLowerCase().indexOf(query) !== -1;

    if (!matches) {
      listContainer.innerHTML = (
        '<div class="empty-report-state">' +
          '<h3>No matching reports found</h3>' +
          '<p>Try searching for <strong>MR001</strong> or <strong>Chest X-Ray</strong>.</p>' +
        '</div>'
      );
      viewerContainer.innerHTML = '';
      return;
    }

    // Render Report Summary Card in List
    listContainer.innerHTML = (
      '<div class="patient-report-card">' +
        '<div>' +
          '<div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.35rem;">' +
            '<span class="badge badge-primary font-mono text-xs">MR001</span>' +
            '<span class="report-doctor-approved-seal">' +
              '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>' +
              'Doctor Approved Final Report' +
            '</span>' +
          '</div>' +
          '<h3 style="font-size: 1.25rem; font-weight: 700; color: var(--color-text-main); margin: 0 0 0.25rem 0;">' +
            reportData.investigation + ' Report' +
          '</h3>' +
          '<p class="text-xs text-muted mb-0">' +
            'Attending Physician: <strong class="text-primary">' + reportData.reviewingDoctor + '</strong> &bull; ' + reportData.approvalDate +
          '</p>' +
        '</div>' +
        '<div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">' +
          '<button type="button" class="btn btn-outline-primary btn-sm" id="btn-patient-print-report" onclick="window.print()">' +
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>' +
            ' Download Report' +
          '</button>' +
          '<button type="button" class="btn btn-primary btn-sm" id="btn-patient-view-modal">' +
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>' +
            ' View Report' +
          '</button>' +
        '</div>' +
      '</div>'
    );

    // Render Full Inline PDF Viewer Sheet
    viewerContainer.innerHTML = buildReportHtml(reportData, false);
  }

  // Builder for Report Viewer Sheet
  function buildReportHtml(report, isModal) {
    return (
      '<div class="clinical-report-sheet" style="' + (isModal ? 'padding: 2rem; border-radius: var(--radius-xl);' : '') + '">' +
        
        // Letterhead
        '<div class="report-letterhead">' +
          '<div class="report-letterhead-left">' +
            '<div class="brand-group">' +
              '<div class="brand-logo" style="width: 32px; height: 32px;">' +
                '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">' +
                  '<path d="M12 2v20M2 12h20"></path>' +
                  '<circle cx="12" cy="12" r="5" stroke-width="1.8" stroke-dasharray="2 2"></circle>' +
                '</svg>' +
              '</div>' +
              '<div>' +
                '<div class="brand-name" style="font-size: 1.05rem;">MediSight <span>AI</span></div>' +
                '<div class="text-xs text-muted uppercase">Medical Investigation Report &bull; Hospital Record</div>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<div class="report-letterhead-right">' +
            '<div class="font-mono text-sm font-bold text-primary">REPORT REF: REP-' + report.mrNo + '-2026</div>' +
            '<div class="report-doctor-approved-seal" style="margin-top: 0.25rem;">' +
              '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>' +
              'DOCTOR APPROVED' +
            '</div>' +
          '</div>' +
        '</div>' +

        // Patient Demographics Grid
        '<div class="report-patient-meta-grid" style="margin-bottom: 1.25rem;">' +
          '<div class="meta-item">' +
            '<span class="meta-label">Patient Name</span>' +
            '<span class="meta-value font-bold">' + report.patientName + '</span>' +
          '</div>' +
          '<div class="meta-item">' +
            '<span class="meta-label">MR No</span>' +
            '<span class="meta-value font-mono font-bold text-primary">' + report.mrNo + '</span>' +
          '</div>' +
          '<div class="meta-item">' +
            '<span class="meta-label">Age / Gender</span>' +
            '<span class="meta-value">' + report.age + ' Y / ' + report.gender + '</span>' +
          '</div>' +
          '<div class="meta-item">' +
            '<span class="meta-label">Investigation</span>' +
            '<span class="meta-value font-semibold text-primary">' + report.investigation + '</span>' +
          '</div>' +
          '<div class="meta-item">' +
            '<span class="meta-label">Attending Reviewer</span>' +
            '<span class="meta-value font-medium">' + report.reviewingDoctor + '</span>' +
          '</div>' +
          '<div class="meta-item">' +
            '<span class="meta-label">Final Status</span>' +
            '<span class="meta-value"><span class="badge badge-success font-semibold">Doctor Approved &bull; Signed Off</span></span>' +
          '</div>' +
        '</div>' +

        // ==========================================
        // 1. AI / IMAGING ANALYSIS SECTION
        // ==========================================
        '<div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: var(--radius-lg); padding: 1.25rem; margin-bottom: 1.5rem;">' +
          '<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">' +
            '<h4 style="font-size: 0.95rem; font-weight: 700; color: var(--color-primary-dark); margin: 0; display: flex; align-items: center; gap: 0.4rem;">' +
              '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="m4.93 4.93 4.24 4.24"></path><path d="m14.83 9.17 4.24-4.24"></path></svg>' +
              'AI / Imaging Analysis' +
            '</h4>' +
            '<span class="badge badge-primary font-mono text-xs">' + report.aiConfidence + '</span>' +
          '</div>' +

          // Important AI Safety Notice
          '<div class="clinical-safety-alert-banner" style="margin-bottom: 0.85rem; padding: 0.75rem 1rem;">' +
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2" style="flex-shrink: 0; margin-top: 2px;">' +
              '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>' +
              '<line x1="12" y1="9" x2="12" y2="13"></line>' +
              '<line x1="12" y1="17" x2="12.01" y2="17"></line>' +
            '</svg>' +
            '<div>' +
              '<strong style="font-size: 0.85rem;">AI Preliminary Analysis – Requires Physician Review</strong>' +
              '<p class="mb-0 text-xs" style="color: #92400e; margin-top: 0.15rem;">' +
                'This section provides algorithmic computer-assisted imaging observations. Artificial intelligence findings are non-definitive observations, use cautious diagnostic phrasing (possible, suggestive of), and do not replace professional physician judgment.' +
              '</p>' +
            '</div>' +
          '</div>' +

          '<div style="margin-bottom: 0.75rem;">' +
            '<span class="text-xs font-bold text-muted uppercase">Algorithmic Observation</span>' +
            '<div style="background: #ffffff; border: 1px solid #bae6fd; border-radius: var(--radius-md); padding: 0.85rem 1rem; margin-top: 0.25rem; font-weight: 600; color: var(--color-text-main); font-size: 0.925rem;">' +
              '&ldquo;' + report.aiAnalysisFindings + '&rdquo;' +
            '</div>' +
          '</div>' +

          '<div>' +
            '<span class="text-xs font-bold text-muted uppercase">Supporting Evidence</span>' +
            '<div style="font-size: 0.85rem; color: var(--color-text-muted); margin-top: 0.25rem;">' +
              report.supportingEvidence +
            '</div>' +
          '</div>' +
        '</div>' +

        // Section Divider
        '<div class="review-section-divider">' +
          '<span>Doctor\'s Final Review &bull; Approved Prescription</span>' +
        '</div>' +

        // ==========================================
        // 2. DOCTOR'S FINAL REVIEW SECTION
        // ==========================================
        '<div style="background: #ffffff; border: 2px solid #22c55e; border-radius: var(--radius-lg); padding: 1.5rem; margin-bottom: 1.25rem; box-shadow: var(--shadow-sm);">' +
          '<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; border-bottom: 1px solid #f0fdf4; padding-bottom: 0.75rem;">' +
            '<div style="display: flex; align-items: center; gap: 0.5rem;">' +
              '<span class="report-doctor-approved-seal">' +
                '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>' +
                'Doctor Approved' +
              '</span>' +
              '<span class="text-xs text-muted">Reviewed by <strong>' + report.reviewingDoctor + '</strong></span>' +
            '</div>' +
            '<span class="text-xs font-mono text-muted">' + report.doctorLicense + '</span>' +
          '</div>' +

          // Doctor Conclusion
          '<div style="margin-bottom: 1rem;">' +
            '<span class="text-xs font-bold text-muted uppercase">Doctor\'s Clinical Conclusion</span>' +
            '<div class="report-text-box" style="margin-top: 0.35rem; font-weight: 500; color: var(--color-text-main); background: #f8fafc; border-left: 3px solid #16a34a;">' +
              report.doctorConclusion +
            '</div>' +
          '</div>' +

          // Prescribed Medications
          '<div style="margin-bottom: 1rem;">' +
            '<span class="text-xs font-bold text-muted uppercase">Prescribed Medications</span>' +
            '<div class="report-meds-box" style="margin-top: 0.35rem;">' +
              report.medications +
            '</div>' +
          '</div>' +

          // Recommendations
          '<div>' +
            '<span class="text-xs font-bold text-muted uppercase">Physician Recommendations &amp; Lifestyle Advice</span>' +
            '<div class="report-text-box" style="margin-top: 0.35rem; font-size: 0.875rem;">' +
              report.recommendations +
            '</div>' +
          '</div>' +
        '</div>' +

        // Report Footer Actions
        '<div class="report-footer-actions">' +
          '<div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: #15803d; font-weight: 600;">' +
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>' +
            'Official hospital document signed off by authorized attending medical personnel.' +
          '</div>' +
          '<div style="display: flex; gap: 0.75rem;">' +
            '<button type="button" class="btn btn-outline" onclick="window.print()">' +
              '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>' +
              ' Download / Print Report' +
            '</button>' +
            (isModal ? (
              '<button type="button" class="btn btn-primary" id="btn-close-report-modal-inside">Close Viewer</button>'
            ) : '') +
          '</div>' +
        '</div>' +

      '</div>'
    );
  }

  // ============================================================================
  // 6. Render Notifications
  // ============================================================================
  function renderNotificationsView() {
    const container = document.getElementById('notifications-list-container');
    if (!container) return;

    container.innerHTML = notificationsList.map(function (n) {
      const unreadClass = n.isRead ? 'read' : 'unread';
      return (
        '<div class="notification-item ' + unreadClass + '">' +
          '<div class="notification-dot"></div>' +
          '<div style="flex: 1;">' +
            '<div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;">' +
              '<h4 style="font-size: 0.95rem; font-weight: 700; color: var(--color-text-main); margin: 0 0 0.2rem 0;">' + n.title + '</h4>' +
              '<span class="text-xs font-mono text-muted">' + n.timestamp + '</span>' +
            '</div>' +
            '<p class="text-xs text-muted mb-0" style="line-height: 1.45;">' + n.message + '</p>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  function updateUnreadBadges() {
    const unreadCount = notificationsList.filter(function (n) { return !n.isRead; }).length;
    const navBadge = document.getElementById('nav-unread-badge');
    const tabBadge = document.getElementById('tab-unread-badge');

    if (navBadge) {
      navBadge.textContent = unreadCount;
      navBadge.style.display = unreadCount > 0 ? 'inline-block' : 'none';
    }
    if (tabBadge) {
      tabBadge.textContent = unreadCount;
      tabBadge.style.display = unreadCount > 0 ? 'inline-block' : 'none';
    }
  }

  function markAllNotificationsRead() {
    notificationsList.forEach(function (n) {
      n.isRead = true;
    });
    renderNotificationsView();
    updateUnreadBadges();
    showToast('Notifications Updated', 'All clinical notifications marked as read.', 'info');
  }

  // ============================================================================
  // Modals & User Actions
  // ============================================================================

  // Report Modal
  function openReportModal() {
    const modal = document.getElementById('modal-report-dialog');
    const container = document.getElementById('modal-report-dialog-content');
    if (!modal || !container) return;

    const report = getApprovedReportData();
    container.innerHTML = buildReportHtml(report, true);

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    const closeBtn = document.getElementById('btn-close-report-modal-inside');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeReportModal);
    }
  }

  function closeReportModal() {
    const modal = document.getElementById('modal-report-dialog');
    if (!modal) return;
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }

  // Edit Profile Modal
  function openEditProfileModal() {
    const modal = document.getElementById('modal-edit-profile');
    if (!modal) return;

    const nameInput = document.getElementById('edit-name');
    const phoneInput = document.getElementById('edit-phone');
    const emailInput = document.getElementById('edit-email');
    const emgInput = document.getElementById('edit-emergency');
    const addrInput = document.getElementById('edit-address');

    if (nameInput) nameInput.value = currentProfile.name;
    if (phoneInput) phoneInput.value = currentProfile.phone;
    if (emailInput) emailInput.value = currentProfile.email;
    if (emgInput) emgInput.value = currentProfile.emergencyContact;
    if (addrInput) addrInput.value = currentProfile.address;

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  function closeEditProfileModal() {
    const modal = document.getElementById('modal-edit-profile');
    if (!modal) return;
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }

  // Book Appointment Modal
  function openBookAppointmentModal() {
    const modal = document.getElementById('modal-book-appointment');
    if (!modal) return;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  function closeBookAppointmentModal() {
    const modal = document.getElementById('modal-book-appointment');
    if (!modal) return;
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }

  // Record Detail Modal
  function openRecordDetailModal(recId) {
    const record = defaultMedicalRecords.find(function (r) { return r.id === recId; });
    if (!record) return;

    const modal = document.getElementById('modal-report-dialog');
    const container = document.getElementById('modal-report-dialog-content');
    if (!modal || !container) return;

    container.innerHTML = (
      '<div class="clinical-report-sheet" style="padding: 2rem; border-radius: var(--radius-xl);">' +
        '<div class="report-letterhead">' +
          '<div class="report-letterhead-left">' +
            '<div class="brand-group">' +
              '<div class="brand-logo" style="width: 32px; height: 32px;">' +
                '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>' +
              '</div>' +
              '<div>' +
                '<div class="brand-name" style="font-size: 1.05rem;">MediSight <span>AI</span></div>' +
                '<div class="text-xs text-muted uppercase">Hospital Clinical Episode Record</div>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<div class="report-letterhead-right">' +
            '<div class="font-mono text-sm font-bold text-primary">EPISODE REF: ' + record.id.toUpperCase() + '</div>' +
            '<div class="text-xs text-muted">Date: ' + record.date + '</div>' +
          '</div>' +
        '</div>' +

        '<div class="report-patient-meta-grid" style="margin-bottom: 1.25rem;">' +
          '<div class="meta-item"><span class="meta-label">Patient</span><span class="meta-value font-bold">' + currentProfile.name + '</span></div>' +
          '<div class="meta-item"><span class="meta-label">MR No</span><span class="meta-value font-mono font-bold text-primary">' + currentProfile.mrNo + '</span></div>' +
          '<div class="meta-item"><span class="meta-label">Attending Doctor</span><span class="meta-value font-semibold">' + record.doctor + '</span></div>' +
          '<div class="meta-item col-span-3"><span class="meta-label">Department</span><span class="meta-value">' + record.department + '</span></div>' +
        '</div>' +

        '<div style="margin-bottom: 1.25rem;">' +
          '<h4 class="report-section-title">Physician Evaluation &amp; Clinical Notes</h4>' +
          '<div class="report-text-box" style="margin-top: 0.35rem; line-height: 1.6;">' + record.diagnosisNotes + '</div>' +
        '</div>' +

        '<div style="margin-bottom: 1.25rem;">' +
          '<h4 class="report-section-title">Prescriptions</h4>' +
          '<div class="report-meds-box" style="margin-top: 0.35rem;">' + record.prescriptions + '</div>' +
        '</div>' +

        '<div class="report-footer-actions">' +
          '<span class="text-xs text-muted">Electronic health record maintained by MediSight Memorial Hospital.</span>' +
          '<button type="button" class="btn btn-outline" id="btn-close-record-modal">Close</button>' +
        '</div>' +
      '</div>'
    );

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    const closeBtn = document.getElementById('btn-close-record-modal');
    if (closeBtn) closeBtn.addEventListener('click', closeReportModal);
  }

  // Toast Notification
  function showToast(title, message, type) {
    type = type || 'success';
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast-card toast-' + type;
    toast.innerHTML = (
      '<div class="toast-icon">' +
        (type === 'success' ? (
          '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>'
        ) : (
          '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>'
        )) +
      '</div>' +
      '<div class="toast-body">' +
        '<h4 class="toast-title">' + title + '</h4>' +
        '<p class="toast-message">' + message + '</p>' +
      '</div>' +
      '<button type="button" class="toast-close" aria-label="Close notification">&times;</button>'
    );

    container.appendChild(toast);

    toast.querySelector('.toast-close').addEventListener('click', function () {
      toast.remove();
    });

    setTimeout(function () {
      toast.classList.add('fade-out');
      setTimeout(function () {
        toast.remove();
      }, 300);
    }, 4500);
  }

  // Logout handler
  function handleLogout() {
    showToast('Patient Session Concluded', 'Returning to MediSight AI portal...', 'info');
    setTimeout(function () {
      window.location.href = 'index.html';
    }, 1000);
  }

  // ============================================================================
  // Event Binding
  // ============================================================================
  function bindEvents() {
    // Navigation Links
    document.querySelectorAll('.patient-nav-link, .patient-tab-btn, .mobile-nav-link').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const tab = btn.getAttribute('data-tab');
        if (tab) {
          switchTab(tab);
          window.location.hash = tab;
        }
      });
    });

    // Mobile Drawer
    const mobileToggle = document.getElementById('patient-mobile-toggle');
    const mobilePanel = document.getElementById('patient-mobile-panel');
    if (mobileToggle && mobilePanel) {
      mobileToggle.addEventListener('click', function () {
        const isOpen = mobilePanel.classList.toggle('is-open');
        mobileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });

      mobilePanel.querySelectorAll('.mobile-nav-link').forEach(function (link) {
        link.addEventListener('click', function () {
          mobilePanel.classList.remove('is-open');
          mobileToggle.setAttribute('aria-expanded', 'false');
        });
      });
    }

    // Logout Buttons
    document.querySelectorAll('.btn-patient-logout').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        handleLogout();
      });
    });

    // Edit Profile Modal Triggers
    const editProfileOpen = document.getElementById('btn-edit-profile-open');
    const editProfileClose = document.getElementById('btn-close-edit-profile');
    const editProfileCancel = document.getElementById('btn-cancel-edit-profile');
    const formEditProfile = document.getElementById('form-edit-profile');

    if (editProfileOpen) editProfileOpen.addEventListener('click', openEditProfileModal);
    if (editProfileClose) editProfileClose.addEventListener('click', closeEditProfileModal);
    if (editProfileCancel) editProfileCancel.addEventListener('click', closeEditProfileModal);

    if (formEditProfile) {
      formEditProfile.addEventListener('submit', function (e) {
        e.preventDefault();
        const nameInput = document.getElementById('edit-name');
        const phoneInput = document.getElementById('edit-phone');
        const emailInput = document.getElementById('edit-email');
        const emgInput = document.getElementById('edit-emergency');
        const addrInput = document.getElementById('edit-address');

        if (nameInput) currentProfile.name = nameInput.value.trim();
        if (phoneInput) currentProfile.phone = phoneInput.value.trim();
        if (emailInput) currentProfile.email = emailInput.value.trim();
        if (emgInput) currentProfile.emergencyContact = emgInput.value.trim();
        if (addrInput) currentProfile.address = addrInput.value.trim();

        saveProfileToStorage();
        renderProfileView();
        closeEditProfileModal();
        showToast('Profile Updated', 'Patient demographic information successfully saved.', 'success');
      });
    }

    // Book Appointment Modal Triggers
    const bookAptOpen = document.getElementById('btn-book-appointment-open');
    const bookAptClose = document.getElementById('btn-close-book-appointment');
    const bookAptCancel = document.getElementById('btn-cancel-book-appointment');
    const formBookApt = document.getElementById('form-book-appointment');

    if (bookAptOpen) bookAptOpen.addEventListener('click', openBookAppointmentModal);
    if (bookAptClose) bookAptClose.addEventListener('click', closeBookAppointmentModal);
    if (bookAptCancel) bookAptCancel.addEventListener('click', closeBookAppointmentModal);

    if (formBookApt) {
      formBookApt.addEventListener('submit', function (e) {
        e.preventDefault();
        const docSelect = document.getElementById('book-doctor');
        const dateInput = document.getElementById('book-date');
        const timeSelect = document.getElementById('book-time');
        const reasonInput = document.getElementById('book-reason');

        const newApt = {
          id: 'apt-' + Date.now(),
          doctor: docSelect ? docSelect.value : 'Dr. Joison, MD',
          department: 'Outpatient Clinical Consultation',
          date: dateInput ? dateInput.value : 'Oct 15, 2026',
          time: timeSelect ? timeSelect.value : '10:30 AM',
          status: 'Upcoming',
          reason: reasonInput ? reasonInput.value.trim() : 'Routine follow-up',
          room: 'Main OPD Block, Room 204'
        };

        appointmentsList.unshift(newApt);
        renderAppointmentsView();
        closeBookAppointmentModal();
        showToast('Appointment Confirmed', 'Consultation booked successfully with ' + newApt.doctor + ' on ' + newApt.date + '.', 'success');
      });
    }

    // Report search
    const reportSearch = document.getElementById('patient-report-search');
    if (reportSearch) {
      reportSearch.addEventListener('input', function () {
        renderReportsView(reportSearch.value);
      });
    }

    // Report filters
    document.querySelectorAll('.btn-report-filter').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('.btn-report-filter').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        const searchVal = reportSearch ? reportSearch.value : '';
        renderReportsView(searchVal);
      });
    });

    // Mark All Read
    const markReadBtn = document.getElementById('btn-mark-all-read');
    if (markReadBtn) {
      markReadBtn.addEventListener('click', markAllNotificationsRead);
    }

    // Delegated clicks
    document.addEventListener('click', function (e) {
      const target = e.target;
      if (!target) return;

      // View Report button
      if (target.id === 'btn-patient-view-modal' || target.closest('#btn-patient-view-modal')) {
        openReportModal();
        return;
      }

      // View result from Investigations
      if (target.closest('.btn-inv-view-result')) {
        switchTab('reports');
        window.location.hash = 'reports';
        return;
      }

      // View single record
      const viewRecBtn = target.closest('.btn-view-single-record');
      if (viewRecBtn) {
        const recId = viewRecBtn.getAttribute('data-recid');
        if (recId) openRecordDetailModal(recId);
        return;
      }
    });

    // Close modals on backdrop click
    ['modal-edit-profile', 'modal-book-appointment', 'modal-report-dialog'].forEach(function (modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.addEventListener('click', function (e) {
          if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
          }
        });
      }
    });

    // Escape closes modals
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        ['modal-edit-profile', 'modal-book-appointment', 'modal-report-dialog'].forEach(function (modalId) {
          const modal = document.getElementById(modalId);
          if (modal && modal.style.display === 'flex') {
            modal.style.display = 'none';
            document.body.style.overflow = '';
          }
        });
      }
    });

    // Storage event: sync when reports or patients updated in doctor dashboard
    window.addEventListener('storage', function () {
      renderReportsView();
    });

    // Window focus sync
    window.addEventListener('focus', function () {
      renderReportsView();
    });
  }

  // Expose global methods for inline handlers
  window.showPatientToast = showToast;
  window.openPatientReportModal = openReportModal;

  // DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
