"""Generate every Victoria page: state hub, upgraded Melbourne hub, 19 Melbourne suburbs, 20 Victorian towns.

Run (from anywhere):
    python scripts/scrape_vic_products.py   # optional, refreshes live products/prices
    python scripts/build_vic.py
    python scripts/build_nav.py             # injects the Trophies/Medals menu
    python scripts/check_unique.py          # writes docs/nsw/NSW-UNIQUENESS.md (all local pages)

Data:  data/victoria/vic_locations.json (suburbs, towns, drive data), data/victoria/vic_products.json (live products).
Chrome (head, header, footer) comes from data/victoria/draft-backup/victoria-state-draft.html so rebuilding is repeatable.
The Melbourne hub is the saved draft with targeted edits (data/victoria/draft-backup/melbourne-hub-draft.html).
"""
import json
import os
import re
import sys
from html import escape, unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_nsw as B  # noqa: E402

ROOT = B.ROOT
SITE = B.SITE
PHONE = B.PHONE
BACKUP = os.path.join(ROOT, 'data', 'victoria', 'draft-backup')

with open(os.path.join(ROOT, 'data', 'victoria', 'vic_locations.json'), encoding='utf-8') as _f:
    LOC = json.load(_f)
with open(os.path.join(ROOT, 'data', 'victoria', 'vic_products.json'), encoding='utf-8') as _f:
    PROD = json.load(_f)

_PROOF_FILE = os.path.join(ROOT, 'data', 'victoria', 'vic_proof.json')
PROOF = {}
if os.path.isfile(_PROOF_FILE):
    with open(_PROOF_FILE, encoding='utf-8') as _f:
        PROOF = {k: v for k, v in json.load(_f).items() if not k.startswith('_')}

# Melbourne hub: names already on the saved draft (Tom, 8 Oct 2026) and larger organisations from the live /about-us page
HUB_CLUBS = ["Macleod Football Netball Club", "Diamond Creek Women's Football Club", "Reservoir Primary School",
             "Marymede Catholic College"]
HUB_LARGE = ["Victoria Police", "RMIT University", "Bunnings", "Ray White", "Downer", "Boxing Victoria"]

SUBS = LOC['suburbs']
TOWNS = LOC['towns']
SUB = {s['slug']: s for s in SUBS}
TOWN = {t['slug']: t for t in TOWNS}

STORE = {'key': 'thomastown', 'name': 'Thomastown', 'street': '11/8–20 Brock Street', 'suburb': 'Thomastown', 'pc': '3074',
         'lat': -37.68788, 'lng': 145.0257629}
STORE_ADDR = '11/8–20 Brock Street, Thomastown VIC 3074'
GMAPS_STORE = 'https://maps.google.com/?q=Alpha+Trophies+Thomastown+VIC'
EMBED = 'https://maps.google.com/maps?q=-37.68788,145.0257629&amp;hl=en&amp;z=15&amp;output=embed'

SPORT_NAME = {
    'afl': 'AFL', 'netball': 'netball', 'soccer': 'soccer', 'cricket': 'cricket', 'basketball': 'basketball', 'tennis': 'tennis',
    'lawnbowls': 'lawn bowls', 'golf': 'golf', 'hockey': 'hockey', 'athletics': 'athletics', 'swimming': 'swimming',
    'equestrian': 'equestrian', 'fishing': 'fishing', 'rowing': 'rowing', 'cycling': 'cycling', 'dance': 'dance',
    'motorsports': 'motorsport', 'sailing': 'sailing', 'schoolmedals': 'school awards', 'plaques': 'corporate plaques',
}
LABEL = {
    'afl': 'AFL', 'netball': 'Netball', 'soccer': 'Soccer', 'cricket': 'Cricket', 'basketball': 'Basketball', 'tennis': 'Tennis',
    'lawnbowls': 'Lawn bowls', 'golf': 'Golf', 'hockey': 'Hockey', 'athletics': 'Athletics', 'swimming': 'Swimming',
    'equestrian': 'Equestrian', 'fishing': 'Fishing', 'rowing': 'Rowing', 'cycling': 'Cycling', 'dance': 'Dance',
    'motorsports': 'Motorsport', 'sailing': 'Sailing', 'schoolmedals': 'School medals', 'plaques': 'Corporate plaques',
}
MEDAL_KEY = {'afl': 'aflmedals', 'netball': 'netballmedals', 'soccer': 'soccermedals', 'cricket': 'cricketmedals',
             'basketball': 'basketballmedals'}
# products already shown on the Melbourne hub are kept out of the suburb and town sets
MELB_HUB_SLUGS = {'aussie-rules-figure-female-gold-on-marble-base-trophy', 'double-lightning-strike-aussie-rules',
                  'cavalier-series-football-trophy', 'double-lightning-strike-netball-trophy', 'shield-series-cricket-trophy',
                  'basketball-achievement-medal', 'glass-budget-plaque-clear', 'timber-plaque'}

FACTS = ('Standard shipping is a $9.90 flat rate after 5 working days production and express shipping is a $25 flat rate. '
         'Fast Track is 4 working days ($40 plus 10% of the order, capped at $300) and Priority Rush is 3 working days '
         '($50 plus 15% of the order, capped at $300).')


# ---------------------------------------------------------------------------
# chrome (head / header / footer) from the saved Victoria draft, without the review banner
# ---------------------------------------------------------------------------

def _chrome(depth):
    with open(os.path.join(BACKUP, 'victoria-state-draft.html'), encoding='utf-8') as f:
        vic = f.read()
    start = vic.index('<div class="crumbs-section">')
    pre = re.sub(r'<div class="review-banner">.*?</div>\s*', '', vic[:start], flags=re.S)
    foot_start = vic.index('<footer class="site-footer">')
    foot_end = vic.index('<script type="application/ld+json">')
    return pre, vic[foot_start:foot_end]


B.chrome = _chrome


# ---------------------------------------------------------------------------
# products: every page gets its own set
# ---------------------------------------------------------------------------

def _clean(p, label):
    return {'name': unescape(p['name']).strip(), 'slug': p['slug'], 'price': p['price'], 'img': p['img'], 'label': label}


def _pool(sport):
    tro = [_clean(p, LABEL[sport]) for p in PROD[sport]['items']] if sport in PROD else []
    med = [_clean(p, LABEL[sport] + ' medals') for p in PROD[MEDAL_KEY[sport]]['items']] if sport in MEDAL_KEY else []
    out = []
    for i in range(max(len(tro), len(med))):
        if i < len(tro):
            out.append(tro[i])
        if i < len(med):
            out.append(med[i])
    return [p for p in out if p['slug'] not in MELB_HUB_SLUGS]


