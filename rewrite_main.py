import io

new_code = """document.querySelectorAll('.modal-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const feedback = form.querySelector('.form-demo-feedback');
      const submitBtn = form.querySelector('button[type="submit"]');

      if (submitBtn) submitBtn.disabled = true;

      try {
        if (form.closest('#modal-doctor-login')) {
          const docIdInput = form.querySelector('#doc-id');
          const passInput = form.querySelector('#doc-password');
          const emailVal = docIdInput ? docIdInput.value.trim() : '';
          const passwordVal = passInput ? passInput.value : '';

          if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#0284c7';
            feedback.innerText = 'Authenticating with backend...';
          }

          if (window.MediSightAPI) {
            await window.MediSightAPI.login(emailVal, passwordVal);
            const user = window.MediSightAPI.getCurrentUser();
            if (user && user.role !== 'doctor') {
               throw new Error("Access denied: Not a doctor account.");
            }
          }

          if (feedback) {
            feedback.innerText = 'Authenticated! Opening Doctor Workspace...';
            feedback.style.color = '#10b981';
          }
          setTimeout(() => { window.location.href = 'doctor-dashboard.html'; }, 400);
        }
        else if (form.closest('#modal-patient-login')) {
          const mrnInput = form.querySelector('#pat-mrn');
          const passInput = form.querySelector('#pat-password');
          const emailVal = mrnInput ? mrnInput.value.trim() : '';
          const passwordVal = passInput ? passInput.value : '';

          if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#0284c7';
            feedback.innerText = 'Connecting to Health Portal Database...';
          }

          if (window.MediSightAPI) {
             await window.MediSightAPI.login(emailVal, passwordVal);
             const user = window.MediSightAPI.getCurrentUser();
             if (user && user.role !== 'patient') {
                 throw new Error("Access denied: Not a patient account.");
             }
          }

          if (feedback) {
            feedback.innerText = 'Patient record verified! Opening Health Portal...';
            feedback.style.color = '#10b981';
          }
          setTimeout(() => { window.location.href = 'patient-dashboard.html'; }, 400);
        }
        else if (form.closest('#modal-register')) {
          const roleSelect = form.querySelector('#reg-role');
          const nameInput = form.querySelector('#reg-name');
          const emailInput = form.querySelector('#reg-email');
          const passInput = form.querySelector('#reg-password');

          const role = roleSelect ? roleSelect.value : 'patient';
          const fullName = nameInput ? nameInput.value.trim() : 'New User';
          const email = emailInput ? emailInput.value.trim() : '';
          const passwordVal = passInput ? passInput.value : '';

          if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#0284c7';
            feedback.innerText = 'Registering account in hospital database...';
          }

          if (window.MediSightAPI) {
             await window.MediSightAPI.signup({
               email: email,
               password: passwordVal,
               full_name: fullName,
               role: role === 'staff' ? 'specialist' : role,
             });
             await window.MediSightAPI.login(email, passwordVal);
          }

          if (feedback) {
            feedback.innerText = 'Registered! Redirecting...';
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
          }, 400);
        }
        else if (form.closest('#modal-appointment')) {
          if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#0284c7';
            feedback.innerText = 'Checking doctor availability...';
          }
          setTimeout(() => {
            if (feedback) {
              feedback.innerText = 'Appointment Scheduled Successfully!';
              feedback.style.color = '#10b981';
            }
            form.reset();
            setTimeout(() => {
              const modal = form.closest('[id^="modal-"]');
              if (modal) {
                 modal.style.display = 'none';
                 document.getElementById('modal-backdrop').classList.remove('is-active');
                 document.getElementById('modal-backdrop').setAttribute('aria-hidden', 'true');
                 document.body.style.overflow = '';
              }
            }, 1500);
          }, 1500);
        }
      } catch (err) {
         if (feedback) {
            feedback.style.display = 'block';
            feedback.style.color = '#ef4444';
            feedback.innerText = err.message || 'Authentication failed';
         }
      } finally {
         if (submitBtn) submitBtn.disabled = false;
      }
    });
  });"""

with io.open('js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

start_marker = "document.querySelectorAll('.modal-form').forEach(form => {"
end_marker = "    });\n  });\n}\n\n//"

start_idx = js.find(start_marker)
end_idx = js.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    js = js[:start_idx] + new_code + "\n}\n\n//" + js[end_idx + len(end_marker):]
    with io.open('js/main.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Success")
else:
    print("Failed to find markers")
