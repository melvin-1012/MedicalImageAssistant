/**
 * MediSight AI - Patient Dashboard Logic (Runtime JavaScript)
 * Strictly 4 Tabs: Book an Appointment | Records | Reports | About Us.
 * Zero-dependency, runs natively in all browsers and with file:// or HTTP.
 */

(function () {
  'use strict';

  // ============================================================================
  // Patient & Clinical Data Store
  // ============================================================================
  const patientData = {
    mrNo: 'MR001',
    name: 'Arun Kumar',
    age: 45,
    gender: 'Male',
    contact: '+91 98451 23098',
    lastVisitDate: 'October 06, 2026',
    investigation: 'Digital Chest Radiography (PA View)',
    investigationDate: 'October 06, 2026',
    modality: 'XRay',
    doctorName: 'Dr. Joison, MD',
    doctorLicense: 'MED-REG-84920-KA'
  };

  // Helper to get doctor-approved report data from localStorage (or fallback)
  function getDoctorReportData() {
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
      doctorComments: (report && report.evidenceExplanation) ||
        'Evaluated digital chest radiograph alongside clinical presentation of exertional chest discomfort and borderline hypertension (138/86 mmHg). Cardiothoracic ratio calculated at ~0.52. Subtle perihilar prominence noted without acute focal consolidation or pneumothorax.',
      diagnosis: (report && report.doctorConclusion) ||
        'Clinical findings suggestive of early hypertensive cardiac strain. Borderline cardiomegaly (Cardiothoracic ratio ~0.52).',
      medications: (report && report.medications) ||
        'Tab. Amlodipine 5mg OD (morning), Tab. Aspirin 75mg OD (post-meal), Tab. Sorbitrate 5mg SL PRN for acute chest discomfort.',
      recommendations: (report && report.recommendations) ||
        '2D Echocardiogram with Doppler study within 48 hours, Low sodium cardiac diet, 24-hour ambulatory blood pressure monitoring. Report to emergency immediately if chest pain radiates to arm/jaw or exceeds 15 minutes.',
      isApproved: report ? report.isApproved : true,
      isFinalSent: report ? report.isFinalSent : false
    };
  }

  // Active view state
  let activeTab = 'book-appointment';
  // Report view mode: 'initial' (without diagnosis) or 'doctor-approved' (with diagnosis)
  let reportViewMode = 'initial';

  // ============================================================================
  // Initialization
  // ============================================================================
  function init() {
    // Check if doctor has already signed off in doctor dashboard
    const docData = getDoctorReportData();
    if (docData.isFinalSent) {
      reportViewMode = 'doctor-approved';
    } else {
      reportViewMode = 'initial';
    }

    renderReportsView();
    bindEvents();
    handleUrlHash();
  }

  // ============================================================================
  // Tab Switching (Strictly 4 Tabs)
  // ============================================================================
  function switchTab(tabId) {
    const validTabs = ['book-appointment', 'records', 'reports', 'about-us'];
    if (validTabs.indexOf(tabId) === -1) {
      tabId = 'book-appointment';
    }

    activeTab = tabId;

    // Update Primary & Secondary Navigation Buttons
    document.querySelectorAll('.patient-nav-link, .patient-tab-btn, .mobile-nav-link').forEach(function (el) {
      if (el.getAttribute('data-tab') === tabId) {
        el.classList.add('active');
        el.setAttribute('aria-selected', 'true');
      } else {
        el.classList.remove('active');
        el.setAttribute('aria-selected', 'false');
      }
    });

    // Update Tab View Panels
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
    const validTabs = ['book-appointment', 'records', 'reports', 'about-us'];
    if (validTabs.indexOf(hash) !== -1) {
      switchTab(hash);
    } else {
      switchTab('book-appointment');
    }
  }

  // ============================================================================
  // 3. Render Reports View (Initial Without Diagnosis vs Doctor-Approved)
  // ============================================================================
  function renderReportsView() {
    const container = document.getElementById('report-dynamic-content-area');
    const badgeContainer = document.getElementById('report-header-status-badge');
    const captionEl = document.getElementById('report-mode-caption');
    const btnInitial = document.getElementById('btn-toggle-initial-report');
    const btnDoctor = document.getElementById('btn-toggle-doctor-report');

    if (!container || !badgeContainer) return;

    // Update toggle buttons active class
    if (btnInitial && btnDoctor) {
      if (reportViewMode === 'initial') {
        btnInitial.classList.add('active');
        btnDoctor.classList.remove('active');
        if (captionEl) captionEl.textContent = 'Viewing initial report as received from imaging intake (without diagnosis).';
      } else {
        btnDoctor.classList.add('active');
        btnInitial.classList.remove('active');
        if (captionEl) captionEl.textContent = 'Viewing finalized report with attending doctor comments, diagnosis, and prescriptions.';
      }
    }

    const docData = getDoctorReportData();

    if (reportViewMode === 'initial') {
      // -------------------------------------------------------------
      // INITIAL REPORT: Shown WITHOUT diagnosis
      // -------------------------------------------------------------
      badgeContainer.innerHTML = (
        '<div class="badge badge-warning" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">' +
          '<span class="badge-dot"></span>' +
          'Awaiting Physician Review &bull; Preliminary' +
        '</div>'
      );

      container.innerHTML = (
        '<div style="display: flex; flex-direction: column; gap: 1.25rem;">' +
          
          // Safety Notice
          '<div class="clinical-safety-alert-banner">' +
            '<div>' +
              '<strong>Preliminary Investigation Notice:</strong>' +
              '<p class="mb-0 text-sm">' +
                'This medical imaging report has been logged in hospital records and is currently awaiting attending physician clinical review. Definitive diagnosis, physician comments, medications, and recommendations will be populated here once signed off by your consulting doctor.' +
              '</p>' +
            '</div>' +
          '</div>' +

          // 1. Doctor\'s Comments (Initial Placeholder)
          '<div>' +
            '<span class="record-cell-label">Doctor\'s Comments</span>' +
            '<div class="report-placeholder-field">' +
              'Pending physician clinical review and comments.' +
            '</div>' +
          '</div>' +

          // 2. Diagnosis (Initial Placeholder - WITHOUT Diagnosis)
          '<div>' +
            '<span class="record-cell-label">Diagnosis</span>' +
            '<div class="report-placeholder-field">' +
              'Pending attending physician diagnosis.' +
            '</div>' +
          '</div>' +

          // 3. Medications (Initial Placeholder)
          '<div>' +
            '<span class="record-cell-label">Medications</span>' +
            '<div class="report-placeholder-field">' +
              'No medications prescribed yet &mdash; Awaiting physician review.' +
            '</div>' +
          '</div>' +

          // 4. Recommendations (Initial Placeholder)
          '<div>' +
            '<span class="record-cell-label">Recommendations</span>' +
            '<div class="report-placeholder-field">' +
              'Pending clinical recommendations.' +
            '</div>' +
          '</div>' +

        '</div>'
      );

    } else {
      // -------------------------------------------------------------
      // DOCTOR-APPROVED REPORT: Displays information added by doctor
      // -------------------------------------------------------------
      badgeContainer.innerHTML = (
        '<div class="badge badge-success" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">' +
          '<span class="badge-dot"></span>' +
          'Doctor Approved &bull; Signed Off' +
        '</div>'
      );

      container.innerHTML = (
        '<div style="display: flex; flex-direction: column; gap: 1.25rem;">' +
          
          // Doctor Review Banner
          '<div style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: var(--radius-lg); padding: 1rem 1.25rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">' +
            '<div style="color: #166534; font-weight: 700; font-size: 0.95rem;">' +
              'Doctor Review Completed &bull; Verified by ' + patientData.doctorName +
            '</div>' +
            '<span class="font-mono text-xs text-muted">' + patientData.doctorLicense + '</span>' +
          '</div>' +

          // 1. Doctor\'s Comments
          '<div>' +
            '<span class="record-cell-label">Doctor\'s Comments</span>' +
            '<div class="report-filled-field">' +
              docData.doctorComments +
            '</div>' +
          '</div>' +

          // 2. Diagnosis (Added by Doctor)
          '<div>' +
            '<span class="record-cell-label">Diagnosis</span>' +
            '<div class="report-diagnosis-badge-field">' +
              docData.diagnosis +
            '</div>' +
          '</div>' +

          // 3. Medications (Added by Doctor)
          '<div>' +
            '<span class="record-cell-label">Prescribed Medications</span>' +
            '<div class="report-meds-box" style="margin-top: 0.25rem;">' +
              docData.medications +
            '</div>' +
          '</div>' +

          // 4. Recommendations (Added by Doctor)
          '<div>' +
            '<span class="record-cell-label">Physician Recommendations &amp; Follow-up Advice</span>' +
            '<div class="report-filled-field">' +
              docData.recommendations +
            '</div>' +
          '</div>' +

        '</div>'
      );
    }
  }

  // ============================================================================
  // Toast Notifications
  // ============================================================================
  function showToast(title, message, type) {
    type = type || 'success';
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast-card toast-' + type;
    toast.innerHTML = (
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
    }, 4000);
  }

  // ============================================================================
  // Event Binding
  // ============================================================================
  function bindEvents() {
    // Navigation Links (Navbar, Mobile Drawer, Secondary Sticky Tab Bar)
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

    // Mobile Navigation Drawer Toggle
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

    // Logout
    document.querySelectorAll('.btn-patient-logout').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        showToast('Session Concluded', 'Returning to MediSight AI landing page...', 'info');
        setTimeout(function () {
          window.location.href = 'index.html';
        }, 800);
      });
    });

    // Section 1: Book an Appointment Form Submit
    const formAppointment = document.getElementById('appointment-booking-form');
    const successCard = document.getElementById('booking-success-message');
    const btnBookAnother = document.getElementById('btn-book-another');

    if (formAppointment) {
      formAppointment.addEventListener('submit', function (e) {
        e.preventDefault();

        const nameInput = document.getElementById('booking-patient-name');
        const mrnoInput = document.getElementById('booking-mrno');
        const deptInput = document.getElementById('booking-department');
        const dateInput = document.getElementById('booking-date');
        const timeInput = document.getElementById('booking-time');

        const patName = nameInput ? nameInput.value : patientData.name;
        const mrno = mrnoInput ? mrnoInput.value : patientData.mrNo;
        const dept = deptInput ? deptInput.value : 'Dr. Joison, MD';
        const dateVal = dateInput ? dateInput.value : '2026-10-14';
        const timeVal = timeInput ? timeInput.value : '10:30 AM';

        // Update success card text
        const successPat = document.getElementById('success-patient-info');
        const successSpec = document.getElementById('success-specialist-info');
        const successDt = document.getElementById('success-datetime-info');

        if (successPat) successPat.textContent = patName + ' (' + mrno + ')';
        if (successSpec) successSpec.textContent = dept.split('—')[0].trim();
        if (successDt) successDt.textContent = dateVal + ' at ' + timeVal;

        if (successCard) {
          successCard.style.display = 'flex';
          successCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        showToast(
          'Appointment Booked',
          'Your appointment with ' + dept.split('—')[0].trim() + ' on ' + dateVal + ' has been registered.',
          'success'
        );
      });
    }

    if (btnBookAnother) {
      btnBookAnother.addEventListener('click', function () {
        if (successCard) successCard.style.display = 'none';
        if (formAppointment) {
          formAppointment.reset();
          const nameInput = document.getElementById('booking-patient-name');
          const mrnoInput = document.getElementById('booking-mrno');
          const ageInput = document.getElementById('booking-age');
          const contactInput = document.getElementById('booking-contact');

          if (nameInput) nameInput.value = patientData.name;
          if (mrnoInput) mrnoInput.value = patientData.mrNo;
          if (ageInput) ageInput.value = patientData.age;
          if (contactInput) contactInput.value = patientData.contact;
        }
      });
    }

    // Section 2: Clickable Previous Diagnosis -> Redirects to Reports Tab
    const diagBtn = document.getElementById('btn-diagnosis-link');
    if (diagBtn) {
      diagBtn.addEventListener('click', function (e) {
        e.preventDefault();
        switchTab('reports');
        window.location.hash = 'reports';
      });
    }

    const gotoReportsDirect = document.getElementById('btn-goto-reports-direct');
    if (gotoReportsDirect) {
      gotoReportsDirect.addEventListener('click', function (e) {
        e.preventDefault();
        switchTab('reports');
        window.location.hash = 'reports';
      });
    }

    // Section 3: Report State Toggle (Initial Without Diagnosis vs Doctor-Approved)
    const btnToggleInitial = document.getElementById('btn-toggle-initial-report');
    const btnToggleDoctor = document.getElementById('btn-toggle-doctor-report');

    if (btnToggleInitial) {
      btnToggleInitial.addEventListener('click', function () {
        reportViewMode = 'initial';
        renderReportsView();
      });
    }

    if (btnToggleDoctor) {
      btnToggleDoctor.addEventListener('click', function () {
        reportViewMode = 'doctor-approved';
        renderReportsView();
      });
    }

    // Storage event: sync if doctor finalized report in Doctor Dashboard
    window.addEventListener('storage', function () {
      const docData = getDoctorReportData();
      if (docData.isFinalSent) {
        reportViewMode = 'doctor-approved';
      }
      if (activeTab === 'reports') {
        renderReportsView();
      }
    });

    // Window focus sync
    window.addEventListener('focus', function () {
      const docData = getDoctorReportData();
      if (docData.isFinalSent) {
        reportViewMode = 'doctor-approved';
      }
      if (activeTab === 'reports') {
        renderReportsView();
      }
    });
  }

  // DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
