import re
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import json
parts = {}

# Find sidebar
nav_match = re.search(r'<nav class="nav-sidebar">.*?</nav>', text, flags=re.DOTALL)
if nav_match:
    parts['sidebar'] = nav_match.group(0)

# Find sections
sections = re.finditer(r'<section id="view-([^"]+)".*?</section>', text, flags=re.DOTALL)
for s in sections:
    parts[f'view_{s.group(1)}'] = s.group(0)

print(json.dumps(list(parts.keys())))

# Write extractions
import os
os.makedirs('frontend/components', exist_ok=True)
for k, v in parts.items():
    with open(f'frontend/components/_{k}.jinja2', 'w', encoding='utf-8') as f:
        f.write(v)

print("done")