POOLS = {s: _pool(s) for s in SPORT_NAME}
CURSOR = {s: 0 for s in SPORT_NAME}
USED = set()


def pick(sport, page_slugs):
    pool = POOLS[sport]
    n = len(pool)
    for pass_ in (0, 1):
        for step in range(n):
            p = pool[(CURSOR[sport] + step) % n]
            if p['slug'] in page_slugs:
                continue
            if pass_ == 0 and p['slug'] in USED:
                continue
            CURSOR[sport] = (CURSOR[sport] + step + 1) % n
            USED.add(p['slug'])
            page_slugs.add(p['slug'])
            return p
    raise RuntimeError('no product for ' + sport)


def product_set(sports, per):
    page = set()
    out = []
    for s in sports:
        for _ in range(per):
            out.append(pick(s, page))
    return out


def card(p):
    return ('<article class="product-card"><div class="product-thumb-wrap"><img src="%s" alt="%s" loading="lazy" width="180" height="180"></div>\n'
            '      <div class="product-body"><span class="product-category">%s</span><h3 class="product-title">%s</h3>\n'
            '      <div class="product-meta"><span class="free-engrave"><i class="fa-solid fa-circle-check"></i> Free engraving</span></div>\n'
            '      <div class="product-footer"><div class="product-price-block"><span class="product-price-label">From</span><span class="product-price">$%s</span></div>\n'
            '      <a href="%s/product/%s" class="btn-card-action">View</a></div></div></article>'
            % (p['img'], escape(p['name']), escape(p['label']), escape(p['name']), p['price'], SITE, p['slug']))


def itemlist(name, prods):
    return {'@type': 'ItemList', 'name': name, 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'url': '%s/product/%s' % (SITE, p['slug']), 'name': p['name']}
        for i, p in enumerate(prods)]}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def words(keys):
    names = [SPORT_NAME[k] for k in keys]
    if len(names) <= 2:
        return ' and '.join(names)
    return ', '.join(names[:-1]) + ' and ' + names[-1]


def fmt_pop(n):
    return '{:,}'.format(int(round(n, -2)))


def growth_text(g):
    return 'up %.1f%%' % g if g >= 0 else 'down %.1f%%' % abs(g)


def km_text(km):
    return ('%.1f' % km).rstrip('0').rstrip('.') if km < 100 else '%d' % round(km)


def maps_dir(name):
    return 'https://www.google.com/maps/dir/%s+VIC/-37.68788,145.0257629/' % name.replace(' ', '+')



HERO_GUARANTEES = '''    <div class="hero-guarantees">
      <div class="guarantee-item"><i class="fa-solid fa-shield-halved"></i><div><strong>Trusted since 1985</strong><span>Australian-owned</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-bolt"></i><div><strong>3–5 days production</strong><span>Rush from day 3</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-award"></i><div><strong>No minimum order</strong><span>One trophy or hundreds</span></div></div>
    </div>'''

FOOT_STRIP = '''<div style="background:#fff;padding:22px 0;border-top:1px solid var(--border);font-size:14.5px"><div class="wrap">
  %s
</div></div>'''

LINK = 'style="color:var(--navy-900);font-weight:700"'


def hero(name, lead, chip, hero_prod, cta2_href, cta2_label):
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
    <img src="%s" alt="%s" width="300" height="300">
    <div class="hero-badge-overlay"><div><div style="font-size:13px;font-weight:700;color:#fff">4.9 ★ Google rating</div><div style="font-size:12px;color:#d1d5db">232 reviews across all stores</div></div></div>
  </div></div>
