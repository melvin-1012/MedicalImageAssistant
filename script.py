import re
with open('index.html', 'r', encoding='utf-8') as f:
    print(re.findall(r'<form[^>]*id="([^"]+)"', f.read()))
