/**
 * MediSight AI - Main Application Script (TypeScript)
 * Converted from js/main.js
 * Clean, componentized hospital system script.
 * Zero-dependency, compatible with both local file:// and HTTP servers.
 */

import { ModalType, PipelinePhase, SystemMetadata } from './types';

// ============================================================================
// Clinical Demo Data Model
// ============================================================================
export const HospitalData: {
  readonly system: SystemMetadata;
  readonly pipelinePhases: Record<string, PipelinePhase>;
} = {
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
export function initModals(): void {
  const modalBackdrop = document.getElementById('modal-backdrop') as HTMLElement | null;
  if (!modalBackdrop) return;

  const modalViews: Record<ModalType, HTMLElement | null> = {
    'doctor-login': document.getElementById('modal-doctor-login'),
    'patient-login': document.getElementById('modal-patient-login'),
    'register': document.getElementById('modal-register')
  };

  function openModal(modalType: ModalType): void {
    (Object.keys(modalViews) as ModalType[]).forEach((key) => {
      const view = modalViews[key];
      if (view) {
        view.style.display = 'none';
      }
    });

    const target = modalViews[modalType];
    if (target) {
      target.style.display = 'block';
      modalBackdrop!.classList.add('is-active');
      modalBackdrop!.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';

      const firstInput = target.querySelector<HTMLElement>('input, select, button');
      if (firstInput) {
        firstInput.focus();
      }
    }
  }

  function closeModal(): void {
    modalBackdrop!.classList.remove('is-active');
    modalBackdrop!.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  // Bind open trigger buttons
  const openTriggers = document.querySelectorAll<HTMLElement>('[data-open-modal]');
  openTriggers.forEach((trigger: HTMLElement) => {
    trigger.addEventListener('click', (event: MouseEvent) => {
      event.preventDefault();
      const modalType = trigger.getAttribute('data-open-modal') as ModalType | null;
      if (modalType && modalType in modalViews) {
        openModal(modalType);
      }
    });
  });

  // Bind close buttons
  const closeButtons = document.querySelectorAll<HTMLElement>('[data-close-modal]');
  closeButtons.forEach((btn: HTMLElement) => {
    btn.addEventListener('click', () => {
      closeModal();
    });
  });

  // Close on backdrop click
  modalBackdrop.addEventListener('click', (event: MouseEvent) => {
    if (event.target === modalBackdrop) {
      closeModal();
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', (event: KeyboardEvent) => {
    if (event.key === 'Escape' && modalBackdrop.classList.contains('is-active')) {
      closeModal();
    }
  });

  // Handle demo forms submission
  const forms = document.querySelectorAll<HTMLFormElement>('.modal-form');
  forms.forEach((form: HTMLFormElement) => {
    form.addEventListener('submit', (event: SubmitEvent) => {
      event.preventDefault();
      const feedback = form.querySelector<HTMLElement>('.form-demo-feedback');
      if (feedback) {
        feedback.style.display = 'block';
      }
      if (form.closest('#modal-doctor-login')) {
        setTimeout(() => {
          window.location.href = 'doctor-dashboard.html';
        }, 300);
      }
    });
  });
}

// ============================================================================
// Mobile Navigation Drawer
// ============================================================================
export function initMobileNavigation(): void {
  const toggleBtn = document.getElementById('mobile-menu-toggle') as HTMLButtonElement | null;
  const mobilePanel = document.getElementById('mobile-nav-panel') as HTMLElement | null;

  if (!toggleBtn || !mobilePanel) return;

  toggleBtn.addEventListener('click', () => {
    const isOpen = mobilePanel.classList.toggle('is-open');
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  const links = mobilePanel.querySelectorAll<HTMLAnchorElement>('a');
  links.forEach((link: HTMLAnchorElement) => {
    link.addEventListener('click', () => {
      mobilePanel.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

// ============================================================================
// Medical Imaging HUD Controls (Hero Visual)
// ============================================================================
export function initHudControls(): void {
  const toggleOverlayBtn = document.getElementById('toggle-ai-overlay') as HTMLButtonElement | null;
  const roiBox = document.getElementById('hud-roi-box') as HTMLElement | null;
  const findingCard = document.getElementById('hud-finding-card') as HTMLElement | null;

  if (!toggleOverlayBtn || !roiBox) return;

  let isOverlayActive: boolean = true;

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
export function initExplainabilityPipeline(): void {
  const workflowNodes = document.querySelectorAll<HTMLElement>('.workflow-node');
  const stepDetailContainer = document.getElementById('workflow-step-detail') as HTMLElement | null;

  if (!workflowNodes.length || !stepDetailContainer) return;

  workflowNodes.forEach((node: HTMLElement) => {
    node.addEventListener('click', () => {
      workflowNodes.forEach((n: HTMLElement) => n.classList.remove('active'));
      node.classList.add('active');

      const stepId = node.getAttribute('data-step') || '1';
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

    node.addEventListener('keydown', (event: KeyboardEvent) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        node.click();
      }
    });
  });
}

// ============================================================================
// Scroll Spy for Navigation Highlighting
// ============================================================================
export function initScrollTracking(): void {
  const sections = document.querySelectorAll<HTMLElement>('section[id], article[id]');
  const navLinks = document.querySelectorAll<HTMLAnchorElement>('.nav-links a');

  if (!sections.length || !navLinks.length) return;

  window.addEventListener('scroll', () => {
    let currentId: string = '';
    const scrollPosition = window.scrollY + 140;

    sections.forEach((section: HTMLElement) => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      if (scrollPosition >= top && scrollPosition < top + height) {
        currentId = section.getAttribute('id') || '';
      }
    });

    navLinks.forEach((link: HTMLAnchorElement) => {
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