</div></header>''' % (escape(chip), escape(name), escape(lead), SITE, cta2_href, cta2_label, HERO_GUARANTEES,
                      hero_prod['img'], escape(hero_prod['name']))


_STOP = {'the', 'of', 'and', 'for', 'de', 'at'}
# tag overrides where the keyword rules below would guess wrong
_TAG_OVERRIDE = {
    'Rotary Club of Glen Waverley': 'comm', 'Sri Guru Singh Sabha': 'comm', 'Tamu Samaj Victoria': 'comm',
    'Cook Islands Community Services Vic Inc': 'comm', 'Friends of the Tulliallan Elms Inc.': 'comm',
    'Shepparton Malayalee Association Inc.': 'comm', 'Box Hill RSL Sub-Branch': 'comm', 'Wimmera Poultry Club': 'comm',
    'Global Youth Mental Health Awareness (GYMHA)': 'comm', 'Respect Sports Inc.': 'sport', 'Auscarts Racing': 'sport',
    'Homestyle Aged Care Langford Grange': 'biz', 'Monash Centre for Financial Studies': 'edu',
    'Anugraha Kuchipudi Dance Academy': 'sport', 'Victorian Super Tin Tops': 'biz', 'Global Events Company': 'biz',
    'Institute of Public Accountants': 'biz', 'Institute of Financial Professionals Australia': 'biz',
    'Waters Lawyers': 'biz', 'Indie School Mildura': 'edu', "School's OUT Gisborne": 'biz', 'Hamlyn Views School': 'edu',
    'Gippsland Grammar': 'edu', 'Gippsland Storm Netball Club': 'sport', 'Boxing Victoria': 'sport', 'Victoria Police': 'biz',
    'Downer': 'biz', 'Bunnings': 'biz', 'Ray White': 'biz', 'RMIT University': 'edu', 'Monash University': 'edu',
}
_EDU = ('school', 'college', 'university', 'grammar', 'primary', 'secondary', 'p-12', 'education hub')
_SPORT = ('club', 'football', 'basketball', 'netball', 'gymnastics', 'rugby', 'cricket', 'swim', 'judo', 'soccer', 'futsal',
          'tenpin', 'badminton', 'rabbitohs', 'wildcats', 'ballers', 'sports', 'sporting', 'billiards', 'padel', 'rockets',
          'bulldogs', 'rookies', 'suns', 'coasters', 'eagles', 'bears', 'wolfpack', 'lions', 'warriors', 'flyers',
          'barbarians', 'rlfc', 'gym', 'fit ', 'bft ', 'dance', 'greyhound', 'hoops', 'fc')
_TAG_LABEL = {'sport': 'Sport & recreation', 'edu': 'School & education', 'comm': 'Community group', 'biz': 'Business & organisation'}


def _tag(n):
    if n in _TAG_OVERRIDE:
        return _TAG_OVERRIDE[n]
    low = ' %s ' % n.lower()
    if any(k in low for k in _EDU):
        return 'edu'
    if any(k in low for k in _SPORT):
        return 'sport'
    return 'biz'


def _initials(n):
    words = [w for w in re.split(r'[\s/&]+', n) if w and w.lower() not in _STOP and w[0].isalnum()]
    if len(words) == 1:
        return words[0][:2].upper()
    ini = ''.join(w[0] for w in words[:2]).upper()
    return ini or n[:2].upper()


LOGO_DIR = os.path.join(ROOT, 'assets', 'img', 'customers')
LOGO_EXT = ('.png', '.svg', '.webp', '.jpg')


def customer_slug(n):
    """Stable asset name for a customer, e.g. 'Hoppers Elite Cricket Club' -> 'hoppers-elite-cricket-club'."""
    s = n.lower().replace('&', ' and ')
    s = re.sub(r"[^a-z0-9]+", '-', s.replace("'", ''))
    return s.strip('-')


def logo_file(n):
    """Return the logo file name for a customer if one has been added to assets/img/customers/, else None."""
    for ext in LOGO_EXT:
        if os.path.isfile(os.path.join(LOGO_DIR, customer_slug(n) + ext)):
            return customer_slug(n) + ext
    return None


def proof_html(name, names, phone='1300 485 645', tel='tel:1300485645', nouns='clubs, schools and businesses', depth=3):
    """Local customer cards from names supplied by Tom. Empty when there are none.
    Tags are inferred from the name (override table above); no dates, locations or awards are claimed.
    Every card has the same 64px square mark: the customer's logo when assets/img/customers/<slug>.png exists, else initials."""
    if not names:
        return ''
    items = []
    for n in names:
        t = _tag(n)
        lf = logo_file(n)
        ini = escape(_initials(n))
        if lf:
            mark = ('<div class="proof-ava has-logo"><img src="%s" alt="%s logo" width="76" height="76" loading="lazy" decoding="async" '
                    'onerror="this.parentNode.className=\'proof-ava\';this.parentNode.textContent=\'%s\'"></div>'
                    % (logo_src(lf, depth), escape(n), ini))
        else:
            mark = '<div class="proof-ava" aria-hidden="true">%s</div>' % ini
        items.append((0 if lf else 1, t, mark, n))
    items.sort(key=lambda x: x[0])  # customers with a logo first; otherwise the supplied order
    limit = 8
    cards = []
    for i, (_, t, mark, n) in enumerate(items):
        extra = ' is-extra' if (len(items) > limit and i >= limit) else ''
        cards.append('<div class="proof-card proof-%s%s"><span class="proof-tag">%s</span>'
                     '<div class="proof-body">%s<div class="proof-name">%s</div></div></div>'
                     % (t, extra, _TAG_LABEL[t], mark, escape(n)))
    more = ''
    if len(items) > limit:
        more = ('\n  <button type="button" class="proof-more" aria-expanded="false" data-all="Show all %d customers" data-less="Show fewer">'
                '<span class="t">Show all %d customers</span> <i class="fa-solid fa-chevron-down" aria-hidden="true"></i></button>'
                '\n  <noscript><style>.proof-grid .is-extra{display:flex!important}.proof-more{display:none}</style></noscript>'
                '\n  <script>document.querySelectorAll(".proof-more").forEach(function(b){b.addEventListener("click",function(){'
                'var g=b.previousElementSibling,o=g.classList.toggle("is-open");b.setAttribute("aria-expanded",o);'
                'b.querySelector(".t").textContent=o?b.dataset.less:b.dataset.all;});});</script>' % (len(items), len(items)))
    return ('<section class="proof-section"><div class="wrap"><div class="proof-panel">\n'
            '  <div class="proof-head">\n'
            '  <h2>Trusted by %s %s</h2>\n'
            '  <p>%d %s that have ordered from Alpha Trophies in %s. Every award is engraved in-house, with free engraving on every order.</p></div>\n'
            '  <div class="proof-grid">\n%s\n  </div>%s\n'
            '  <div class="proof-cta"><div><h3>Ordering for a club, school or business?</h3>'
            '<p>No minimum order, free engraving and flat-rate delivery from $9.90. Tell us your event date and we will confirm the right production option.</p></div>'
            '<a class="proof-btn" href="%s"><i class="fa-solid fa-phone"></i> Call %s</a></div>\n'
            '</div></div></section>\n' % (escape(name), nouns, len(names), 'customer' if len(names) == 1 else 'customers', escape(name),
                                           '\n'.join(cards), more, tel, escape(phone)))


def logo_src(lf, depth):
    """Small WebP for the page when one exists (assets/img/customers/sm/), else the 512px asset."""
    base = os.path.splitext(lf)[0]
    if os.path.isfile(os.path.join(LOGO_DIR, 'sm', base + '.webp')):
        return '%sassets/img/customers/sm/%s.webp' % ('../' * depth, base)
    return '%sassets/img/customers/%s' % ('../' * depth, lf)


def post(h):
    """Page-level fixes applied to every generated page: responsive product grid, landmarks, heading order, mobile contact bar."""
    h = h.replace(' class="product-grid" style="grid-template-columns:repeat(4,1fr)"', ' class="product-grid product-grid--4"')
    h = h.replace('color:#64748b">ABN', 'color:#94a3b8">ABN')
    h = re.sub(r'(<div class="store-details">)<h4>(.*?)</h4>', r'\1<p class="store-title">\2</p>', h, flags=re.S)
    h = re.sub(r'(<div class="suburb-card">)<h4>(.*?)</h4>', r'\1<h3>\2</h3>', h, flags=re.S)
    h = re.sub(r'(<div class="dir-card">)<h4>(.*?)</h4>', r'\1<h3>\2</h3>', h, flags=re.S)
    if '<main id="main">' not in h:
        h = h.replace('<div class="crumbs-section">', '<main id="main"><div class="crumbs-section">', 1)
        h = h.replace('<footer class="site-footer">', '</main><footer class="site-footer">', 1)
    if 'class="skip-link"' not in h:
        h = h.replace('<body>', '<body><a class="skip-link" href="#main">Skip to content</a>', 1)
    return h


def page(depth, title, desc, canon, body, graph, extra_js=''):
    pre, footer = B.chrome(depth)
    return post(B.head(pre, title, desc, canon, depth) + body + B.fix_footer(footer, depth) +
                B.ld({'@context': 'https://schema.org', '@graph': graph}) +
                '\n<script src="%sassets/js/nav.js" defer></script>%s</body></html>\n' % ('../' * depth, extra_js))


def store_schema():
    return {
        '@type': ['Store', 'LocalBusiness'], '@id': SITE + '/stores/thomastown#store', 'name': 'Alpha Trophies Thomastown',
        'telephone': '+61 ' + PHONE, 'email': 'sales@alphatrophies.com.au', 'image': SITE + '/assets/frontend/img/logo.png',
        'priceRange': '$$', 'currenciesAccepted': 'AUD',
        'address': {'@type': 'PostalAddress', 'streetAddress': STORE['street'], 'addressLocality': 'Thomastown',
                    'addressRegion': 'VIC', 'postalCode': '3074', 'addressCountry': 'AU'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': STORE['lat'], 'longitude': STORE['lng']},
        'hasMap': GMAPS_STORE,
        'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification',
                                       'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                                       'opens': '09:00', 'closes': '17:00'}],
        'sameAs': ['https://www.facebook.com/alphatrophiesaustralia', 'https://www.instagram.com/alphatrophies/',
                   'https://www.google.com/maps?cid=1167186670153645038'],
        'parentOrganization': {'@type': 'Organization', 'name': 'Alpha Trophies', 'url': SITE},
        'areaServed': {'@type': 'State', 'name': 'Victoria'},
    }


def store_bar(distance_note=None):
    note = ' &nbsp;·&nbsp; %s' % escape(distance_note) if distance_note else ''
    return ('<div class="store-bar" id="store"><div class="wrap store-bar-inner">\n'
            '  <div class="store-location"><div class="store-icon-wrap"><i class="fa-solid fa-shop"></i></div>\n'
            '  <div class="store-details"><h4>Thomastown showroom <span class="store-badge"><i class="fa-solid fa-circle-check"></i> Free pickup</span></h4>\n'
            '  <p>%s &nbsp;·&nbsp; Mon–Fri 9am–5pm%s</p></div></div>\n'
            '  <div class="store-actions"><a class="btn-store-action" href="%s" target="_blank" rel="noopener"><i class="fa-solid fa-location-arrow"></i> Google Maps</a>\n'
            '  <a class="btn-store-action" href="tel:1300485645"><i class="fa-solid fa-phone"></i> %s</a></div>\n'
            '</div></div>' % (escape(STORE_ADDR), note, GMAPS_STORE, PHONE))


# ---------------------------------------------------------------------------
# suburb page  /trophies/victoria/melbourne/<suburb>/   (depth 4)
# ---------------------------------------------------------------------------

def suburb_page(s):
    depth = 4
    name = s['name']
    canon = '%s/trophies/victoria/melbourne/%s/' % (SITE, s['slug'])
    d = s['drive']
    km = km_text(d['km'])
    prods = product_set(s['sports'], 1)
    p0 = prods[0]
    title = 'Trophies in %s, Melbourne | Alpha Trophies' % name
    desc = ('Custom trophies, medals and plaques for %s. Free engraving, %s km from our Thomastown showroom, $9.90 flat-rate delivery.' % (name, km))
    drive_line = ('%s is about %s km by road from our Thomastown showroom, via %s. Google Maps shows about %s in afternoon traffic.'
                  % (name, km, d['route'], d['time']))
    near = [SUB[n] for n in s['near']]
    chips = ''.join('<a class="chip" href="../%s/" style="text-decoration:none">%s</a>' % (o['slug'], escape(o['name'])) for o in near)
    fact = (' ' + s['fact']) if s['fact'] else ''
    faqs = [
        ('Can I pick up trophies from Thomastown if I live in %s?' % name,
         '%s Orders are ready for pickup at %s, Monday to Friday 9am to 5pm, after 5 working days production. Priority Rush pickup is available from day 3 ($15 plus 20%% of the order, capped at $300). There is plenty of on-site parking.' % (drive_line, STORE_ADDR)),
        ('Do you deliver trophies to %s?' % name,
         'Yes. Standard shipping to %s is a $9.90 flat rate and express is $25, after 5 working days production. Pickup from Thomastown has no shipping charge.' % name),
        ('Can I order %s trophies for a %s club or school?' % (SPORT_NAME[s['sports'][0]], name),
         'Yes. %s is one of the popular categories in the area, alongside %s. A good starting point is the %s, from $%s. Every item includes free engraving and there is no minimum order.' % (
             SPORT_NAME[s['sports'][0]].capitalize(), words(s['sports'][1:]), p0['name'], p0['price'])),
        ('How fast can I get trophies for a %s presentation day?' % name,
         'Standard production is 5 working days. Fast Track is 4 working days ($40 plus 10% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15%, capped at $300), plus delivery or pickup. Tell us the event date when you order.'),
    ]
    body = '''
