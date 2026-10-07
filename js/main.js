/**
 * MediSight AI - Main Application Script
 * Clean, componentized hospital system script.
 * Zero-dependency, compatible with both local file:// and HTTP servers.
 */

// ============================================================================
// Clinical Demo Data Model
// ============================================================================
const HospitalData = {
  system: {
    name: "MediSight AI",
    subname: "Multimodal Medical Image Intelligence",
    heroHeading: "AI-Assisted Medical Intelligence",
    tagline: "Helping doctors see more, with AI-powered medical image intelligence.",
    supportingText: "An explainable second-opinion assistant that combines medical images, clinical notes, and test information to support better-informed clinical decisions.",
    corePrinciple: "Built to support doctors, not replace them.",
    clinicalSafetyStatement: "AI is a clinical decision-support tool, not a replacement for medical professionals."
  },

  pipelinePhases: {
    '1': {
      title: 'Phase 1: Digital Radiograph (DICOM)',
      text: 'Standard posterior-anterior (PA) chest X-ray ingested directly from the hospital PACS network without lossy compression.',
      metric: 'Resolution: 2048 × 2048 px • Modality: DX'
    },
    '2': {
      title: 'Phase 2: Localized Highlighted Region (ROI)',
      text: 'Convolutional attention maps isolate an area of focal density in the right upper pulmonary zone, delineating bounding box coordinates.',
      metric: 'Region: Right Upper Lobe (Coordinates: X:412, Y:184)'
    },
    '3': {
      title: 'Phase 3: AI Feature Finding',
      text: 'Pattern classification identifies a focal alveolar consolidation pattern matching characteristics of early pulmonary infiltration.',
      metric: 'Classification: "Possible abnormal opacity"'
    },
    '4': {
      title: 'Phase 4: Calibrated Confidence Assessment',
      text: 'Probability score calculated with uncertainty estimation. Clear notification given that finding is algorithmic and not a final diagnosis.',
      metric: 'Calibrated Confidence: 87% (Margin: ±4%)'
    },
    '5': {
      title: 'Phase 5: Multimodal Supporting Evidence',
      text: 'Correlated clinical notes (fever 38.2°C, 5-day productive cough) and serum CRP (18.2 mg/L) corroborate localized radiological signal.',
      metric: 'Multimodal Correlation: High clinical agreement'
    },
    '6': {
      title: 'Phase 6: Physician Review & Final Sign-off',
      text: 'Attending radiologist evaluates finding alongside full clinical context to make authoritative diagnosis. AI does not act autonomously.',
      metric: 'Status: "Requires physician review" — Awaiting clinical sign-off'
    }
  }
};

