"""Inject the shared mega-menu (with "Popular right now") into every local page.

Source of truth: data/menu.json. Edit that file, then run:  python build_nav.py
Idempotent: replaces the <nav aria-label="Main">...</nav> block on every page under trophies/.

Today: one "popular" list per top-level category (7 links max).
Later: add a "children" map in menu.json (sub-category label -> its own popular list)
and the renderer below will emit one panel per sub-category. See render_panel().
"""
import json
import os
import re
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# First run: the plain <nav aria-label="Main"> inside .header-main. Later runs: the marked mm-bar block.
OLD_NAV_RE = re.compile(r'\s*<nav aria-label="Main"[^>]*>.*?</nav>', re.S)
BAR_RE = re.compile(r'<!--mm-bar-->.*?<!--/mm-bar-->', re.S)
SCRIPT_TAG = '<script src="%sassets/js/nav.js" defer></script>'
SCRIPT_RE = re.compile(r'<script src="[^"]*assets/js/nav\.js" defer></script>')


def render_panel(item):
    """One mega panel. Reused later for sub-category panels by passing a child dict with the same keys."""
    popular = ''
    if item.get('popular'):
        links = ''.join('<a href="%s">%s</a>' % (escape(l['href']), escape(l['label'])) for l in item['popular'])
        popular = ('<div class="mm-foot"><span class="mm-eyebrow">Popular right now</span>'
                   '<div class="mm-pop">%s</div></div>' % links)
    return ('<div class="mm-panel" id="mm-%s"><div class="wrap mm-inner">'
            '<div class="mm-title">%s</div><p class="mm-blurb">%s</p>'
            '<a class="mm-browse" href="%s">%s</a>%s</div></div>'
            % (slug(item['label']), escape(item['label']), escape(item['blurb']),
               escape(item['href']), escape(item['cta']), popular))


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def render_nav(data):
    out = ['<nav aria-label="Main" class="mm-nav"><button class="mm-toggle" type="button" '
           'aria-expanded="false" aria-controls="mm-list"><span>Menu</span></button>'
           '<ul class="mm-list" id="mm-list"><li><a class="mm-link" href="https://alphatrophies.com.au/">Home</a></li>']
    for item in data['items']:
        out.append('<li class="mm-item"><button class="mm-btn" type="button" aria-expanded="false" '
                   'aria-controls="mm-%s">%s<svg viewBox="0 0 24 24" aria-hidden="true">'
                   '<polyline points="6 9 12 15 18 9"></polyline></svg></button>%s</li>'
                   % (slug(item['label']), escape(item['label']), render_panel(item)))
    out.append('</ul></nav>')
    return ''.join(out)


def main():
    with open(os.path.join(ROOT, 'data', 'shared', 'menu.json'), encoding='utf-8') as f:
        nav = render_nav(json.load(f))
    changed = 0
    for dirpath, _, files in os.walk(os.path.join(ROOT, 'trophies')):
        if 'index.html' not in files:
            continue
        path = os.path.join(dirpath, 'index.html')
        with open(path, encoding='utf-8') as f:
            html = f.read()
        if not (BAR_RE.search(html) or OLD_NAV_RE.search(html)) or '</header>' not in html:
            print('no nav block:', path)
            continue
        depth = os.path.relpath(dirpath, ROOT).count(os.sep) + 1
        prefix = '../' * depth
        bar = '<!--mm-bar--><div class="mm-bar"><div class="wrap">%s</div></div><!--/mm-bar-->' % nav
        html = BAR_RE.sub('', html)
        html = OLD_NAV_RE.sub('', html, count=1)
        html = html.replace('</header>', bar + '</header>', 1)
        html = SCRIPT_RE.sub('', html)
        html = html.replace('</body>', SCRIPT_TAG % prefix + '</body>', 1)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        changed += 1
        print('updated', os.path.relpath(path, ROOT))
    print('%d page(s) updated' % changed)


if __name__ == '__main__':
    main()