%(crumbs)s

%(hero)s

%(store)s

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Popular in %(name)s</span><h2 class="sec-title">Trophies for %(name)s clubs and schools</h2>
  <p class="sec-sub">%(sportline)s Every item includes free engraving.</p></div>
  <div class="product-grid" style="grid-template-columns:repeat(4,1fr)">
%(cards)s
  </div>
</div></section>

<section id="directions" class="sec sec-alt"><div class="wrap copy-two">
  <div><h3>Getting from %(name)s to Thomastown</h3>
  <p>%(drive)s</p>
  <p><a class="btn-store-action" href="%(dirlink)s" target="_blank" rel="noopener"><i class="fa-solid fa-route"></i> Directions from %(name)s</a></p></div>
  <div><h3>Pickup or delivery to %(name)s</h3>
  <p>Collect from Thomastown after 5 working days, or from day 3 with Priority Rush pickup. Prefer delivery? Standard shipping is a $9.90 flat rate and express is $25, after production.</p>
  <p>Typical orders from %(name)s include %(occ)s.</p></div>
</div></section>

<section class="sec"><div class="wrap copy-two">
  <div><h3>About %(name)s</h3>
  <p>%(blurb)s %(name)s is in the City of %(lga)s, in %(region)s, with about %(pop)s residents (number %(rank)d on our Melbourne top 20 list).%(fact)s</p></div>
  <div><h3>Nearby Melbourne suburbs</h3>
  <div class="chip-list">%(chips)s</div>
  <p style="margin-top:14px;font-size:15px;color:var(--text-muted)">See the full <a href="../" %(link)s>Melbourne trophies page</a> or call <a href="tel:1300485645" %(link)s>%(phone)s</a>.</p></div>
</div></section>

%(proof)s<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(name)s</span><h2 class="sec-title">%(name)s trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

%(foot)s

