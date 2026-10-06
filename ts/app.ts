/**
 * MediSight AI - Application Logic (TypeScript)
 * Converted from js/app.js
 * Interactive UI behaviors, DICOM HUD overlays, and clinical workflow steps
 */

import { PipelinePhase } from './types';
import { setupModals } from './modal';

document.addEventListener('DOMContentLoaded', () => {
  // Initialize accessible modal dialogs
  setupModals();

  // Mobile navigation drawer toggle
  initMobileNav();

  // Radiology HUD interactive controls
  initHudControls();

  // Interactive explainability workflow pipeline
  initExplainabilityPipeline();

  // Smooth scroll and active section observer
  initScrollSpy();
});

/**
 * Mobile Navigation Drawer
 */
function initMobileNav(): void {
  const toggleBtn = document.getElementById('mobile-menu-toggle') as HTMLButtonElement | null;
  const mobilePanel = document.getElementById('mobile-nav-panel') as HTMLElement | null;

  if (!toggleBtn || !mobilePanel) return;

  toggleBtn.addEventListener('click', () => {
    const isOpen = mobilePanel.classList.toggle('is-open');
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Close when clicking any mobile navigation link
  const navLinks = mobilePanel.querySelectorAll<HTMLAnchorElement>('a');
  navLinks.forEach((link: HTMLAnchorElement) => {
    link.addEventListener('click', () => {
      mobilePanel.classList.remove('is-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

/**
 * Medical Imaging HUD Interactive Controls (Hero Viewer)
 */
function initHudControls(): void {
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

  // Clicking on the ROI box highlights finding details
  roiBox.addEventListener('click', () => {
    roiBox.style.borderColor = '#38bdf8';
    roiBox.style.boxShadow = '0 0 0 3px rgba(56, 189, 248, 0.45)';
    setTimeout(() => {
      roiBox.style.boxShadow = '';
    }, 1200);
  });
}

/**
 * AI Explainability Interactive Workflow
 * Allows user to click each step in the pipeline:
 * X-Ray Image -> Highlighted Region -> AI Finding -> Confidence -> Supporting Evidence -> Doctor Review
 */
function initExplainabilityPipeline(): void {
  const workflowNodes = document.querySelectorAll<HTMLElement>('.workflow-node');
  const stepDetailContainer = document.getElementById('workflow-step-detail') as HTMLElement | null;

  if (!workflowNodes.length || !stepDetailContainer) return;

  const nodeDescriptions: Record<string, PipelinePhase> = {
    '1': {
      title: 'Phase 1: Digital Radiograph (DICOM)',
      text: 'Standard posterior-anterior (PA) chest X-ray ingested directly from the hospital PACS network without lossy compression.',
      metric: 'Resolution: 2048 × 2048 px | Modality: DX'
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
      metric: 'Calibrated Confidence: 87% (Uncertainty Margin: ±4%)'
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
  };

  workflowNodes.forEach((node: HTMLElement) => {
    node.addEventListener('click', () => {
      workflowNodes.forEach((n: HTMLElement) => n.classList.remove('active'));
      node.classList.add('active');

      const stepId = node.getAttribute('data-step') || '1';
      const data = nodeDescriptions[stepId];

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

    // Keyboard accessibility (Enter / Space)
    node.addEventListener('keydown', (event: KeyboardEvent) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        node.click();
      }
    });
  });
}

/**
 * Scroll spy for updating active state on navbar links
 */
function initScrollSpy(): void {
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
