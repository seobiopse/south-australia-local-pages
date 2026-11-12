"""Prepare customer logos for the local pages and keep the logo manifest up to date.

Workflow
  1. Drop the logo files you have into data/customers/logos-raw/ (png, jpg, webp or svg). Name each file after the
     customer, e.g. "Hoppers Elite Cricket Club.png" or "hoppers-elite-cricket-club.png" (the name is matched by slug).
  2. Run:  python scripts/prepare_logos.py
     - raster logos are trimmed of blank margins and saved as square 512x512 PNG (transparent, 32px padding),
       named <slug>.png in assets/img/customers/  (SVG logos are copied as <slug>.svg)
     - data/customers/logos-manifest.csv is rewritten: every customer, its asset name, whether the logo is present,
       and the pages it appears on. Source and permission columns are preserved so they can be filled in.
  3. Run scripts/build_vic.py and scripts/build_sa.py. Cards show the logo when <slug>.png/.svg exists, else initials.

The card tile is always a fixed 64px square (CSS: .proof-ava), so 512px assets stay sharp on high-density screens.
"""
import csv
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_vic as V  # noqa: E402

try:
    from PIL import Image, ImageChops
except ImportError:  # pragma: no cover
    Image = None

ROOT = V.ROOT
RAW = os.path.join(ROOT, 'data', 'customers', 'logos-raw')
OUT = V.LOGO_DIR
MANIFEST = os.path.join(ROOT, 'data', 'customers', 'logos-manifest.csv')
SIZE, PAD = 512, 32
RASTER = ('.png', '.jpg', '.jpeg', '.webp')


def customers():
    """Return {customer name: [pages it appears on]} from the Victoria and SA customer lists."""
    out = {}

    def add(n, page):
        out.setdefault(n, [])
        if page not in out[n]:
            out[n].append(page)

    for n in V.HUB_LARGE + V.HUB_CLUBS:
        add(n, 'victoria/melbourne')
    for slug, names in V.PROOF.items():
        page = 'victoria/melbourne' if slug == 'melbourne' else (
            'victoria/melbourne/%s' % slug if slug in V.SUB else 'victoria/%s' % slug)
        for n in names:
            add(n, page)
    sa_file = os.path.join(ROOT, 'data', 'sa', 'sa_proof.json')
    if os.path.isfile(sa_file):
        import json
        with open(sa_file, encoding='utf-8') as f:
            sa = {k: v for k, v in json.load(f).items() if not k.startswith('_')}
        sa_subs = {s['slug'] for s in json.load(open(os.path.join(ROOT, 'data', 'sa', 'sa_locations.json'), encoding='utf-8'))['suburbs']}
        for slug, names in sa.items():
            page = 'south-australia/adelaide/%s' % slug if slug in sa_subs else 'south-australia/%s' % slug
            for n in names:
                add(n, page)
    return out


def make_square(src, dst):
    im = Image.open(src)
    im.load()
    im = im.convert('RGBA')
    w0, h0 = im.size
    # trim blank margins: transparent pixels, or near-white pixels when there is no transparency
    alpha = im.getchannel('A')
    if alpha.getextrema()[0] < 250:
        box = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    else:
        rgb = im.convert('RGB')
        diff = ImageChops.difference(rgb, Image.new('RGB', rgb.size, (255, 255, 255))).convert('L')
        box = diff.point(lambda v: 255 if v > 12 else 0).getbbox()
    if box:
        im = im.crop(box)
    inner = SIZE - 2 * PAD
    scale = min(inner / im.width, inner / im.height)
    nw, nh = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    canvas.paste(im, ((SIZE - nw) // 2, (SIZE - nh) // 2), im)
    canvas.save(dst, 'PNG', optimize=True)
    return (w0, h0)


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    cust = customers()
    by_slug = {V.customer_slug(n): n for n in cust}
    done, unknown, lowres = [], [], []
    for fn in sorted(os.listdir(RAW)):
        stem, ext = os.path.splitext(fn)
        ext = ext.lower()
        if ext not in RASTER + ('.svg',):
            continue
        slug = V.customer_slug(stem)
        if slug not in by_slug:
            unknown.append(fn)
            continue
        src = os.path.join(RAW, fn)
        if ext == '.svg':
            shutil.copyfile(src, os.path.join(OUT, slug + '.svg'))
        elif Image is None:
            print('Pillow is required to process raster logos (pip install pillow)')
            return 1
        else:
            w, h = make_square(src, os.path.join(OUT, slug + '.png'))
            if max(w, h) < 256:
                lowres.append('%s (%dx%d)' % (fn, w, h))
        done.append(slug)
    # keep any source / permission notes already in the manifest
    keep = {}
    if os.path.isfile(MANIFEST):
        with open(MANIFEST, encoding='utf-8-sig', newline='') as f:
            for r in csv.DictReader(f):
                keep[r['slug']] = (r.get('source_url', ''), r.get('permission', ''))
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    have = 0
    with open(MANIFEST, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['customer', 'slug', 'asset_file', 'status', 'shown_on', 'source_url', 'permission'])
        for n in sorted(cust, key=str.lower):
            slug = V.customer_slug(n)
            lf = V.logo_file(n)
            have += 1 if lf else 0
            src, perm = keep.get(slug, ('', ''))
            w.writerow([n, slug, lf or slug + '.png', 'present' if lf else 'missing', '; '.join(cust[n]), src, perm])
    print('customers: %d | logos present: %d | missing: %d' % (len(cust), have, len(cust) - have))
    print('processed this run: %d' % len(done))
    if unknown:
        print('raw files that match no customer (rename to the customer name or slug):', ', '.join(unknown))
    if lowres:
        print('low resolution (under 256px, will look soft; send a larger file):', ', '.join(lowres))
    print('manifest: %s' % os.path.relpath(MANIFEST, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
