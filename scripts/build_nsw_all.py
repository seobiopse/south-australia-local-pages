"""Generate every NSW page: state, Sydney hub, 20 Sydney suburbs/areas, 35 NSW towns.

Run:  python build_nsw_all.py   then   python build_nav.py   then   python check_unique.py

Data:  data/nsw_locations.json (towns, suburbs), data/sports.json (product tiles).
Shared chrome comes from trophies/victoria/index.html via build_nsw.py.
"""
import json
import os
from html import escape

import build_nsw as B

ROOT = B.ROOT
SITE = B.SITE
IMG = B.IMG
PHONE = B.PHONE

with open(os.path.join(ROOT, 'data', 'shared', 'sports.json'), encoding='utf-8') as f:
    SPORTS = json.load(f)

SPORT_NAME = {
    'rugby': 'rugby league and union', 'rugbymedals': 'rugby medals', 'lifesaving': 'surf life saving',
    'swimming': 'swimming', 'basketball': 'basketball', 'golf': 'golf', 'soccer': 'soccer', 'afl': 'AFL',
    'netball': 'netball', 'cricket': 'cricket', 'tennis': 'tennis', 'athletics': 'athletics', 'hockey': 'hockey',
    'equestrian': 'equestrian', 'lawnbowls': 'lawn bowls', 'rowing': 'rowing', 'fishing': 'fishing',
    'dance': 'dance', 'motorsports': 'motorsport', 'sailing': 'sailing', 'cycling': 'cycling',
    'schoolmedals': 'school medals', 'plaques': 'corporate plaques',
}

TOWN_BY_SLUG = {t['slug']: t for t in B.TOWNS}
SUB_BY_SLUG = {s['slug']: s for s in B.SUBS}
STORE_BY_KEY = {s['key']: s for s in B.STORES}


def words(keys):
    names = [SPORT_NAME[k] for k in keys]
    if len(names) <= 2:
        return ' and '.join(names)
    return ', '.join(names[:-1]) + ' and ' + names[-1]


def tiles(keys, depth):
    out = []
    for k in keys:
        sp = SPORTS[k]
        out.append('<a class="cat-tile" href="%s/products/%s"><div class="thumb"><img src="%s%s%s" alt="%s" loading="lazy" width="140" height="140"></div>\n'
                   '      <div class="body"><h3>%s</h3><p>%s</p><span class="from">From $%s</span></div></a>'
                   % (SITE, sp['path'], '../' * depth, IMG, sp['img'], escape(sp['alt']), sp['title'], sp['blurb'], sp['from']))
    return '\n'.join(out)


def fmt_pop(n):
    return '{:,}'.format(int(round(n, -2)))


def growth_text(g):
    if g >= 0:
        return 'up %.1f%%' % g
    return 'down %.1f%%' % abs(g)


def neighbours(t, n=4):
    toks = {w.strip().lower() for w in t['region'].replace(',', ' ').split(' ') if len(w) > 3}
    cands = []
    for o in B.TOWNS:
        if o['slug'] == t['slug']:
            continue
        otoks = {w.strip().lower() for w in o['region'].replace(',', ' ').split(' ') if len(w) > 3}
        shared = len(toks & otoks)
        cands.append((-shared, abs(o['km'] - t['km']), o['slug']))
    cands.sort()
    return [TOWN_BY_SLUG[c[2]] for c in cands[:n]]


def store_text(key):
    if key == 'both':
        return ('Either of our two Sydney locations is within reach: %s, or %s.' % (B.addr(B.STORES[0]), B.addr(B.STORES[1])))
    s = STORE_BY_KEY[key]
    return 'The closer of our two Sydney locations is %s (%s).' % (s['name'], B.addr(s))


def page(pre, footer, depth, title, desc, canon, body, graph):
    return (B.head(pre, title, desc, canon, depth) + body + B.fix_footer(footer, depth) +
            B.ld({'@context': 'https://schema.org', '@graph': graph}) +
            '\n<script src="%sassets/js/nav.js" defer></script></body></html>\n' % ('../' * depth))


HERO_GUARANTEES = '''    <div class="hero-guarantees">
      <div class="guarantee-item"><i class="fa-solid fa-shield-halved"></i><div><strong>Trusted since 1985</strong><span>Australian-owned</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-bolt"></i><div><strong>3–5 days production</strong><span>Rush from day 3</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-award"></i><div><strong>No minimum order</strong><span>One trophy or hundreds</span></div></div>
    </div>'''

