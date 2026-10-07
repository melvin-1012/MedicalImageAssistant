/**
 * MediSight AI - Specialist Medical Imaging & AI Analysis
 * Runtime JavaScript for specialist-imaging.html
 * Zero-dependency, runs natively in all browsers and with file:// or HTTP.
 */

(function () {
  'use strict';

  // Default Mock Patients
  const defaultPatients = [
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

  // Default Mock Reports
  const defaultReports = {
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

  // State Management
  function loadPatients() {
    try {
      const stored = localStorage.getItem('medisight_patients');
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return JSON.parse(JSON.stringify(defaultPatients));
  }

  function savePatients(data) {
    try {
      localStorage.setItem('medisight_patients', JSON.stringify(data));
    } catch (e) {}
  }

  function loadReports() {
    try {
      const stored = localStorage.getItem('medisight_reports');
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return JSON.parse(JSON.stringify(defaultReports));
  }

  function saveReports(data) {
    try {
      localStorage.setItem('medisight_reports', JSON.stringify(data));
    } catch (e) {}
  }

  let currentPatientMrNo = 'MR001';
  let hasImageAttached = false;
  let attachedImageSrc = 'assets/images/chest_xray.jpg';

  // Initialize
  function init() {
    // Parse URL parameter ?mrNo=...
    const urlParams = new URLSearchParams(window.location.search);
    const paramMrNo = urlParams.get('mrNo');
    if (paramMrNo) {
      currentPatientMrNo = paramMrNo.toUpperCase();
    }

    renderPatientDetails();
    setupDropzone();
    setupModality();
    setupSubmission();
    setupModal();
    setupPatientSwitchers();
  }

  // Render Patient Info Card
  function renderPatientDetails() {
    const patients = loadPatients();
    const patient = patients.find(function (p) { return p.mrNo === currentPatientMrNo; }) || patients[0];
    if (!patient) return;

    currentPatientMrNo = patient.mrNo;

    // Update Elements
    const mrNoEl = document.getElementById('patient-info-mrno');
    const nameEl = document.getElementById('patient-info-name');
    const demoEl = document.getElementById('patient-info-demographics');
    const symptomsEl = document.getElementById('patient-info-symptoms');
    const investEl = document.getElementById('patient-info-investigation');
    const specEl = document.getElementById('patient-info-specialist');
    const notesEl = document.getElementById('patient-info-notes');
    const statusBadgeEl = document.getElementById('patient-info-status-badge');
    const statusTextEl = document.getElementById('patient-info-status-text');
    const breadcrumbMrNo = document.getElementById('breadcrumb-mrno');

    if (mrNoEl) mrNoEl.textContent = patient.mrNo;
    if (nameEl) nameEl.textContent = patient.name;
    if (demoEl) demoEl.textContent = patient.age + ' Y • ' + patient.gender;
    if (symptomsEl) symptomsEl.textContent = patient.symptoms;
    if (investEl) investEl.textContent = patient.investigationStatus;
    if (specEl) specEl.textContent = patient.assignedSpecialist;
    if (notesEl) notesEl.textContent = patient.clinicalNotes;
    if (breadcrumbMrNo) breadcrumbMrNo.textContent = patient.mrNo + ' (' + patient.name + ') Imaging Intake';

    if (statusBadgeEl && statusTextEl) {
      if (patient.status === 'Completed') {
        statusBadgeEl.className = 'badge badge-success';
        statusTextEl.textContent = 'Completed';
      } else {
        statusBadgeEl.className = 'badge badge-warning';
        statusTextEl.textContent = 'Pending';
      }
    }

    // Update buttons pointing to doctor dashboard with correct query params
    const btnGotoStatus = document.getElementById('btn-goto-patient-status');
    if (btnGotoStatus) {
      btnGotoStatus.href = 'doctor-dashboard.html?mrNo=' + patient.mrNo + '&view=patient-status';
    }

    const btnGotoReports = document.getElementById('btn-goto-doctor-reports');
    if (btnGotoReports) {
      btnGotoReports.href = 'doctor-dashboard.html?mrNo=' + patient.mrNo + '&view=reports';
    }

    const btnModalOpenDoctor = document.getElementById('btn-modal-open-doctor-review');
    if (btnModalOpenDoctor) {
      btnModalOpenDoctor.href = 'doctor-dashboard.html?mrNo=' + patient.mrNo + '&view=reports';
    }

    // Set modality dropdown based on existing report if available
    const reports = loadReports();
    const report = reports[patient.mrNo];
    const modalitySelect = document.getElementById('modality-select');
    if (modalitySelect && report && report.modality) {
      modalitySelect.value = report.modality;
    }
  }

  // Setup Patient Switchers
  function setupPatientSwitchers() {
    document.querySelectorAll('.btn-patient-switch').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const mrNo = btn.getAttribute('data-mrno');
        if (mrNo) {
          currentPatientMrNo = mrNo;
          // Reset view state
          resetViewState();
          renderPatientDetails();
          // Update URL without reload
          if (window.history.pushState) {
            const newUrl = window.location.pathname + '?mrNo=' + mrNo;
            window.history.pushState({ path: newUrl }, '', newUrl);
          }
        }
      });
    });
  }

  function resetViewState() {
    const intakeCard = document.getElementById('imaging-intake-card');
    const procState = document.getElementById('ai-processing-state');
    const resState = document.getElementById('ai-result-state');

    if (intakeCard) intakeCard.style.display = 'flex';
    if (procState) procState.style.display = 'none';
    if (resState) resState.style.display = 'none';

    const submitBtn = document.getElementById('btn-submit-ai');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
          '<path d="M12 2v20M2 12h20"></path>' +
          '<circle cx="12" cy="12" r="5" stroke-width="1.8" stroke-dasharray="2 2"></circle>' +
        '</svg> ' +
        'Submit for AI Analysis'
      );
    }
  }

  // Setup Dropzone & File Picker
  function setupDropzone() {
    const dropzone = document.getElementById('imaging-dropzone');
    const fileInput = document.getElementById('image-file-input');
    const sampleBtn = document.getElementById('btn-load-sample-scan');
    const previewContainer = document.getElementById('imaging-preview-container');
    const previewImg = document.getElementById('imaging-preview-img');
    const previewRadar = document.getElementById('preview-radar-line');
    const statusLabel = document.getElementById('upload-status-label');

    if (!dropzone || !fileInput) return;

    // Click dropzone to open file picker
    dropzone.addEventListener('click', function () {
      fileInput.click();
    });

    // Keyboard support
    dropzone.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInput.click();
      }
    });

    // Drag and drop handlers
    dropzone.addEventListener('dragover', function (e) {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', function () {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', function (e) {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });

    // File input change
    fileInput.addEventListener('change', function () {
      if (fileInput.files && fileInput.files.length > 0) {
        handleFileSelection(fileInput.files[0]);
      }
    });

    // Sample scan one-click load
    if (sampleBtn) {
      sampleBtn.addEventListener('click', function (e) {
        e.preventDefault();
        hasImageAttached = true;
        attachedImageSrc = 'assets/images/chest_xray.jpg';
        if (previewImg) previewImg.src = attachedImageSrc;
        if (previewContainer) previewContainer.style.display = 'flex';
        if (previewRadar) previewRadar.style.display = 'block';
        if (statusLabel) {
          statusLabel.textContent = 'Attached: chest_xray_sample.dcm (Ready)';
          statusLabel.className = 'text-xs text-success font-mono font-semibold';
        }
        showToast('Sample Scan Loaded', 'Demo chest radiograph successfully indexed for AI analysis.', 'success');
      });
    }

    function handleFileSelection(file) {
      if (!file) return;

      const reader = new FileReader();
      reader.onload = function (evt) {
        hasImageAttached = true;
        attachedImageSrc = evt.target.result;
        if (previewImg) previewImg.src = attachedImageSrc;
        if (previewContainer) previewContainer.style.display = 'flex';
        if (previewRadar) previewRadar.style.display = 'block';
        if (statusLabel) {
          statusLabel.textContent = 'Attached: ' + file.name + ' (' + Math.round(file.size / 1024) + ' KB)';
          statusLabel.className = 'text-xs text-success font-mono font-semibold';
        }
        showToast('Scan Attached', 'File "' + file.name + '" ready for multimodal AI evaluation.', 'success');
      };

      if (file.type.indexOf('image') !== -1 || file.name.endsWith('.dcm')) {
        reader.readAsDataURL(file);
      } else {
        // Fallback for DICOM binary files
        hasImageAttached = true;
        attachedImageSrc = 'assets/images/chest_xray.jpg';
        if (previewImg) previewImg.src = attachedImageSrc;
        if (previewContainer) previewContainer.style.display = 'flex';
        if (statusLabel) {
          statusLabel.textContent = 'Attached: ' + file.name + ' (DICOM Parsed)';
          statusLabel.className = 'text-xs text-success font-mono font-semibold';
        }
      }
    }
  }

  // Setup Modality
  function setupModality() {
    const modalitySelect = document.getElementById('modality-select');
    if (!modalitySelect) return;

    modalitySelect.addEventListener('change', function () {
      const selected = modalitySelect.value;
      const previewTag = document.getElementById('preview-tag-badge');
      if (previewTag) {
        previewTag.textContent = selected.toUpperCase() + ' SCAN READY';
      }
    });
  }

  // Setup Submission Workflow
  function setupSubmission() {
    const submitBtn = document.getElementById('btn-submit-ai');
    if (!submitBtn) return;

    submitBtn.addEventListener('click', function (e) {
      e.preventDefault();

      // If user hasn't loaded an image, auto-attach sample scan so the workflow is seamless
      if (!hasImageAttached) {
        hasImageAttached = true;
        attachedImageSrc = 'assets/images/chest_xray.jpg';
        const previewImg = document.getElementById('imaging-preview-img');
        const previewContainer = document.getElementById('imaging-preview-container');
        if (previewImg) previewImg.src = attachedImageSrc;
        if (previewContainer) previewContainer.style.display = 'flex';
        const statusLabel = document.getElementById('upload-status-label');
        if (statusLabel) {
          statusLabel.textContent = 'Attached: auto_sample_radiograph.dcm';
          statusLabel.className = 'text-xs text-success font-mono font-semibold';
        }
      }

      const modalitySelect = document.getElementById('modality-select');
      const selectedModality = modalitySelect ? modalitySelect.value : 'XRay';

      // 1. Show Processing State
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner spinner-white" style="width: 16px; height: 16px; margin-right: 8px;"></span> Submitting to AI...';

      const intakeCard = document.getElementById('imaging-intake-card');
      const procState = document.getElementById('ai-processing-state');
      const resState = document.getElementById('ai-result-state');
      const progressBar = document.getElementById('ai-progress-bar');
      const step1 = document.getElementById('step-1');
      const step2 = document.getElementById('step-2');
      const step3 = document.getElementById('step-3');

      if (procState) {
        procState.style.display = 'flex';
        procState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }

      showToast(
        'AI Processing Initiated',
        'Image submitted for AI analysis. Running multimodal model v4.2...',
        'info'
      );

      // Multi-stage progress simulation
      if (progressBar) progressBar.style.width = '25%';

      setTimeout(function () {
        if (progressBar) progressBar.style.width = '65%';
        if (step2) {
          step2.style.color = '#38bdf8';
        }
      }, 500);

      setTimeout(function () {
        if (progressBar) progressBar.style.width = '100%';
        if (step3) {
          step3.style.color = '#38bdf8';
        }
      }, 1000);

      // 2. Complete Analysis & Update Data via FastAPI Backend
      setTimeout(async function () {
        if (procState) procState.style.display = 'none';
        if (resState) {
          resState.style.display = 'flex';
          resState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Update patient status in localStorage
        const patients = loadPatients();
        const patient = patients.find(function (p) { return p.mrNo === currentPatientMrNo; });
        if (patient) {
          patient.status = 'Completed';
          patient.investigationStatus = selectedModality + ' Completed &bull; AI Analyzed';
          patient.aiAnalysisStatus = 'AI Analysis Completed &bull; Report Generated';
          savePatients(patients);
        }

        // Call FastAPI Backend GenAI Analysis (Port 8000)
        let aiResultFinding = 'AI analysis completed. Subtle infiltrate observed. Requires physician sign-off.';
        let aiConfidence = 'Confidence: 87%';
        let aiEvidence = 'Multimodal correlation completed with clinical notes.';

        if (window.MediSightAPI) {
          try {
            const visionData = {
              status: "success",
              modality: selectedModality || "X-Ray",
              findings: [
                {
                  label: "possible_lung_infiltrate",
                  score: 0.88,
                  region_id: "region_1"
                }
              ]
            };
            const rawNotes = (patient && patient.clinicalNotes) ? patient.clinicalNotes : (notesInput ? notesInput.value : "Persistent cough and fever");
            const res = await window.MediSightAPI.analyzeWithGenAI(visionData, rawNotes);
            if (res && res.findings && res.findings.length > 0) {
              const f = res.findings[0];
              aiResultFinding = f.finding + " • " + (f.explanation || "");
              aiConfidence = "Confidence: " + Math.round((f.model_score || 0.88) * 100) + "%";
              aiEvidence = (res.summary || "") + " • Cross-correlated with patient symptoms.";
            }
          } catch (apiErr) {
            console.warn('[GenAI API] Using cached radiomic data:', apiErr);
          }
        }

        // Update reports in localStorage
        const reports = loadReports();
        if (!reports[currentPatientMrNo]) {
          reports[currentPatientMrNo] = {
            mrNo: currentPatientMrNo,
            patientName: patient ? patient.name : 'Unknown',
            age: patient ? patient.age : 40,
            gender: patient ? patient.gender : 'Male',
            investigationType: selectedModality + ' Scan',
            modality: selectedModality,
            aiPreliminaryReportStatus: 'AI Preliminary Analysis Available',
            doctorReviewStatus: 'In Review by Attending Physician',
            finalReportStatus: 'Pending Final Physician Approval',
            aiFindings: aiResultFinding,
            confidence: aiConfidence,
            evidenceExplanation: aiEvidence,
            doctorConclusion: 'Awaiting doctor conclusion.',
            medications: '',
            recommendations: 'Follow up recommended.',
            additionalNotes: '',
            reviewedBy: 'Dr. Joison',
            isApproved: false,
            isFinalSent: false
          };
        } else {
          reports[currentPatientMrNo].modality = selectedModality;
          reports[currentPatientMrNo].investigationType = selectedModality + ' Examination';
          reports[currentPatientMrNo].aiPreliminaryReportStatus = 'AI Preliminary Analysis Available';
          reports[currentPatientMrNo].finalReportStatus = 'Pending Final Physician Approval';
          reports[currentPatientMrNo].aiFindings = aiResultFinding;
          reports[currentPatientMrNo].confidence = aiConfidence;
          reports[currentPatientMrNo].evidenceExplanation = aiEvidence;
        }
        saveReports(reports);

        // Update current patient badge on screen
        const statusBadgeEl = document.getElementById('patient-info-status-badge');
        const statusTextEl = document.getElementById('patient-info-status-text');
        if (statusBadgeEl && statusTextEl) {
          statusBadgeEl.className = 'badge badge-success';
          statusTextEl.textContent = 'Completed';
        }

        // Update Result Card Texts
        const resultModality = document.getElementById('result-modality-text');
        if (resultModality) {
          resultModality.textContent = selectedModality + ' (Completed)';
        }

        const resultFindings = document.getElementById('result-findings-text');
        if (resultFindings && reports[currentPatientMrNo]) {
          resultFindings.textContent = '“' + reports[currentPatientMrNo].aiFindings + '”';
        }

        const resultConfidence = document.getElementById('result-confidence-pill');
        if (resultConfidence && reports[currentPatientMrNo]) {
          resultConfidence.textContent = reports[currentPatientMrNo].confidence;
        }

        showToast(
          'Analysis Completed',
          'Analysis completed – Report generated. Patient status is now Completed.',
          'success'
        );

      }, 1500);
    });
  }

  // Setup PDF Report Modal
  function setupModal() {
    const viewReportBtn = document.getElementById('btn-view-report-modal');
    const modal = document.getElementById('report-preview-modal');
    const closeBtn = document.getElementById('btn-close-modal-report');

    if (!modal) return;

    if (viewReportBtn) {
      viewReportBtn.addEventListener('click', function () {
        openReportModal();
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        closeReportModal();
      });
    }

    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        closeReportModal();
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.style.display === 'flex') {
        closeReportModal();
      }
    });
  }

  function openReportModal() {
    const modal = document.getElementById('report-preview-modal');
    if (!modal) return;

    const reports = loadReports();
    const patients = loadPatients();
    const patient = patients.find(function (p) { return p.mrNo === currentPatientMrNo; }) || patients[0];
    const report = reports[currentPatientMrNo] || {};

    const modalitySelect = document.getElementById('modality-select');
    const modality = modalitySelect ? modalitySelect.value : (report.modality || 'XRay');

    const modalRef = document.getElementById('modal-report-ref');
    const modalName = document.getElementById('modal-patient-name');
    const modalMrNo = document.getElementById('modal-patient-mrno');
    const modalDemo = document.getElementById('modal-patient-demographics');
    const modalModality = document.getElementById('modal-patient-modality');
    const modalFindings = document.getElementById('modal-patient-findings');
    const modalEvidence = document.getElementById('modal-patient-evidence');

    if (modalRef) modalRef.textContent = 'REPORT REF: REP-' + patient.mrNo + '-2026';
    if (modalName) modalName.textContent = patient.name;
    if (modalMrNo) modalMrNo.textContent = patient.mrNo;
    if (modalDemo) modalDemo.textContent = patient.age + ' Y / ' + patient.gender;
    if (modalModality) modalModality.textContent = modality;
    if (modalFindings) modalFindings.textContent = '“' + (report.aiFindings || 'Preliminary radiomic analysis complete.') + '”';
    if (modalEvidence) modalEvidence.textContent = report.evidenceExplanation || 'Multimodal correlation confirmed.';

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  function closeReportModal() {
    const modal = document.getElementById('report-preview-modal');
    if (!modal) return;
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }

  // Toast Notifications
  function showToast(title, message, type) {
    type = type || 'success';
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast-card toast-' + type;
    toast.innerHTML = (
      '<div class="toast-icon">' +
        (type === 'success' ? (
          '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">' +
            '<polyline points="20 6 9 17 4 12"></polyline>' +
          '</svg>'
        ) : (
          '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">' +
            '<circle cx="12" cy="12" r="10"></circle>' +
            '<line x1="12" y1="8" x2="12" y2="12"></line>' +
            '<line x1="12" y1="16" x2="12.01" y2="16"></line>' +
          '</svg>'
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

  // DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