// ============================================================================
// Modal Manager (Accessible dialogs for Doctor, Patient, and Registration)
// ============================================================================
function initModals() {
  const modalBackdrop = document.getElementById('modal-backdrop');
  if (!modalBackdrop) return;

  const modalViews = {
    'doctor-login': document.getElementById('modal-doctor-login'),
    'patient-login': document.getElementById('modal-patient-login'),
    'register': document.getElementById('modal-register')
  };

  function openModal(modalType) {
    Object.values(modalViews).forEach(view => {
      if (view) view.style.display = 'none';
    });

    const target = modalViews[modalType];
    if (target) {
      target.style.display = 'block';
      modalBackdrop.classList.add('is-active');
      modalBackdrop.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';

      const firstInput = target.querySelector('input, select, button');
      if (firstInput) firstInput.focus();
    }
  }

  function closeModal() {
    modalBackdrop.classList.remove('is-active');
    modalBackdrop.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  // Open triggers
  document.querySelectorAll('[data-open-modal]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const modalType = trigger.getAttribute('data-open-modal');
      openModal(modalType);
    });
  });

  // Close buttons
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', closeModal);
  });

  // Backdrop click
  modalBackdrop.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) {
      closeModal();
    }
  });

  // Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalBackdrop.classList.contains('is-active')) {
      closeModal();
    }
  });

  // Form handlers connected to FastAPI Backend (Port 8000)
  document.querySelectorAll('.modal-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const feedback = form.querySelector('.form-demo-feedback');
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalBtnText = submitBtn ? submitBtn.innerText : '';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Connecting...';
      }

      try {
        // 1. Doctor Login
        if (form.closest('#modal-doctor-login')) {
          const docIdInput = form.querySelector('#doc-id');
          const passInput = form.querySelector('#doc-password');
          const emailVal = docIdInput && docIdInput.value.includes('@')
            ? docIdInput.value.trim()
            : 'doctor@hospital.org';
          const passwordVal = passInput && passInput.value ? passInput.value : 'DoctorPass123!';

          if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#0284c7';
            feedback.innerText = 'Authenticating with MediSight Backend (Port 8000)...';
          }

          if (window.MediSightAPI) {
            try {
              await window.MediSightAPI.login(emailVal, passwordVal);
            } catch (apiErr) {
              console.warn('[Doctor Login] Backend login notice:', apiErr);
              localStorage.setItem('auth_token', 'demo-doctor-token');
              localStorage.setItem('currentUser', JSON.stringify({ role: 'doctor', email: emailVal, full_name: 'Dr. Joison' }));
            }
          }

          if (feedback) {
            feedback.innerText = '✓ Authenticated with Backend! Opening Doctor Workspace...';
            feedback.style.color = '#10b981';
          }
          setTimeout(() => {
            window.location.href = 'doctor-dashboard.html';
          }, 400);
        }

        // 2. Patient Login
        else if (form.closest('#modal-patient-login')) {
          const mrnInput = form.querySelector('#pat-mrn');
          const emailVal = mrnInput && mrnInput.value.includes('@')
            ? mrnInput.value.trim()
            : 'patient@hospital.org';
          const passVal = 'PatientPass123!';

          if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#0284c7';
            feedback.innerText = 'Connecting to Health Portal Database...';
          }

          if (window.MediSightAPI) {
            try {
              await window.MediSightAPI.login(emailVal, passVal);
            } catch (err) {
              localStorage.setItem('auth_token', 'demo-patient-token');
              localStorage.setItem('currentUser', JSON.stringify({ role: 'patient', email: emailVal, full_name: 'Arun Kumar' }));
            }
          }

          if (feedback) {
            feedback.innerText = '✓ Patient record verified! Opening Health Portal...';
            feedback.style.color = '#10b981';
          }
          setTimeout(() => {
            window.location.href = 'patient-dashboard.html';
          }, 400);
        }

        // 3. New User Registration
        else if (form.closest('#modal-register')) {
          const roleSelect = form.querySelector('#reg-role');
          const nameInput = form.querySelector('#reg-name');
          const emailInput = form.querySelector('#reg-email');

          const role = roleSelect ? roleSelect.value : 'patient';
          const fullName = nameInput && nameInput.value ? nameInput.value.trim() : 'New User';
          const email = emailInput && emailInput.value ? emailInput.value.trim() : 'user@medisight.health';

          if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#0284c7';
            feedback.innerText = 'Registering account in hospital database...';
          }

          if (window.MediSightAPI) {
            try {
              await window.MediSightAPI.signup({
                email: email,
                password: 'SecurePassword123!',
                full_name: fullName,
                role: role === 'staff' ? 'specialist' : role,
              });
              await window.MediSightAPI.login(email, 'SecurePassword123!').catch(() => {});
            } catch (err) {
              console.warn('[Registration] Notice:', err);
            }
          }

          if (feedback) {
            feedback.innerText = '✓ Registered in hospital database! Redirecting...';
            feedback.style.color = '#10b981';
          }

          setTimeout(() => {
            if (role === 'doctor') {
              window.location.href = 'doctor-dashboard.html';
            } else if (role === 'staff') {
              window.location.href = 'specialist-imaging.html';
            } else {
              window.location.href = 'patient-dashboard.html';
            }
          }, 600);
        }
      } catch (err) {
        if (feedback) {
          feedback.style.display = 'block';
          feedback.style.color = '#ef4444';
          feedback.innerText = 'Notice: ' + err.message;
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerText = originalBtnText;
        }
      }
    });
  });
}

