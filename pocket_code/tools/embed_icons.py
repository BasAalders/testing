# Usage: python3 tools/embed_icons.py index.html path/to/codicon.css path/to/codicon.ttf
# (codicon files come from: npm pack @vscode/codicons@0.0.36)
# Embed a subset of the Codicons font (CC BY 4.0, Microsoft) holding only the icons index.html uses.
import re, sys, base64, io
from fontTools import subset
from fontTools.ttLib import TTFont
html_path, css_path, ttf_path = sys.argv[1:4]
html = open(html_path, encoding='utf-8').read()
css = open(css_path, encoding='utf-8').read()
available = dict(re.findall(r'\.codicon-([a-z0-9-]+):before\s*\{\s*content:\s*"\\([0-9a-f]+)"', css))
words = set(re.findall(r"ci-([a-z0-9-]+)", html)) | set(re.findall(r"'([a-z0-9-]+)'", html))
words |= {'chevron-' + d for d in ('left', 'right', 'up', 'down')} | {'bell', 'bell-dot'}
names = sorted(n for n in words if n in available)
rules = ['.ci-%s:before { content: "\\%s"; }' % (n, available[n]) for n in names]
font = TTFont(ttf_path)
opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = []; opts.name_IDs = ['*']
sub = subset.Subsetter(opts); sub.populate(unicodes=[int(available[n], 16) for n in names]); sub.subset(font)
buf = io.BytesIO(); font.flavor = 'woff2'; font.save(buf)
b64 = base64.b64encode(buf.getvalue()).decode()
html = re.sub(r'data:font/woff2;base64,[A-Za-z0-9+/=_]+', 'data:font/woff2;base64,' + b64, html, count=1)
block = '/*codicon-rules*/\n' + '\n'.join(rules) + '\n/*end-codicon-rules*/'
if '/*__CODICON_RULES__*/' in html: html = html.replace('/*__CODICON_RULES__*/', block)
elif '/*codicon-rules*/' in html: html = re.sub(r'/\*codicon-rules\*/.*?/\*end-codicon-rules\*/', lambda m: block, html, flags=re.S)
else:
    html = re.sub(r'(\.ci-[a-z0-9-]+:before \{ content: "\\[0-9a-f]+"; \}\n?)+', lambda m: block + '\n', html, count=1)
open(html_path, 'w', encoding='utf-8').write(html)
print('icons:', len(names), 'font bytes:', len(buf.getvalue()))