''' % {'proof': proof_html(name, PROOF.get(s['slug']), depth=4),
       'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('Victoria', '../../'), ('Melbourne', '../'), (escape(name), None)]),
       'hero': hero(name, '%s Engraved in-house, ready for pickup in Thomastown or delivered to %s clubs, schools and businesses.' % (s['blurb'], name),
                    s['region'], p0, '#directions', 'Getting to Thomastown'),
       'store': store_bar('%s km from %s' % (km, name)), 'name': escape(name), 'sportline': escape(s['sportline']),
       'cards': '\n'.join(card(p) for p in prods), 'drive': escape(drive_line), 'dirlink': maps_dir(name),
       'occ': escape(s['occasion']), 'blurb': escape(s['blurb']), 'lga': escape(s['lga']), 'region': escape(s['region']),
       'pop': fmt_pop(s['pop']), 'rank': s['rank'], 'fact': escape(fact), 'chips': chips, 'link': LINK, 'phone': PHONE,
       'faq': B.faq_html(faqs),
       'foot': FOOT_STRIP % ('<a href="../" %s><i class="fa-solid fa-arrow-left"></i> Trophies in Melbourne</a>'
                             '<span style="margin:0 10px;color:#cbd5e1">|</span><a href="../../" %s>All Victoria trophies</a>' % (LINK, LINK))}
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                             ('Victoria', SITE + '/trophies/victoria/'), ('Melbourne', SITE + '/trophies/victoria/melbourne/'), (name, canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies in %s' % name, 'url': canon,
         'about': {'@type': 'Place', 'name': '%s, Melbourne' % name}},
        itemlist('Featured products in %s' % name, prods),
        B.faq_schema(faqs),
    ]
    return page(depth, title, desc, canon, body, graph)


# ---------------------------------------------------------------------------
# town page  /trophies/victoria/<town>/   (depth 3)
# ---------------------------------------------------------------------------

def town_page(t):
    depth = 3
    name = t['name']
    canon = '%s/trophies/victoria/%s/' % (SITE, t['slug'])
    d = t['drive']
    km = km_text(d['km'])
    prods = product_set(t['sports'], 2)
    p0 = prods[0]
    title = 'Trophies in %s | Alpha Trophies' % name
    desc = ('Custom trophies, medals and plaques delivered to %s, about %s km from Melbourne. Free engraving, $9.90 flat-rate shipping, no minimum order.' % (name, km))
    drive_line = ('%s is about %s km by road from our Thomastown showroom, via %s. Google Maps shows about %s in afternoon traffic.'
                  % (name, km, d['route'], d['time']))
    fact = (' ' + t['fact']) if t['fact'] else ''
    faqs = [
        ('Do you deliver trophies to %s?' % name,
         'Yes. %s is about %s km from our Melbourne showroom, and we deliver there with standard shipping at a $9.90 flat rate or express at $25, after 5 working days production.' % (name, km)),
        ('Can you make %s trophies for %s clubs?' % (SPORT_NAME[t['sports'][0]], name),
         'Yes. %s and %s are among the main categories for %s, and every item includes free engraving. Popular picks include the %s, from $%s. There is no minimum order.' % (
             SPORT_NAME[t['sports'][0]].capitalize(), SPORT_NAME[t['sports'][1]], name, p0['name'], p0['price'])),
        ('How fast can I get trophies to %s for a presentation day?' % name,
         'Standard production is 5 working days, plus delivery to %s. Fast Track is 4 working days ($40 plus 10%% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15%% of the order, capped at $300), also plus delivery. Tell us the event date when you order.' % name),
        ('Can I collect my order instead of having it delivered to %s?' % name,
         'Yes, if you are coming to Melbourne. Pickup is from %s, Monday to Friday 9am to 5pm, with no shipping charge. %s' % (STORE_ADDR, drive_line)),
        ('Is engraving free?', 'Yes, free engraving on every order, and there is no minimum order.'),
    ]
    near = [TOWN[n] for n in t['near']]
    chips = ''.join('<a class="chip" href="../%s/" style="text-decoration:none">%s</a>' % (o['slug'], escape(o['name'])) for o in near)
    body = '''
%(crumbs)s

%(hero)s

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Popular in %(name)s</span><h2 class="sec-title">Trophies and medals for %(name)s clubs and schools</h2>
  <p class="sec-sub">%(sportline)s Every item includes free engraving.</p></div>
  <div class="product-grid" style="grid-template-columns:repeat(4,1fr)">
%(cards)s
  </div>
</div></section>

<section class="sec sec-alt"><div class="wrap copy-two">
  <div><h3>Delivered to %(name)s</h3>
  <p>%(drive)s Every order is engraved in-house, then sent by standard shipping at a $9.90 flat rate or express at $25, after 5 working days production.</p>
  <p>The %(name)s urban area has about %(pop)s residents (ABS estimate, June 2025), %(growth)s over the past ten years, and ranks number %(rank)d of the Victorian urban areas on our list.</p></div>
  <div><h3>Presentation days in %(region)s</h3>
  <p>%(blurb)s%(fact)s</p>
  <p>We regularly see orders from the area for %(occ)s. Fast Track (4 working days) and Priority Rush (3 working days) are available at checkout when a date is fixed.</p></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Also delivering nearby</span><h2 class="sec-title">Other Victorian towns near %(name)s</h2></div>
  <div class="chip-list" style="justify-content:center">%(chips)s</div>
  <p style="text-align:center;margin-top:24px;font-size:15px;color:var(--text-muted)">Order online and we deliver, or collect from our Thomastown showroom. Questions? Call <a href="tel:1300485645" %(link)s>%(phone)s</a> or email <a href="mailto:sales@alphatrophies.com.au" %(link)s>sales@alphatrophies.com.au</a>. See the <a href="../melbourne/" %(link)s>Melbourne page</a> for directions to the showroom.</p>
</div></section>

%(proof)s<section id="faq" class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(name)s</span><h2 class="sec-title">%(name)s trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

%(foot)s

