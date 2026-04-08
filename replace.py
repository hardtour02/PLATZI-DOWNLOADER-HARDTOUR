import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace sidebar
text = re.sub(r'<nav class="nav-sidebar">.*?</nav>', "{% include 'components/_sidebar.jinja2' %}", text, flags=re.DOTALL)

# Replace sections
text = re.sub(r'<section id="view-([^"]+)".*?</section>', r"{% include 'components/_view_\1.jinja2' %}", text, flags=re.DOTALL)

# Replace fonts and css
head_additions = """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link href="/assets/carbon-neon.css" rel="stylesheet">
"""
text = text.replace('<link href="/assets/assetsmenu/inter.css" rel="stylesheet">', head_additions)

# Update main-content margin-left
text = text.replace('margin-left: 240px;', 'margin-left: 180px;')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacement complete.")