FOOT_STRIP = '''<div style="background:#fff;padding:22px 0;border-top:1px solid var(--border);font-size:14.5px"><div class="wrap">
  %s
</div></div>'''


def hero(depth, h1_name, lead, chip, hero_key, cta2_href, cta2_label):
    sp = SPORTS[hero_key]
    return '''<header class="hero"><div class="wrap hero-grid">
  <div class="hero-content">
    <div class="hero-badge-row"><span class="hero-tag"><i class="fa-solid fa-check"></i> Free engraving</span><span class="hero-local-chip"><i class="fa-solid fa-location-dot"></i> %s</span></div>
    <h1>Custom Trophies in <span class="gold">%s</span></h1>
    <p class="lead">%s</p>
    <div class="hero-ctas">
      <a class="btn-primary" href="%s/products/trophies"><span>Shop trophies</span><i class="fa-solid fa-arrow-right"></i></a>
      <a class="btn-secondary" href="%s"><i class="fa-solid fa-map-pin"></i><span>%s</span></a>
    </div>
%s
  </div>
  <div class="hero-visual"><div class="hero-visual-card">
    <img src="%s%s%s" alt="%s" width="300" height="300">
    <div class="hero-badge-overlay"><div><div style="font-size:13px;font-weight:700;color:#fff">4.9 ★ Google rating</div><div style="font-size:12px;color:#d1d5db">232 reviews across all stores</div></div></div>
  </div></div>
</div></header>''' % (escape(chip), escape(h1_name), escape(lead), SITE, cta2_href, cta2_label, HERO_GUARANTEES,
                      '../' * depth, IMG, sp['img'], escape(sp['alt']))


# ---------------------------------------------------------------------------
# Town page (depth 3)
# ---------------------------------------------------------------------------

def town_page(t, idx):
    depth = 3
    pre, footer = B.chrome(depth)
    name = t['name']
    canon = '%s/trophies/new-south-wales/%s/' % (SITE, t['slug'])
    title = 'Trophies in %s | Alpha Trophies' % name
    desc = ('Custom trophies, medals and plaques delivered to %s. Free engraving, $9.90 flat-rate shipping, no minimum order.' % name)
    km = '{:,}'.format(t['km'])
    pop = fmt_pop(t['pop'])
    first_occ = t['occasion']
    faqs = [
        ('Do you deliver trophies to %s?' % name,
         'Yes. %s is about %s km from Sydney by road, and we deliver there with standard shipping at a $9.90 flat rate or express at $25, after 5 working days production.' % (name, km)),
        ('Can you make %s trophies for %s clubs?' % (SPORT_NAME[t['sports'][0]], name),
         'Yes. %s and %s are among the most popular categories for %s, and every item includes free engraving. There is no minimum order.' % (
             SPORT_NAME[t['sports'][0]].capitalize(), SPORT_NAME[t['sports'][1]], name)),
        ('How fast can I get trophies to %s for a presentation day?' % name,
         'Standard production is 5 working days, plus delivery to %s. Fast Track is 4 working days ($40 plus 10%% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15%% of the order, capped at $300), also plus delivery. Tell us the event date when you order.' % name),
        ('Where is the nearest Alpha Trophies store to %s?' % name,
         'Our NSW stores are in Sydney: %s and %s. You do not need to visit; order online and we deliver to %s.' % (B.addr(B.STORES[0]), B.addr(B.STORES[1]), name)),
        ('Is engraving free?', 'Yes, free engraving on every order.'),
    ]
    nb = neighbours(t)
    near_chips = ''.join('<a class="chip" href="../%s/" style="text-decoration:none">%s</a>' % (o['slug'], escape(o['name'])) for o in nb)
    body = '''
%(crumbs)s

%(hero)s

<section class="sec sec-alt"><div class="wrap copy-two">
  <div><h3>Delivered to %(name)s</h3>
  <p>%(name)s is about %(km)s km from Sydney by road. Every order is engraved in-house, then sent by standard shipping at a $9.90 flat rate or express at $25, after 5 working days production.</p>
  <p>%(name)s has about %(pop)s residents (ABS estimate, June 2025), %(growth)s over the past ten years.</p></div>
  <div><h3>Running to a deadline?</h3>
  <p>Fast Track (4 working days) and Priority Rush (3 working days) are available at checkout. Tell us the date of your event and we will confirm the right option.</p>
  <p>We regularly see orders from the %(region)s for %(occ)s.</p></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Popular in %(name)s</span><h2 class="sec-title">Trophies for %(name)s clubs and schools</h2>
  <p class="sec-sub">%(sportline)s Every item includes free engraving.</p></div>
  <div class="tile-grid" style="grid-template-columns:repeat(4,1fr)">
      %(tiles)s
  </div>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(region)s</span><h2 class="sec-title">Also delivering nearby</h2></div>
  <div class="chip-list" style="justify-content:center">%(near)s</div>
  <p style="text-align:center;margin-top:24px;font-size:15px;color:var(--text-muted)">Order online and we deliver. Questions? Call <a href="tel:1300485645" style="color:var(--navy-900);font-weight:700">%(phone)s</a> or email <a href="mailto:sales@alphatrophies.com.au" style="color:var(--navy-900);font-weight:700">sales@alphatrophies.com.au</a>. Our NSW stores are in <a href="../sydney/" style="color:var(--navy-900);font-weight:700">Sydney</a>.</p>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(name)s</span><h2 class="sec-title">%(name)s trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

%(foot)s

''' % {'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('New South Wales', '../'), (escape(name), None)]),
       'hero': hero(depth, name, '%s Engraved in-house and delivered to %s clubs, schools and businesses.' % (t['blurb'], name),
                    t['region'], t['sports'][0], '#faq', 'Delivery and FAQs'),
       'name': escape(name), 'km': km, 'pop': pop, 'growth': growth_text(t['growth']), 'region': escape(t['region']),
       'occ': escape(first_occ), 'sportline': escape(t['sportline']), 'tiles': tiles(t['sports'], depth),
       'near': near_chips, 'phone': PHONE, 'faq': B.faq_html(faqs),
       'foot': FOOT_STRIP % '<a href="../" style="color:var(--navy-900);font-weight:700"><i class="fa-solid fa-arrow-left"></i> All NSW trophies</a>'
                            '<span style="margin:0 10px;color:#cbd5e1">|</span><a href="../sydney/" style="color:var(--navy-900);font-weight:700">Sydney stores</a>'}
    body = body.replace('<section class="sec"><div class="wrap">\n  <div class="sec-header"><span class="sec-eyebrow">%s</span>' % escape(name),
                        '<section id="faq" class="sec"><div class="wrap">\n  <div class="sec-header"><span class="sec-eyebrow">%s</span>' % escape(name), 1)
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                             ('New South Wales', SITE + '/trophies/new-south-wales/'), (name, canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies in %s' % name, 'url': canon,
         'about': {'@type': 'City', 'name': name}},
        B.faq_schema(faqs),
    ]
    return page(pre, footer, depth, title, desc, canon, body, graph)