''' % {'proof': proof_html(name, PROOF.get(t['slug'])),
       'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('Victoria', '../'), (escape(name), None)]),
       'hero': hero(name, '%s Engraved in-house and delivered to %s clubs, schools and businesses.' % (t['blurb'], name),
                    t['region'], p0, '#faq', 'Delivery and FAQs'),
       'name': escape(name), 'sportline': escape(t['sportline']), 'cards': '\n'.join(card(p) for p in prods),
       'drive': escape(drive_line), 'pop': fmt_pop(t['pop']), 'growth': growth_text(t['growth']), 'rank': t['rank'],
       'region': escape(t['region']), 'blurb': escape(t['blurb']), 'fact': escape(fact), 'occ': escape(t['occasion']),
       'chips': chips, 'link': LINK, 'phone': PHONE, 'faq': B.faq_html(faqs),
       'foot': FOOT_STRIP % ('<a href="../" %s><i class="fa-solid fa-arrow-left"></i> All Victoria trophies</a>'
                             '<span style="margin:0 10px;color:#cbd5e1">|</span><a href="../melbourne/" %s>Melbourne showroom</a>' % (LINK, LINK))}
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                             ('Victoria', SITE + '/trophies/victoria/'), (name, canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies in %s' % name, 'url': canon,
         'about': {'@type': 'City', 'name': name}},
        itemlist('Featured products in %s' % name, prods),
        B.faq_schema(faqs),
    ]
    return page(depth, title, desc, canon, body, graph)


# ---------------------------------------------------------------------------
# Victoria state page  /trophies/victoria/   (depth 2)
# ---------------------------------------------------------------------------

STATE_TILES = [  # key, blurb, badge
    ('afl', 'Premiership, best-and-fairest and junior footy awards', 'Winter favourite'),
    ('netball', 'Team, player and association awards', 'Association sport'),
    ('soccer', 'Junior clubs through to senior leagues', 'Club season'),
    ('cricket', 'Batting, bowling and premiership awards', 'Summer favourite'),
    ('basketball', 'MVP, team and association awards', 'Indoor season'),
    ('schoolmedals', 'Presentation-day medals for every subject and sport', 'School awards'),
]
TOWN_GROUP_NAME = {'metro': 'Greater Melbourne', 'west': 'Geelong & Western Victoria', 'north': 'Central & Northern Victoria',
                   'gippsland': 'Gippsland'}


def min_price(key):
    return min(float(p['price']) for p in PROD[key]['items'])


def state_page():
    depth = 2
    canon = SITE + '/trophies/victoria/'
    title = 'Custom Trophies Victoria | Free Engraving | Alpha Trophies'
    desc = ('Custom trophies, medals and awards for Victorian clubs, schools and businesses. Free engraving, flat-rate delivery statewide, Melbourne showroom.')
    faqs = [
        ('Do you deliver trophies across Victoria?',
         'Yes. We deliver to every part of Victoria, from Melbourne to regional towns such as Geelong, Ballarat and Bendigo. Standard shipping is a $9.90 flat rate and express is a $25 flat rate, after 5 working days production.'),
        ('Where is your Victorian store?',
         'Our Victorian showroom is at %s, off Settlement Road. It is open Monday to Friday 9am to 5pm, with plenty of on-site parking.' % STORE_ADDR),
        ('Can I pick up my order in Melbourne?',
         'Yes. Pickup from Thomastown has no shipping charge. Standard pickup is after 5 working days production and Priority Rush pickup is available from day 3 ($15 plus 20% of the order, capped at $300).'),
        ('How fast can I get trophies for a presentation day?',
         'Fast Track is 4 working days ($40 plus 10% of the order, capped at $300). Priority Rush is 3 working days ($50 plus 15% of the order, capped at $300). Tell us your event date when you order.'),
        ('Do you do trophies for AFL, netball and cricket clubs?',
         'Yes. These are among our most popular Victorian categories, and every item includes free engraving. Browse the categories above or the full trophy range.'),
        ('Is engraving free?', 'Yes, free engraving on every order. There is no minimum order.'),
    ]
    # featured category cards (representative product image per category)
    feat = []
    for (key, blurb, badge) in STATE_TILES:
        items = PROD[key]['items']
        rep = items[min(2, len(items) - 1)]
        label = {'schoolmedals': 'School medals'}.get(key, LABEL[key] + ' trophies')
        feat.append('<a class="feat-card" href="%s/%s"><div class="feat-img"><img src="%s" alt="%s" loading="lazy" width="320" height="240"><span class="feat-badge">%s</span></div>\n'
                    '      <div class="feat-body"><h3>%s</h3><p>%s</p>\n'
                    '      <div class="feat-chips"><span><i class="fa-regular fa-clock"></i> 3–5 days production</span><span><i class="fa-regular fa-circle-check"></i> Free engraving included</span></div>\n'
                    '      <div class="feat-price"><div><span class="feat-label">Starting price</span><strong>From $%.2f</strong></div><span class="feat-btn">Explore range <i class="fa-solid fa-arrow-right"></i></span></div></div></a>'
                    % (SITE, PROD[key]['path'], rep['img'], escape(unescape(rep['name'])), badge, label, blurb, min_price(key)))
    featured = (
        '<section class="sec sec-alt"><div class="wrap">\n'
        '  <div class="feat-head"><div><span class="sec-eyebrow" style="text-align:left">Statewide presentation favourites</span><h2 class="sec-title" style="text-align:left">Popular in Victoria: trophies for Victorian clubs and schools</h2>\n'
        '  <p class="sec-sub" style="text-align:left;margin:0">Browse the categories Victorian clubs order most. Every award includes free engraving.</p></div>\n'
        '  <span class="feat-pill"><i class="fa-regular fa-circle-check"></i> Includes free engraving</span></div>\n'
        '  <div class="feat-grid">\n      %s\n  </div>\n</div></section>' % '\n'.join(feat))

    # directory
    cards = ['    <a class="dir-city" data-group="metro" data-search="melbourne metropolitan thomastown showroom suburbs" href="melbourne/"><span class="dir-top"><span class="dir-tag dir-tag-gold">Greater Melbourne</span><i class="fa-solid fa-store"></i></span><h3>Melbourne</h3><p>Our Thomastown showroom with free pickup, plus a suburb guide covering 19 Melbourne suburbs from Point Cook to Richmond.</p><span class="dir-go">Trophies in Melbourne <i class="fa-solid fa-arrow-right"></i></span></a>']
    for t in TOWNS:
        cards.append('    <a class="dir-city" data-group="%s" data-search="%s" href="%s/"><span class="dir-top"><span class="dir-tag">%s</span><i class="fa-solid fa-truck"></i></span><h3>%s</h3><p>%s</p><span class="dir-go">Trophies in %s <i class="fa-solid fa-arrow-right"></i></span></a>'
                     % (t['group'], escape((t['name'] + ' ' + t['region']).lower()), t['slug'], escape(t['region']), escape(t['name']), escape(t['blurb']), escape(t['name'])))
    total = len(TOWNS) + 1
    cities = (
        '<section id="cities" class="sec"><div class="wrap">\n'
        '  <div class="sec-header"><span class="sec-eyebrow">Statewide directory <span class="dir-count">%d locations</span></span><h2 class="sec-title">Find trophies near you across Victoria</h2>\n'
        '  <p class="sec-sub">From Melbourne to Geelong, Ballarat, Bendigo and Gippsland, we engrave and deliver trophies, medals and awards to every corner of Victoria.</p></div>\n'
        '  <div class="dir-tabs" role="group" aria-label="Filter locations">\n'
        '    <button type="button" class="dir-tab is-active" data-filter="all">All %d locations</button>\n'
        '    <button type="button" class="dir-tab" data-filter="metro">Greater Melbourne</button>\n'
        '    <button type="button" class="dir-tab" data-filter="west">Geelong &amp; Western Victoria</button>\n'
        '    <button type="button" class="dir-tab" data-filter="north">Central &amp; Northern Victoria</button>\n'
        '    <button type="button" class="dir-tab" data-filter="gippsland">Gippsland</button>\n'
        '  </div>\n'
        '  <div class="dir-search"><i class="fa-solid fa-magnifying-glass"></i><input type="search" id="dir-q" placeholder="Type your city or region (e.g. Geelong, Bendigo, Melbourne)" aria-label="Search Victorian locations"></div>\n'
        '  <div class="dir-grid" id="dir-grid">\n%s\n  </div>\n'
        '  <p class="dir-empty" id="dir-empty" hidden>No match yet. Call %s and we will help.</p>\n'
        '</div></section>' % (total, total, '\n'.join(cards), PHONE))

    suburbs = (
        '<section class="sec sec-alt"><div class="wrap">\n'
        '  <div class="sec-header"><span class="sec-eyebrow">Melbourne suburbs</span><h2 class="sec-title">Trophies in your Melbourne suburb</h2>\n'
        '  <p class="sec-sub">Each suburb page shows the drive to our Thomastown showroom and a trophy range for local clubs. Albury–Wodonga, on the border, is on our <a href="../new-south-wales/albury-wodonga/" %s>NSW page</a>.</p></div>\n'
        '  <div class="chip-list" style="justify-content:center">%s</div>\n'
        '</div></section>' % (LINK, ''.join('<a class="chip" href="melbourne/%s/" style="text-decoration:none">%s</a>' % (s['slug'], escape(s['name'])) for s in SUBS)))

    delivery = """<section class="sec"><div class="wrap dlv-grid">
  <div class="dlv-card">
    <div class="dlv-top"><span class="dlv-eyebrow"><i class="fa-solid fa-truck"></i> Statewide delivery</span><span class="dlv-badge">Flat-rate shipping</span></div>
    <h3>Delivered across Victoria</h3>
    <p>Every Victorian order is engraved in-house and sent to your door, whether you are in Melbourne, Geelong, Gippsland or the Murray. Standard shipping is a $9.90 flat rate and express is $25, after 5 working days production.</p>
    <div class="dlv-opts">
      <div class="dlv-opt"><div class="dlv-opt-top"><span><i class="fa-solid fa-box"></i> Standard delivery</span><em>Regular</em></div><strong>$9.90 flat rate</strong><small>5 working days production, then shipping</small></div>
      <div class="dlv-opt"><div class="dlv-opt-top"><span><i class="fa-solid fa-bolt"></i> Express delivery</span><em class="hot">Faster</em></div><strong>$25 flat rate</strong><small>Express shipping after 5 working days production</small></div>
    </div>
    <div class="dlv-rush"><h4><i class="fa-regular fa-clock"></i> Rush options for deadlines</h4>
      <ul><li><span>Fast Track (4 working days)</span><strong>$40 + 10%, capped $300</strong></li><li><span>Priority Rush (3 working days)</span><strong>$50 + 15%, capped $300</strong></li></ul></div>
    <div class="dlv-foot"><span>Free engraving on every order</span><span>Questions? Call 1300 485 645</span></div>
  </div>
  <div class="dlv-card dlv-dark">
    <span class="dlv-eyebrow"><i class="fa-solid fa-trophy"></i> Built for Victorian clubs</span>
    <h3>Made for Victorian presentation days</h3>
    <p>Built for AFL and netball clubs, cricket associations, soccer clubs, basketball leagues and school presentation days. More than 70 trophy categories are available.</p>
    <ul class="dlv-list">
      <li><i class="fa-solid fa-football"></i> Football-netball premierships and best-and-fairest awards</li>
      <li><i class="fa-solid fa-baseball-bat-ball"></i> Summer cricket club and association awards</li>
      <li><i class="fa-solid fa-futbol"></i> Soccer and basketball season awards</li>
      <li><i class="fa-solid fa-school"></i> School presentation days and sports carnivals</li>
    </ul>
    <div class="dlv-note"><strong>Free pickup in Thomastown</strong><span>Every piece includes free laser engraving</span></div>
  </div>
</div></section>"""

    hero_prod = _clean(PROD['afl']['items'][2], 'AFL')
    body = '''
