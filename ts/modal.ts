/**
 * MediSight AI - Modal Manager (TypeScript)
 * Converted from js/modal.js
 * Accessible modal handler for Patient Login, Doctor Login, and Registration demo dialogs.
 */

import { ModalType } from './types';

/**
 * Initializes accessible modal behaviors across the landing page.
 */
export function setupModals(): void {
  const modalBackdrop = document.getElementById('modal-backdrop') as HTMLElement | null;
  if (!modalBackdrop) return;

  const modalContents: Record<ModalType, HTMLElement | null> = {
    'doctor-login': document.getElementById('modal-doctor-login'),
    'patient-login': document.getElementById('modal-patient-login'),
    'register': document.getElementById('modal-register')
  };

  /**
   * Opens the requested modal type and traps focus on its first active element.
   */
  function openModal(modalType: ModalType): void {
    // Hide all modal views first
    (Object.keys(modalContents) as ModalType[]).forEach((key) => {
      const view = modalContents[key];
      if (view) {
        view.style.display = 'none';
      }
    });

    const targetModal = modalContents[modalType];
    if (targetModal) {
      targetModal.style.display = 'block';
      modalBackdrop!.classList.add('is-active');
      modalBackdrop!.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';

      // Focus first input or button inside target modal
      const firstInput = targetModal.querySelector<HTMLElement>('input, select, button');
      if (firstInput) {
        firstInput.focus();
      }
    }
  }

  /**
   * Closes any open modal and restores body scrolling.
   */
  function closeModal(): void {
    modalBackdrop!.classList.remove('is-active');
    modalBackdrop!.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  // Bind modal open trigger buttons
  const openTriggers = document.querySelectorAll<HTMLElement>('[data-open-modal]');
  openTriggers.forEach((trigger: HTMLElement) => {
    trigger.addEventListener('click', (event: MouseEvent) => {
      event.preventDefault();
      const modalType = trigger.getAttribute('data-open-modal') as ModalType | null;
      if (modalType && modalType in modalContents) {
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

  // Close when clicking directly on backdrop
  modalBackdrop.addEventListener('click', (event: MouseEvent) => {
    if (event.target === modalBackdrop) {
      closeModal();
    }
  });

  // Close when pressing the Escape key
  document.addEventListener('keydown', (event: KeyboardEvent) => {
    if (event.key === 'Escape' && modalBackdrop.classList.contains('is-active')) {
      closeModal();
    }
  });

  // Handle demo forms submission without page reload
  const demoForms = document.querySelectorAll<HTMLFormElement>('.modal-form');
  demoForms.forEach((form: HTMLFormElement) => {
    form.addEventListener('submit', (event: SubmitEvent) => {
      event.preventDefault();
      const feedback = form.querySelector<HTMLElement>('.form-demo-feedback');
      if (feedback) {
        feedback.style.display = 'block';
      }
    });
  });
}
