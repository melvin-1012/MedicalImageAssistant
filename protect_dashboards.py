import os

def prepend_auth_guard(filepath, role_condition, alert_msg):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already guarded
    if "window.MediSightAPI.getToken()" in content[:500]:
        print(f"Already protected: {filepath}")
        return
        
    guard = f"""(function() {{
  if (!window.MediSightAPI) return;
  const token = window.MediSightAPI.getToken();
  const user = window.MediSightAPI.getCurrentUser();
  if (!token || !user || !({role_condition})) {{
    alert("{alert_msg}");
    window.location.replace('index.html');
  }}
}})();\n\n"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(guard + content)
    print(f"Protected {filepath}")

prepend_auth_guard('js/doctor-dashboard.js', 'user.role === "doctor"', 'Access Denied: You must be logged in as a doctor.')
prepend_auth_guard('js/patient-dashboard.js', 'user.role === "patient"', 'Access Denied: You must be logged in as a patient.')
prepend_auth_guard('js/specialist-imaging.js', 'user.role === "specialist" || user.role === "admin" || user.role === "doctor"', 'Access Denied: You must be logged in as a specialist.')