%(crumbs)s

<header class="hero"><div class="wrap hero-grid">
  <div class="hero-content">
    <div class="hero-badge-row"><span class="hero-tag"><i class="fa-solid fa-check"></i> Free engraving</span><span class="hero-local-chip"><i class="fa-solid fa-location-dot"></i> Melbourne showroom: Thomastown</span></div>
    <h1>Custom Trophies &amp; Awards in <span class="gold">Victoria</span></h1>
    <p class="lead">Trophies, medals and awards for Victorian clubs, schools and businesses. Engraved in-house, delivered anywhere in the state, with free pickup from our Thomastown showroom in Melbourne.</p>
    <div class="hero-ctas">
      <a class="btn-primary" href="#cities"><span>Choose your city</span><i class="fa-solid fa-arrow-right"></i></a>
      <a class="btn-secondary" href="melbourne/"><i class="fa-solid fa-map-pin"></i><span>Melbourne store &amp; directions</span></a>
    </div>
%(guar)s
  </div>
  <div class="hero-visual"><div class="hero-visual-card">
    <img src="%(himg)s" alt="%(halt)s" width="300" height="300">
    <div class="hero-badge-overlay"><div><div style="font-size:13px;font-weight:700;color:#fff">4.9 ★ Google rating</div><div style="font-size:12px;color:#d1d5db">232 reviews across all stores</div></div></div>
  </div></div>
</div></header>

%(cities)s

%(featured)s

%(delivery)s

%(suburbs)s

<section id="store" class="sec"><div class="wrap find-us-layout">
  <div>
    <span class="sec-eyebrow" style="text-align:left">Our Victorian location</span>
    <h2 class="sec-title" style="text-align:left">Alpha Trophies in Melbourne</h2>
    <p style="font-size:15px;color:var(--text-muted);margin-bottom:14px"><strong>Thomastown showroom:</strong> %(addr)s, off Settlement Road. Free pickup, with plenty of on-site parking.</p>
    <p style="font-size:15px;color:var(--text-muted);margin-bottom:14px"><strong>Hours:</strong> Mon–Fri 9am–5pm<br><strong>Phone:</strong> %(phone)s<br><strong>Email:</strong> sales@alphatrophies.com.au</p>
    <p><a class="btn-primary" href="melbourne/#how-to-find-us" style="font-size:15px;padding:12px 22px"><i class="fa-solid fa-route"></i> See how to find us</a></p>
  </div>
  <div class="interactive-map-panel"><div class="map-embed-wrapper"><iframe title="Alpha Trophies Thomastown map" src="%(embed)s" loading="lazy"></iframe></div></div>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><h2 class="sec-title">Victoria trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

