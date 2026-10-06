/**
 * MediSight AI - Modal Manager
 * Accessible modal handler for Patient Login, Doctor Login, and Registration demo dialogs.
 */

export function setupModals() {
  const modalBackdrop = document.getElementById('modal-backdrop');
  if (!modalBackdrop) return;

  const modalContents = {
    'doctor-login': document.getElementById('modal-doctor-login'),
    'patient-login': document.getElementById('modal-patient-login'),
    'register': document.getElementById('modal-register')
  };

  function openModal(modalType) {
    // Hide all modal views
    Object.values(modalContents).forEach(m => {
      if (m) m.style.display = 'none';
    });

    const targetModal = modalContents[modalType];
    if (targetModal) {
      targetModal.style.display = 'block';
      modalBackdrop.classList.add('is-active');
      modalBackdrop.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';

      // Focus first input if available
      const firstInput = targetModal.querySelector('input, select, button');
      if (firstInput) firstInput.focus();
    }
  }

  function closeModal() {
    modalBackdrop.classList.remove('is-active');
    modalBackdrop.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  // Trigger buttons
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

  // Escape key handler
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalBackdrop.classList.contains('is-active')) {
      closeModal();
    }
  });

  // Demo form submit prevent default
  document.querySelectorAll('.modal-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const feedback = form.querySelector('.form-demo-feedback');
      if (feedback) {
        feedback.style.display = 'block';
      }
      if (form.closest('#modal-doctor-login')) {
        setTimeout(() => {
          window.location.href = 'doctor-dashboard.html';
        }, 300);
      }
      if (form.closest('#modal-patient-login')) {
        setTimeout(() => {
          window.location.href = 'patient-dashboard.html';
        }, 300);
      }
    });
  });
}