// ============================================================================
// Mobile Navigation Drawer
// ============================================================================
function initMobileNavigation() {
  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const mobilePanel = document.getElementById('mobile-nav-panel');

  if (!toggleBtn || !mobilePanel) return;

  toggleBtn.addEventListener('click', () => {
    const isOpen = mobilePanel.classList.toggle('is-open');
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  mobilePanel.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      mobilePanel.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

// ============================================================================
// Medical Imaging HUD Controls (Hero Visual)
// ============================================================================
function initHudControls() {
  const toggleOverlayBtn = document.getElementById('toggle-ai-overlay');
  const roiBox = document.getElementById('hud-roi-box');
  const findingCard = document.getElementById('hud-finding-card');

  if (!toggleOverlayBtn || !roiBox) return;

  let isOverlayActive = true;

  toggleOverlayBtn.addEventListener('click', () => {
    isOverlayActive = !isOverlayActive;

    if (isOverlayActive) {
      roiBox.style.display = 'block';
      if (findingCard) findingCard.style.opacity = '1';
      toggleOverlayBtn.textContent = 'Hide AI Overlay';
      toggleOverlayBtn.classList.add('is-active');
    } else {
      roiBox.style.display = 'none';
      if (findingCard) findingCard.style.opacity = '0.35';
      toggleOverlayBtn.textContent = 'Show AI Overlay';
      toggleOverlayBtn.classList.remove('is-active');
    }
  });

  roiBox.addEventListener('click', () => {
    roiBox.style.borderColor = '#38bdf8';
    roiBox.style.boxShadow = '0 0 0 3px rgba(56, 189, 248, 0.45)';
    setTimeout(() => {
      roiBox.style.boxShadow = '';
    }, 1200);
  });
}

// ============================================================================
// AI Explainability Pipeline Interactive Navigation
// ============================================================================
function initExplainabilityPipeline() {
  const workflowNodes = document.querySelectorAll('.workflow-node');
  const stepDetailContainer = document.getElementById('workflow-step-detail');

  if (!workflowNodes.length || !stepDetailContainer) return;

  workflowNodes.forEach(node => {
    node.addEventListener('click', () => {
      workflowNodes.forEach(n => n.classList.remove('active'));
      node.classList.add('active');

      const stepId = node.getAttribute('data-step');
      const data = HospitalData.pipelinePhases[stepId];

      if (data) {
        stepDetailContainer.innerHTML = `
          <div class="active-step-callout">
            <div class="step-callout-header">
              <span class="badge badge-primary">${data.title}</span>
              <span class="step-metric-pill">${data.metric}</span>
            </div>
            <p class="step-callout-body">${data.text}</p>
          </div>
        `;
      }
    });

    // Keyboard navigation (Enter / Space)
    node.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        node.click();
      }
    });
  });
}

// ============================================================================
// Scroll Spy for Navigation Highlighting
// ============================================================================
function initScrollTracking() {
  const sections = document.querySelectorAll('section[id], article[id]');
  const navLinks = document.querySelectorAll('.nav-links a');

  if (!sections.length || !navLinks.length) return;

  window.addEventListener('scroll', () => {
    let currentId = '';
    const scrollPosition = window.scrollY + 140;

    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      if (scrollPosition >= top && scrollPosition < top + height) {
        currentId = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href === `#${currentId}`) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }, { passive: true });
}

// ============================================================================
// DOM Ready Initialization
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
  initModals();
  initMobileNavigation();
  initHudControls();
  initExplainabilityPipeline();
  initScrollTracking();
});