<div style="background:#fff;padding:22px 0;border-top:1px solid var(--border);font-size:14.5px"><div class="wrap">
  Browse: <a href="melbourne/" %(link)s>Melbourne</a> &nbsp;|&nbsp; <a href="../new-south-wales/" %(link)s>New South Wales</a> &nbsp;|&nbsp; <a href="../south-australia/" %(link)s>South Australia</a>
</div></div>

''' % {'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('Victoria', None)]), 'guar': HERO_GUARANTEES,
       'himg': hero_prod['img'], 'halt': escape(hero_prod['name']), 'cities': cities, 'featured': featured, 'delivery': delivery,
       'suburbs': suburbs, 'addr': escape(STORE_ADDR), 'phone': PHONE, 'embed': EMBED, 'faq': B.faq_html(faqs), 'link': LINK}
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'), ('Victoria', canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies Victoria', 'url': canon,
         'about': {'@type': 'AdministrativeArea', 'name': 'Victoria'}},
        {'@type': 'ItemList', 'name': 'Victorian cities and towns', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'url': canon + sl + '/'}
            for i, (n, sl) in enumerate([('Melbourne', 'melbourne')] + [(t['name'], t['slug']) for t in TOWNS])]},
        store_schema(), B.faq_schema(faqs),
    ]
    return page(depth, title, desc, canon, body, graph,
                '<script src="../../assets/js/directory.js" defer></script>')


# ---------------------------------------------------------------------------
# Melbourne hub: the saved draft plus targeted edits
# ---------------------------------------------------------------------------

def melbourne_page():
    with open(os.path.join(BACKUP, 'melbourne-hub-draft.html'), encoding='utf-8') as f:
        h = f.read()

    def sub(old, new, count=1):
        nonlocal h
        if old not in h:
            raise RuntimeError('Melbourne hub text not found: ' + old[:60])
        h = h.replace(old, new, count)

    h = re.sub(r'<div class="review-banner">.*?</div>\s*', '', h, count=1, flags=re.S)
    title = 'Custom Trophies Melbourne | Thomastown Pickup | Alpha Trophies'
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, h, count=1, flags=re.S)
    h = h.replace('Custom Trophies Melbourne | Free Engraving, Thomastown Pickup | Alpha Trophies', title)
    # verified drive data (Google Maps, 11 Nov 2026)
    sub('From Reservoir and nearby</h4><ol class="steps-list"><li>Head north on Cheddar Road or Dalton Road. About 4.5 km, 9 minutes.</li>',
        'From Reservoir and nearby</h4><ol class="steps-list"><li>Head north on Cheddar Road. About 3.9 km, 9 minutes.</li>')
    sub('About 22 km, 21 minutes from Craigieburn.', 'About 22 km from Craigieburn, roughly 20 to 30 minutes depending on traffic.')
    sub('About 32 km, 35 minutes from the CBD.', 'About 34 km from Southbank, roughly 35 to 40 minutes depending on traffic.')
    # suburb section: linked cards for all 19 suburbs
    start = h.index('<section class="sec sec-alt"><div class="wrap">\n  <div class="sec-header"><span class="sec-eyebrow">Melbourne suburbs</span>')
    end = h.index('</section>', start) + len('</section>')
    cards = []
    for s in SUBS:
        d = s['drive']
        cards.append('    <div class="suburb-card"><h4><a href="%s/" %s>%s</a></h4><p>%s km from our store via %s. %s</p></div>'
                     % (s['slug'], 'style="color:var(--navy-900)"', escape(s['name']), km_text(d['km']), escape(d['route']), escape(s['sportline'])))
    new_sec = ('<section id="suburbs" class="sec sec-alt"><div class="wrap">\n'
               '  <div class="sec-header"><span class="sec-eyebrow">Melbourne suburbs</span><h2 class="sec-title">Close by, or delivered to you</h2>\n'
               '  <p class="sec-sub">Pick your suburb for the drive to our Thomastown showroom and a trophy range for local clubs. Distances are by road, from Google Maps.</p></div>\n'
               '  <div class="suburb-grid-pickup">\n%s\n  </div>\n</div></section>' % '\n'.join(cards))
    h = h[:start] + new_sec + h[end:]
    sub('<span style="color:var(--text-subtle)">More Victorian cities coming soon</span>',
        '<a href="../#cities" %s>More Victorian cities</a>' % LINK)
    # customers section: the saved draft strip is replaced by the card grid (large names first, then clubs, then Tom's list)
    names = HUB_LARGE + HUB_CLUBS + PROOF.get('melbourne', [])
    new_proof = proof_html('Melbourne', names, nouns='clubs, schools and organisations')
    h, n_sub = re.subn(r'<section class="clients-strip">.*?</section>\n?', lambda m: new_proof, h, count=1, flags=re.S)
    if n_sub != 1:
        raise RuntimeError('Melbourne hub customers section not found')
    # schema: add the suburb list
    graph_item = json.dumps({'@type': 'ItemList', 'name': 'Melbourne suburbs', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': s['name'], 'url': '%s/trophies/victoria/melbourne/%s/' % (SITE, s['slug'])}
        for i, s in enumerate(SUBS)]}, indent=1, ensure_ascii=False)
    sub('  {\n   "@type": "ItemList",\n   "name": "Featured products in Melbourne",',
        '  ' + graph_item.replace('\n', '\n  ') + ',\n  {\n   "@type": "ItemList",\n   "name": "Featured products in Melbourne",')
    return post(h)


# ---------------------------------------------------------------------------

def main():
    B.write('trophies/victoria/index.html', state_page())
    B.write('trophies/victoria/melbourne/index.html', melbourne_page())
    for s in SUBS:
        B.write('trophies/victoria/melbourne/%s/index.html' % s['slug'], suburb_page(s))
    for t in TOWNS:
        B.write('trophies/victoria/%s/index.html' % t['slug'], town_page(t))
    urls = ['/trophies/victoria/', '/trophies/victoria/melbourne/']
    urls += ['/trophies/victoria/melbourne/%s/' % s['slug'] for s in SUBS]
    urls += ['/trophies/victoria/%s/' % t['slug'] for t in TOWNS]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += ['  <url><loc>%s%s</loc></url>' % (SITE, u) for u in urls]
    xml.append('</urlset>')
    os.makedirs(os.path.join(ROOT, 'sitemaps'), exist_ok=True)
    with open(os.path.join(ROOT, 'sitemaps', 'sitemap-victoria.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(xml) + '\n')
    print('%d URLs in sitemaps/sitemap-victoria.xml; %d distinct products used' % (len(urls), len(USED)))


if __name__ == '__main__':
    main()