# ---------------------------------------------------------------------------
# Suburb page (depth 4)
# ---------------------------------------------------------------------------

def suburb_page(s, idx):
    depth = 4
    pre, footer = B.chrome(depth)
    name = s['name']
    canon = '%s/trophies/new-south-wales/sydney/%s/' % (SITE, s['slug'])
    title = 'Trophies in %s, Sydney | Alpha Trophies' % name
    desc = ('Custom trophies, medals and plaques for %s, Sydney. Free engraving, $9.90 flat-rate delivery, no minimum order.' % name)
    storeline = store_text(s['store'])
    faqs = [
        ('Which Alpha Trophies store is closest to %s?' % name, storeline + ' Order online and we deliver to %s.' % name),
        ('Do you deliver trophies to %s?' % name,
         'Yes. Standard shipping to %s is a $9.90 flat rate and express is $25, after 5 working days production.' % name),
        ('Can I order %s trophies for a %s club or school?' % (SPORT_NAME[s['sports'][0]], name),
         'Yes. %s is one of the most popular categories in the area, alongside %s. Every item includes free engraving and there is no minimum order.' % (
             SPORT_NAME[s['sports'][0]].capitalize(), words(s['sports'][1:]))),
        ('How fast can I get trophies for %s?' % name,
         'Fast Track is 4 working days ($40 plus 10% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15% of the order, capped at $300). Tell us your event date when you order.'),
    ]
    near = [SUB_BY_SLUG[n] for n in s['near']]
    near_chips = ''.join('<a class="chip" href="../%s/" style="text-decoration:none">%s</a>' % (o['slug'], escape(o['name'])) for o in near)
    if s['store'] == 'both':
        stores = B.STORES
    else:
        stores = [STORE_BY_KEY[s['store']]]
    store_cards = ''.join(
        '<div class="store-location"><div class="store-icon-wrap"><i class="fa-solid fa-shop"></i></div>'
        '<div class="store-details"><h4>%s</h4><p>%s</p></div>'
        '<div class="store-actions"><a class="btn-store-action" href="%s" target="_blank" rel="noopener"><i class="fa-solid fa-location-arrow"></i> Google Maps</a></div></div>'
        % (st['name'], escape(B.addr(st)), B.gmaps(st)) for st in stores)
    body = '''
%(crumbs)s

%(hero)s

<div class="store-bar"><div class="wrap store-bar-inner two-stores">
  %(store_cards)s
</div></div>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Popular in %(name)s</span><h2 class="sec-title">Trophies for %(name)s clubs and schools</h2>
  <p class="sec-sub">%(sportline)s Every item includes free engraving.</p></div>
  <div class="tile-grid" style="grid-template-columns:repeat(4,1fr)">
      %(tiles)s
  </div>
</div></section>

<section class="sec sec-alt"><div class="wrap copy-two">
  <div><h3>Delivered to %(name)s</h3>
  <p>%(storeline)s Order online, we engrave in-house, and your order is delivered to %(name)s.</p>
  <p>Standard shipping is a $9.90 flat rate and express is $25, after 5 working days production. Fast Track (4 working days) and Priority Rush (3 working days) are available at checkout.</p></div>
  <div><h3>Orders from %(name)s</h3>
  <p>%(blurb)s</p>
  <p>Typical orders include %(occ)s.</p></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(region)s</span><h2 class="sec-title">Nearby Sydney areas</h2></div>
  <div class="chip-list" style="justify-content:center">%(near)s</div>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(name)s</span><h2 class="sec-title">%(name)s trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

%(foot)s

''' % {'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('New South Wales', '../../'), ('Sydney', '../'), (escape(name), None)]),
       'hero': hero(depth, name, '%s Engraved in-house and delivered to %s clubs, schools and businesses.' % (s['blurb'], name),
                    s['region'], s['sports'][0], '#store', 'Nearest store'),
       'store_cards': store_cards, 'name': escape(name), 'sportline': escape(s['sportline']),
       'tiles': tiles(s['sports'], depth), 'storeline': escape(storeline), 'blurb': escape(s['blurb']),
       'occ': escape(s['occasion']), 'region': escape(s['region']), 'near': near_chips, 'faq': B.faq_html(faqs),
       'foot': FOOT_STRIP % '<a href="../" style="color:var(--navy-900);font-weight:700"><i class="fa-solid fa-arrow-left"></i> Trophies in Sydney</a>'
                            '<span style="margin:0 10px;color:#cbd5e1">|</span><a href="../../" style="color:var(--navy-900);font-weight:700">All NSW trophies</a>'}
    body = body.replace('<div class="store-bar">', '<div class="store-bar" id="store">', 1)
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                             ('New South Wales', SITE + '/trophies/new-south-wales/'),
                             ('Sydney', SITE + '/trophies/new-south-wales/sydney/'), (name, canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies in %s' % name, 'url': canon,
         'about': {'@type': 'Place', 'name': '%s, Sydney' % name}},
        B.faq_schema(faqs),
    ]
    return page(pre, footer, depth, title, desc, canon, body, graph)


def main():
    B.write('trophies/new-south-wales/index.html', B.state_page())
    B.write('trophies/new-south-wales/sydney/index.html', B.sydney_page())
    for i, s in enumerate(B.SUBS):
        B.write('trophies/new-south-wales/sydney/%s/index.html' % s['slug'], suburb_page(s, i))
    for i, t in enumerate(B.TOWNS):
        B.write('trophies/new-south-wales/%s/index.html' % t['slug'], town_page(t, i))
    # sitemap
    urls = ['/trophies/victoria/', '/trophies/victoria/melbourne/', '/trophies/new-south-wales/', '/trophies/new-south-wales/sydney/']
    urls += ['/trophies/new-south-wales/sydney/%s/' % s['slug'] for s in B.SUBS]
    urls += ['/trophies/new-south-wales/%s/' % t['slug'] for t in B.TOWNS]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += ['  <url><loc>%s%s</loc></url>' % (SITE, u) for u in urls]
    xml.append('</urlset>')
    with open(os.path.join(ROOT, 'sitemaps', 'sitemap-local.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(xml) + '\n')
    print('%d URLs in sitemap-local.xml' % len(urls))


if __name__ == '__main__':
    main()
