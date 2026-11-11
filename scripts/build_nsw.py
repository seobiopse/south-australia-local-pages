"""Generate the NSW state page and the Sydney hub from the Victoria page chrome.

Run: python build_nsw.py   then   python build_nav.py   (build_nav is idempotent).
Head, top bar, header and footer come from trophies/victoria/index.html so the
shared chrome stays identical. Body copy, schema and meta are NSW/Sydney specific.
"""
import json
import os
import re
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://alphatrophies.com.au'
IMG = 'assets/img/products/nsw/'
PHONE = '1300 485 645'

STORES = [
    {'key': 'riverwood', 'name': 'Riverwood', 'street': '8/5 Leedham Place', 'suburb': 'Riverwood', 'pc': '2210'},
    {'key': 'castle-hill', 'name': 'Castle Hill', 'street': '51/9 Hoyle Ave', 'suburb': 'Castle Hill', 'pc': '2154'},
]


with open(os.path.join(ROOT, 'data', 'nsw', 'nsw_locations.json'), encoding='utf-8') as _f:
    LOC = json.load(_f)
TOWNS = LOC['towns']
SUBS = LOC['suburbs']
SUB_SLUG = {x['name']: x['slug'] for x in SUBS}
HUNTER_CC = {'newcastle-maitland', 'central-coast', 'singleton', 'muswellbrook', 'morisset-cooranbong', 'medowie', 'nelson-bay'}


def addr(s):
    return '%s, %s NSW %s' % (s['street'], s['suburb'], s['pc'])


def gmaps(s):
    if s.get('maps'):
        return s['maps']
    return 'https://maps.google.com/?q=' + (addr(s) + ' Alpha Trophies').replace(' ', '+').replace(',', '')


def embed(s):
    if s.get('lat'):
        return 'https://maps.google.com/maps?q=%s,%s&amp;hl=en&amp;z=15&amp;output=embed' % (s['lat'], s['lng'])
    return 'https://maps.google.com/maps?q=' + addr(s).replace(' ', '+').replace(',', '') + '&amp;hl=en&amp;z=15&amp;output=embed'


# ---- products -------------------------------------------------------------
# name, category label, price, product url, image file
SYDNEY_PRODUCTS = [
    ('Elliptical Rugby Trophy', 'Rugby', '9.20', 'elliptical-rugby-trophy', 'elliptical-rugby-front-8620.jpg'),
    ('Rugby Mini Star Trophy', 'Rugby', '9.10', 'rugby-mini-star-trophy', 'rugby-mini-star-front-2003.jpg'),
    ('Lifesaving Rescue Board Trophy', 'Surf life saving', '9.45', 'lifesaving-rescue-board-trophy', 'dsc08883-3350.jpg'),
    ('Shield Series Lifesaving Trophy', 'Surf life saving', '9.80', 'shield-series-lifesaving-trophy', 'shield-series-lifesaving-front-8513.jpg'),
    ('Titan Series Swimming Trophy', 'Swimming', '9.95', 'titan-series-swimming-trophy', 'titan-swimming-front-9082.jpg'),
    ('Swim Mini Star Trophy', 'Swimming', '9.10', 'swim-mini-star-trophy', '2swimming-mini-star-front-6077-1147.jpg'),
    ('Double Lightning Strike - Swimming Trophy', 'Swimming', '9.45', 'double-lightning-strike-swimming-trophy', '43-3968.webp'),
    ('Falcon Series-Rugby Medal', 'Rugby medals', '6.35', 'falcon-series-rugby-medal', '1072-6g-3813.jpg'),
]

# title, blurb, from price, url, image, alt
STATE_TILES = [
    ('Rugby league &amp; union trophies', 'Club, junior and premiership awards', '7.45', 'trophies/r/rugby-league', '64-4748-2107.webp', 'Male Rugby on Marble Base Trophy'),
    ('Rugby medals', 'Presentation-day medals for juniors and seniors', '5.00', 'medals/rr/rugby-league-medals', 'mw913g-4973.jpg', 'Rugby Wayfare Medal'),
    ('Surf life saving trophies', 'Patrol, nipper and club championship awards', '8.60', 'trophies/s/surf-life-saving', '2-lifesaving-budget-theme-front-9234-2824.jpg', 'Lifesaving Budget Theme Trophy'),
    ('Swimming trophies', 'Carnival champions and age-group awards', '8.10', 'trophies/s/swimming', '9-2710.webp', 'Mini Black Cobra Swimming Trophy'),
    ('Basketball trophies', 'Team, MVP and association awards', '7.65', 'trophies/b/basketball', '6-3938.webp', 'Basketball Figure Male with Marble Base Trophy'),
    ('Golf trophies', 'Hole in one, nearest the pin and day winners', '7.45', 'trophies/g/golf', 'dsc08658-9498-4837.webp', 'Hole in 1 on Marble Base Trophy'),
]

SYDNEY_AREAS = [
    ('Hills District', ['Castle Hill', 'Baulkham Hills', 'Norwest']),
    ('Western Sydney', ['Blacktown', 'Parramatta', 'Granville', 'Auburn', 'Penrith']),
    ('South-West Sydney', ['Bankstown', 'Greenacre', 'Liverpool', 'Campbelltown', 'Campsie']),
    ('St George and south', ['Hurstville']),
    ('North and inner Sydney', ['Ryde', 'Epping', 'Chatswood', 'Pyrmont / Ultimo', 'Potts Point / Woolloomooloo']),
    ('Eastern Sydney', ['Bondi']),
]

# ---- shared chrome ---------------------------------------------------------


def read(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return f.read()


def chrome(depth):
    """Return (head_before_title, top_through_header, footer_through_end) from the Victoria page."""
    vic = read('trophies/victoria/index.html')
    start = vic.index('<div class="crumbs-section">')
    pre = vic[:start]
    foot_start = vic.index('<footer class="site-footer">')
    foot_end = vic.index('<script type="application/ld+json">')
    footer = vic[foot_start:foot_end]
    return pre, footer


def head(pre, title, desc, canon, depth):
    pre = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, pre, flags=re.S)
    pre = re.sub(r'(<meta name="description" content=")[^"]*(")', r'\g<1>%s\g<2>' % desc, pre)
    pre = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s\g<2>' % canon, pre)
    pre = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % title, pre)
    pre = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % desc, pre)
    pre = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s\g<2>' % canon, pre)
    # paths: Victoria state page is depth 2 ('../../'); adjust for deeper pages
    pre = pre.replace('../../assets/', '../' * depth + 'assets/')
    pre = pre.replace('Items to confirm are listed in README.md', 'Items to confirm are listed in README.md and NSW-PLAN.md')
    return pre


def fix_footer(footer, depth):
    return footer.replace('../../assets/', '../' * depth + 'assets/')


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, indent=1, ensure_ascii=False)


def store_schema(s):
    return {
        '@type': ['Store', 'LocalBusiness'],
        '@id': '%s/stores/%s#store' % (SITE, s['key']),
        'name': 'Alpha Trophies %s' % s['name'],
        'telephone': '+61 ' + PHONE,
        'email': 'sales@alphatrophies.com.au',
        'image': SITE + '/assets/frontend/img/logo.png',
        'priceRange': '$$',
        'currenciesAccepted': 'AUD',
        'address': {'@type': 'PostalAddress', 'streetAddress': s['street'], 'addressLocality': s['suburb'],
                    'addressRegion': 'NSW', 'postalCode': s['pc'], 'addressCountry': 'AU'},
        'hasMap': gmaps(s),
        **({'geo': {'@type': 'GeoCoordinates', 'latitude': s['lat'], 'longitude': s['lng']}} if s.get('lat') else {}),
        'parentOrganization': {'@type': 'Organization', 'name': 'Alpha Trophies', 'url': SITE},
        'areaServed': {'@type': 'State', 'name': 'New South Wales'},
    }


def faq_schema(items):
    return {'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]}


def faq_html(items):
    out = []
    for n, (q, a) in enumerate(items):
        out.append('      <details class="faq-item"%s><summary>%s</summary><div class="faq-answer"><p>%s</p></div></details>'
                   % (' open' if n == 0 else '', escape(q), escape(a)))
    return '\n'.join(out)


def crumbs(parts):
    out = ['<a href="%s/">Home</a>' % SITE]
    for label, href in parts:
        out.append('<span class="sep">›</span>' + ('<a href="%s">%s</a>' % (href, label) if href else '<span class="current">%s</span>' % label))
    return '<div class="crumbs-section"><div class="wrap crumbs">%s</div></div>' % ''.join(out)


def breadcrumb_schema(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}


DELIVERY_FACTS = ('Standard shipping is a $9.90 flat rate after 5 working days production. Express shipping is a $25 flat rate. '
                  'Fast Track is 4 working days ($40 plus 10% of the order, capped at $300) and Priority Rush is 3 working days '
                  '($50 plus 15% of the order, capped at $300).')

# ---------------------------------------------------------------------------
# NSW state page
# ---------------------------------------------------------------------------


def state_page():
    pre, footer = chrome(2)
    title = 'Custom Trophies NSW | Free Engraving | Alpha Trophies'
    desc = ('Custom trophies, medals and awards for NSW clubs, schools and businesses. Free engraving, flat-rate delivery statewide, two Sydney stores.')
    canon = SITE + '/trophies/new-south-wales/'
    faqs = [
        ('Do you deliver trophies across New South Wales?',
         'Yes. We deliver to every part of NSW, from Sydney to regional towns. Standard shipping is a $9.90 flat rate and express is a $25 flat rate, after 5 working days production.'),
        ('Where are your NSW stores?',
         'We have two Sydney locations: %s and %s.' % (addr(STORES[0]), addr(STORES[1]))),
        ('How fast can I get trophies for a presentation day?',
         'Fast Track is 4 working days ($40 plus 10% of the order, capped at $300). Priority Rush is 3 working days ($50 plus 15% of the order, capped at $300). Tell us your event date when you order.'),
        ('Do you do trophies for rugby league, surf life saving and swimming?',
         'Yes. These are some of our most popular NSW categories, and every item includes free engraving. Browse the tiles above or the full trophy range.'),
        ('Is engraving free?', 'Yes, free engraving on every order.'),
        ('Is there a minimum order?', 'No. Order one trophy or hundreds.'),
    ]
    tiles = '\n'.join(
        '<a class="cat-tile" href="%s/products/%s"><div class="thumb"><img src="../../%s%s" alt="%s" loading="lazy" width="140" height="140"></div>'
        '\n      <div class="body"><h3>%s</h3><p>%s</p><span class="from">From $%s</span></div></a>'
        % (SITE, url, IMG, img, alt, t, b, p) for t, b, p, url, img, alt in STATE_TILES)
    stores_html = ''.join(
        '<p style="font-size:15px;color:var(--text-muted);margin-bottom:14px"><strong>%s:</strong> %s</p>' % (s['name'], escape(addr(s)))
        for s in STORES)
    town_cards = chr(10).join(
        '    <div class="city-card live"><h3>%s</h3><p>%s.</p><a class="go" href="%s/">Trophies in %s <i class="fa-solid fa-arrow-right"></i></a></div>'
        % (escape(t['name']), escape(t['region']), t['slug'], escape(t['name'])) for t in TOWNS)
    # ---- directory (filter tabs + search) ----
    def grp(t):
        if t['slug'] in HUNTER_CC:
            return 'hunter'
        return 'regional'
    dir_cards = ['    <a class="dir-city" data-group="metro" data-search="sydney metropolitan riverwood castle hill" href="sydney/"><span class="dir-top"><span class="dir-tag dir-tag-gold">Metropolitan NSW</span><i class="fa-solid fa-store"></i></span><h3>Sydney</h3><p>Two locations: Riverwood in the south-west and Castle Hill in the Hills District. Suburb guide from Bondi to Penrith.</p><span class="dir-go">Trophies in Sydney <i class="fa-solid fa-arrow-right"></i></span></a>']
    for t in TOWNS:
        dir_cards.append('    <a class="dir-city" data-group="%s" data-search="%s" href="%s/"><span class="dir-top"><span class="dir-tag">%s</span><i class="fa-solid fa-truck"></i></span><h3>%s</h3><p>%s</p><span class="dir-go">Trophies in %s <i class="fa-solid fa-arrow-right"></i></span></a>'
                         % (grp(t), escape((t['name'] + ' ' + t['region']).lower()), t['slug'], escape(t['region']), escape(t['name']), escape(t['blurb']), escape(t['name'])))
    cities = (
        '<section id="cities" class="sec"><div class="wrap">\n'
        '  <div class="sec-header"><span class="sec-eyebrow">Statewide directory <span class="dir-count">%d locations</span></span><h2 class="sec-title">Find trophies near you across New South Wales</h2>\n'
        '  <p class="sec-sub">From Sydney to regional coastal towns and country associations, we engrave and deliver trophies, medals and awards to every corner of NSW.</p></div>\n'
        '  <div class="dir-tabs" role="group" aria-label="Filter locations">\n'
        '    <button type="button" class="dir-tab is-active" data-filter="all">All %d locations</button>\n'
        '    <button type="button" class="dir-tab" data-filter="metro">Metropolitan Sydney</button>\n'
        '    <button type="button" class="dir-tab" data-filter="hunter">Hunter &amp; Central Coast</button>\n'
        '    <button type="button" class="dir-tab" data-filter="regional">Regional NSW, South Coast &amp; Northern Rivers</button>\n'
        '  </div>\n'
        '  <div class="dir-search"><i class="fa-solid fa-magnifying-glass"></i><input type="search" id="dir-q" placeholder="Type your city or region (e.g. Newcastle, Dubbo, Sydney)" aria-label="Search NSW locations"></div>\n'
        '  <div class="dir-grid" id="dir-grid">\n%s\n  </div>\n'
        '  <p class="dir-empty" id="dir-empty" hidden>No match yet. Call %s and we will help.</p>\n'
        '</div></section>' % (len(TOWNS) + 1, len(TOWNS) + 1, chr(10).join(dir_cards), PHONE))

    # ---- featured product cards ----
    badges = ['Winter favourite', 'Presentation medals', 'Coastal clubs', 'Carnival season', 'Association sport', 'Day events']
    feat = []
    for (t, b2, p2, url, img, alt), badge in zip(STATE_TILES, badges):
        feat.append('<a class="feat-card" href="%s/products/%s"><div class="feat-img"><img src="../../%s%s" alt="%s" loading="lazy" width="320" height="240"><span class="feat-badge">%s</span></div>\n'
                    '      <div class="feat-body"><h3>%s</h3><p>%s</p>\n'
                    '      <div class="feat-chips"><span><i class="fa-regular fa-clock"></i> 3–5 days production</span><span><i class="fa-regular fa-circle-check"></i> Free engraving included</span></div>\n'
                    '      <div class="feat-price"><div><span class="feat-label">Starting price</span><strong>From $%s</strong></div><span class="feat-btn">Explore range <i class="fa-solid fa-arrow-right"></i></span></div></div></a>'
                    % (SITE, url, IMG, img, alt, badge, t, b2, p2))
    featured = (
        '<section class="sec sec-alt"><div class="wrap">\n'
        '  <div class="feat-head"><div><span class="sec-eyebrow" style="text-align:left">Statewide presentation favourites</span><h2 class="sec-title" style="text-align:left">Popular in NSW: trophies for NSW clubs and schools</h2>\n'
        '  <p class="sec-sub" style="text-align:left;margin:0">Browse the categories NSW clubs order most. Every award includes free engraving.</p></div>\n'
        '  <span class="feat-pill"><i class="fa-regular fa-circle-check"></i> Includes free engraving</span></div>\n'
        '  <div class="feat-grid">\n      %s\n  </div>\n</div></section>' % chr(10).join(feat))

    # ---- delivery + presentation days cards ----
    delivery = """<section class="sec"><div class="wrap dlv-grid">
  <div class="dlv-card">
    <div class="dlv-top"><span class="dlv-eyebrow"><i class="fa-solid fa-truck"></i> Statewide delivery</span><span class="dlv-badge">Flat-rate shipping</span></div>
    <h3>Delivered across NSW</h3>
    <p>Every NSW order is engraved in-house and sent to your door, whether you are in Sydney, the Hunter, the Illawarra or further out. Standard shipping is a $9.90 flat rate and express is $25, after 5 working days production.</p>
    <div class="dlv-opts">
      <div class="dlv-opt"><div class="dlv-opt-top"><span><i class="fa-solid fa-box"></i> Standard delivery</span><em>Regular</em></div><strong>$9.90 flat rate</strong><small>5 working days production, then shipping</small></div>
      <div class="dlv-opt"><div class="dlv-opt-top"><span><i class="fa-solid fa-bolt"></i> Express delivery</span><em class="hot">Faster</em></div><strong>$25 flat rate</strong><small>Express shipping after 5 working days production</small></div>
    </div>
    <div class="dlv-rush"><h4><i class="fa-regular fa-clock"></i> Rush options for deadlines</h4>
      <ul><li><span>Fast Track (4 working days)</span><strong>$40 + 10%, capped $300</strong></li><li><span>Priority Rush (3 working days)</span><strong>$50 + 15%, capped $300</strong></li></ul></div>
    <div class="dlv-foot"><span>Free engraving on every order</span><span>Questions? Call 1300 485 645</span></div>
  </div>
  <div class="dlv-card dlv-dark">
    <span class="dlv-eyebrow"><i class="fa-solid fa-trophy"></i> Built for NSW clubs</span>
    <h3>Made for NSW presentation days</h3>
    <p>Built for rugby league and rugby union clubs, surf life saving clubs, swimming carnivals, basketball associations and school presentation days. More than 70 trophy categories are available.</p>
    <ul class="dlv-list">
      <li><i class="fa-solid fa-football"></i> Rugby league and rugby union premierships</li>
      <li><i class="fa-solid fa-person-swimming"></i> Surf life saving patrol and nipper trophies</li>
      <li><i class="fa-solid fa-water-ladder"></i> Swimming carnivals and school presentation days</li>
      <li><i class="fa-solid fa-basketball"></i> Basketball association MVP and finals awards</li>
    </ul>
    <div class="dlv-note"><strong>More than 70 trophy categories</strong><span>Every piece includes free laser engraving</span></div>
  </div>
</div></section>"""

    body = '''
%(crumbs)s

<header class="hero"><div class="wrap hero-grid">
  <div class="hero-content">
    <div class="hero-badge-row"><span class="hero-tag"><i class="fa-solid fa-check"></i> Free engraving</span><span class="hero-local-chip"><i class="fa-solid fa-location-dot"></i> Sydney stores: Riverwood &amp; Castle Hill</span></div>
    <h1>Custom Trophies &amp; Awards in <span class="gold">New South Wales</span></h1>
    <p class="lead">Trophies, medals and awards for NSW clubs, schools and businesses. Engraved in-house and delivered anywhere in the state, with two Sydney stores to call on.</p>
    <div class="hero-ctas">
      <a class="btn-primary" href="#cities"><span>Choose your city</span><i class="fa-solid fa-arrow-right"></i></a>
      <a class="btn-secondary" href="sydney/"><i class="fa-solid fa-map-pin"></i><span>Sydney stores &amp; delivery</span></a>
    </div>
    <div class="hero-guarantees">
      <div class="guarantee-item"><i class="fa-solid fa-shield-halved"></i><div><strong>Trusted since 1985</strong><span>Australian-owned</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-bolt"></i><div><strong>3–5 days production</strong><span>Rush from day 3</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-award"></i><div><strong>No minimum order</strong><span>One trophy or hundreds</span></div></div>
    </div>
  </div>
  <div class="hero-visual"><div class="hero-visual-card">
    <img src="../../%(img)sdsc08883-3350.jpg" alt="Lifesaving Rescue Board Trophy" width="300" height="300">
    <div class="hero-badge-overlay"><div><div style="font-size:13px;font-weight:700;color:#fff">4.9 ★ Google rating</div><div style="font-size:12px;color:#d1d5db">232 reviews across all stores</div></div></div>
  </div></div>
</div></header>

%(cities)s

%(featured)s

%(delivery)s

<section id="store" class="sec sec-alt"><div class="wrap find-us-layout">
  <div>
    <span class="sec-eyebrow" style="text-align:left">Our NSW locations</span>
    <h2 class="sec-title" style="text-align:left">Alpha Trophies in Sydney</h2>
    %(stores_html)s
    <p style="font-size:15px;color:var(--text-muted);margin-bottom:14px"><strong>Phone:</strong> %(phone)s<br><strong>Email:</strong> sales@alphatrophies.com.au</p>
    <p><a class="btn-primary" href="sydney/#how-to-find-us" style="font-size:15px;padding:12px 22px"><i class="fa-solid fa-route"></i> See where we are in Sydney</a></p>
  </div>
  <div class="interactive-map-panel"><div class="map-embed-wrapper"><iframe title="Alpha Trophies Sydney map" src="%(embed)s" loading="lazy"></iframe></div></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><h2 class="sec-title">NSW trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

<div style="background:#fff;padding:22px 0;border-top:1px solid var(--border);font-size:14.5px"><div class="wrap">
  Browse: <a href="sydney/" style="color:var(--navy-900);font-weight:700">Sydney</a> &nbsp;|&nbsp; <a href="../victoria/" style="color:var(--navy-900);font-weight:700">Victoria</a> &nbsp;|&nbsp; <span style="color:var(--text-subtle)">SA page coming soon</span>
</div></div>

''' % {'crumbs': crumbs([('Trophies', SITE + '/products/trophies'), ('New South Wales', None)]),
       'img': IMG, 'tiles': tiles, 'stores_html': stores_html, 'phone': PHONE, 'town_cards': town_cards, 'cities': cities, 'featured': featured, 'delivery': delivery,
       'embed': embed(STORES[0]), 'faq': faq_html(faqs)}
    graph = [
        breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'), ('New South Wales', canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies New South Wales', 'url': canon,
         'about': {'@type': 'AdministrativeArea', 'name': 'New South Wales'}},
        {'@type': 'ItemList', 'name': 'NSW cities', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'url': canon + sl + '/'}
            for i, (n, sl) in enumerate([('Sydney', 'sydney')] + [(t['name'], t['slug']) for t in TOWNS])]},
    ] + [store_schema(s) for s in STORES] + [faq_schema(faqs)]
    page = head(pre, title, desc, canon, 2) + body + fix_footer(footer, 2) + ld({'@context': 'https://schema.org', '@graph': graph}) + \
        '\n<script src="../../assets/js/nav.js" defer></script><script src="../../assets/js/directory.js" defer></script></body></html>\n'
    return page


# ---------------------------------------------------------------------------
# Sydney hub
# ---------------------------------------------------------------------------


def sydney_page():
    pre, footer = chrome(3)
    title = 'Custom Trophies Sydney | Free Engraving | Alpha Trophies'
    desc = ('Custom trophies, medals and plaques in Sydney. Free engraving, delivery across Greater Sydney, stores at Riverwood and Castle Hill.')
    canon = SITE + '/trophies/new-south-wales/sydney/'
    faqs = [
        ('Where are your Sydney stores?',
         'We have two Sydney locations: %s, and %s. Call %s or email sales@alphatrophies.com.au with any questions about your order.' % (addr(STORES[0]), addr(STORES[1]), PHONE)),
        ('How much is delivery in Sydney?',
         'Standard shipping is a $9.90 flat rate after 5 working days production. Express shipping is a $25 flat rate.'),
        ('Can I get trophies in time for a presentation day?',
         'Fast Track is 4 working days ($40 plus 10% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15% of the order, capped at $300). Tell us your event date when you order.'),
        ('Do you make trophies for swimming carnivals and surf life saving clubs?',
         'Yes. We have swimming and lifesaving trophies and medals for champions, age groups, patrol teams and club awards, all with free engraving.'),
        ('Can you handle rugby league and rugby union clubs?',
         'Yes. Rugby trophies and medals suit juniors through to seniors, and there is no minimum order, so you can order for one player or the whole club.'),
        ('Is engraving free?', 'Yes, free engraving on every order.'),
    ]
    cards = []
    for name, cat, price, slug_, img in SYDNEY_PRODUCTS:
        cards.append('''      <article class="product-card"><div class="product-thumb-wrap"><img src="../../../%s%s" alt="%s" loading="lazy" width="180" height="180"></div>
      <div class="product-body"><span class="product-category">%s</span><h3 class="product-title">%s</h3>
      <div class="product-meta"><span class="free-engrave"><i class="fa-solid fa-circle-check"></i> Free engraving</span></div>
      <div class="product-footer"><div class="product-price-block"><span class="product-price-label">From</span><span class="product-price">$%s</span></div>
      <a href="%s/product/%s" class="btn-card-action">View</a></div></div></article>'''
                     % (IMG, img, escape(name), cat, escape(name), price, SITE, slug_))
    cards_html = '\n'.join(cards)

    def store_bar(s, note):
        return ('<div class="store-location"><div class="store-icon-wrap"><i class="fa-solid fa-shop"></i></div>'
                '<div class="store-details"><h4>%s</h4><p>%s &nbsp;·&nbsp; %s</p></div>'
                '<div class="store-actions"><a class="btn-store-action" href="%s" target="_blank" rel="noopener"><i class="fa-solid fa-location-arrow"></i> Google Maps</a></div></div>'
                % (s['name'], escape(addr(s)), note, gmaps(s)))

    areas = ''.join('<div class="suburb-card"><h4>%s</h4><p>%s</p></div>' % (
        region, ', '.join('<a href="%s/" style="color:var(--navy-900);font-weight:600">%s</a>' % (SUB_SLUG[n], n) for n in subs))
        for region, subs in SYDNEY_AREAS)
    sports = [
        ('Rugby league and rugby union', 'trophies/r/rugby-league', 'Trophies and medals for juniors through to seniors, from end-of-season presentation to player-of-the-match awards.'),
        ('Swimming', 'trophies/s/swimming', 'Carnival champions, age-group places and squad awards.'),
        ('Surf life saving', 'trophies/s/surf-life-saving', 'Patrol, nipper and club championship awards for the summer season.'),
        ('Soccer', 'trophies/s/soccer', 'Junior clubs through to senior leagues, including golden boot and coach awards.'),
        ('Netball', 'trophies/n/netball', 'Team and player awards for netball associations and school teams.'),
        ('Cricket', 'trophies/c/cricket', 'Batting, bowling and premiership awards.'),
    ]
    sports_html = ''.join('<div class="suburb-card"><h4><a href="%s/products/%s" style="color:inherit">%s</a></h4><p>%s</p></div>' % (SITE, u, t, d) for t, u, d in sports)
    body = '''
%(crumbs)s

<header class="hero"><div class="wrap hero-grid">
  <div class="hero-content">
    <div class="hero-badge-row"><span class="hero-tag"><i class="fa-solid fa-check"></i> Free engraving</span><span class="hero-local-chip"><i class="fa-solid fa-location-dot"></i> Riverwood &amp; Castle Hill, Sydney</span></div>
    <h1>Custom Trophies in <span class="gold">Sydney</span></h1>
    <p class="lead">Engraved in-house and delivered to your club, school or office across Greater Sydney. Two Sydney locations at Riverwood and Castle Hill.</p>
    <div class="hero-ctas">
      <a class="btn-primary" href="%(site)s/products/trophies"><span>Shop trophies</span><i class="fa-solid fa-arrow-right"></i></a>
      <a class="btn-secondary" href="#how-to-find-us"><i class="fa-solid fa-map-pin"></i><span>Where we are</span></a>
    </div>
    <div class="hero-guarantees">
      <div class="guarantee-item"><i class="fa-solid fa-shield-halved"></i><div><strong>Trusted since 1985</strong><span>Australian-owned</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-bolt"></i><div><strong>3–5 days production</strong><span>Rush from day 3</span></div></div>
      <div class="guarantee-item"><i class="fa-solid fa-award"></i><div><strong>No minimum order</strong><span>One trophy or hundreds</span></div></div>
    </div>
  </div>
  <div class="hero-visual"><div class="hero-visual-card">
    <img src="../../../%(img)selliptical-rugby-front-8620.jpg" alt="Elliptical Rugby Trophy" width="300" height="300">
    <div class="hero-badge-overlay"><div><div style="font-size:13px;font-weight:700;color:#fff">4.9 ★ Google rating</div><div style="font-size:12px;color:#d1d5db">232 reviews across all stores</div></div></div>
  </div></div>
</div></header>

<div class="store-bar"><div class="wrap store-bar-inner two-stores">
  %(bar1)s
  %(bar2)s
</div></div>

<section class="product-showcase-strip"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Popular with Sydney clubs and schools</span><h2 class="sec-title">Rugby, swimming and surf life saving awards</h2>
  <p class="sec-sub">Real products from our range, all with free engraving. Prices are the starting price on the product page.</p></div>
  <div class="product-grid" style="grid-template-columns:repeat(4,1fr)">
%(cards)s
  </div>
  <p style="text-align:center;margin-top:28px"><a class="btn-card-action" style="padding:12px 24px;font-size:14px" href="%(site)s/products/trophies">Browse all trophies</a></p>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Sydney delivery</span><h2 class="sec-title">How ordering works in Sydney</h2></div>
  <div class="order-ways-grid">
    <div class="order-card featured"><div>
      <div class="order-card-header"><div class="order-card-icon"><i class="fa-solid fa-truck-moving"></i></div><span class="order-pill rate">From $9.90</span></div>
      <h3>Delivered across Sydney</h3>
      <p>Order online, we engrave it in-house, and it is delivered to your club, school or workplace.</p>
      <ul class="timeline-list"><li><span>Standard shipping</span><strong>$9.90 flat rate, after 5 working days production</strong></li><li><span>Express shipping</span><strong>$25 flat rate</strong></li><li><span>Fast Track / Priority Rush</span><strong>4 / 3 working days production</strong></li></ul></div>
      <a href="%(site)s/delivery-information" class="btn-primary" style="justify-content:center"><i class="fa-solid fa-circle-info"></i> Full delivery information</a></div>
    <div class="order-card"><div>
      <div class="order-card-header"><div class="order-card-icon"><i class="fa-solid fa-headset"></i></div><span class="order-pill free">Talk to us</span></div>
      <h3>Big order or tight deadline?</h3>
      <p>Presentation nights, carnivals and grand finals have fixed dates. Call or email and we will confirm the right production option for yours.</p>
      <ul class="timeline-list"><li><span>Phone</span><strong>%(phone)s</strong></li><li><span>Email</span><strong>sales@alphatrophies.com.au</strong></li><li><span>Support hours</span><strong>Mon–Fri 9am–5pm</strong></li></ul></div>
      <a href="tel:1300485645" class="btn-secondary" style="background:var(--navy-900);border-color:var(--navy-900);justify-content:center"><i class="fa-solid fa-phone"></i> Call %(phone)s</a></div>
  </div>
</div></section>

<section id="how-to-find-us" class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Our Sydney locations</span><h2 class="sec-title">Where we are in Sydney</h2>
  <p class="sec-sub">Two locations, one in the south-west and one in the Hills District.</p></div>
  <div class="directions-grid">
    <div class="dir-card"><h4><i class="fa-solid fa-compass"></i> Riverwood</h4><p style="font-size:14px;color:var(--text-muted);margin-bottom:10px">%(a1)s</p><p style="font-size:14px;color:var(--text-muted)">In the Riverwood industrial precinct off Leedham Place, close to the M5 Motorway, Canterbury Road and King Georges Road. The closest of our locations for St George and south-west Sydney.</p>
    <p style="margin-top:12px"><a class="btn-store-action" href="%(g1)s" target="_blank" rel="noopener"><i class="fa-solid fa-location-arrow"></i> Open in Google Maps</a></p>
    <div class="map-embed-wrapper" style="margin-top:14px"><iframe title="Alpha Trophies Riverwood map" src="%(e1)s" loading="lazy"></iframe></div></div>
    <div class="dir-card"><h4><i class="fa-solid fa-compass"></i> Castle Hill</h4><p style="font-size:14px;color:var(--text-muted);margin-bottom:10px">%(a2)s</p><p style="font-size:14px;color:var(--text-muted)">In the Hoyle Avenue and Gladstone Road industrial area, near Carrington Road and Victoria Avenue. The closest of our locations for the Hills District.</p>
    <p style="margin-top:12px"><a class="btn-store-action" href="%(g2)s" target="_blank" rel="noopener"><i class="fa-solid fa-location-arrow"></i> Open in Google Maps</a></p>
    <div class="map-embed-wrapper" style="margin-top:14px"><iframe title="Alpha Trophies Castle Hill map" src="%(e2)s" loading="lazy"></iframe></div></div>
  </div>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Sydney suburbs</span><h2 class="sec-title">Delivered to every part of Sydney</h2>
  <p class="sec-sub">From the Hills to the eastern suburbs. These are the areas we hear from most.</p></div>
  <div class="suburb-grid-pickup">%(areas)s</div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Sydney sports</span><h2 class="sec-title">Trophies for the sports Sydney plays</h2></div>
  <div class="suburb-grid-pickup">%(sports)s</div>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Sydney</span><h2 class="sec-title">Sydney trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

<div style="background:#fff;padding:22px 0;border-top:1px solid var(--border);font-size:14.5px"><div class="wrap">
  <a href="../" style="color:var(--navy-900);font-weight:700"><i class="fa-solid fa-arrow-left"></i> All NSW trophies</a>
  <span style="margin:0 10px;color:#cbd5e1">|</span><a href="../#cities" style="color:var(--navy-900);font-weight:700">More NSW cities</a>
</div></div>

''' % {'crumbs': crumbs([('Trophies', SITE + '/products/trophies'), ('New South Wales', '../'), ('Sydney', None)]),
       'site': SITE, 'img': IMG, 'phone': PHONE, 'cards': cards_html, 'areas': areas, 'sports': sports_html,
       'faq': faq_html(faqs),
       'bar1': store_bar(STORES[0], 'Riverwood industrial precinct'),
       'bar2': store_bar(STORES[1], 'Castle Hill industrial area'),
       'a1': escape(addr(STORES[0])), 'a2': escape(addr(STORES[1])),
       'g1': gmaps(STORES[0]), 'g2': gmaps(STORES[1]), 'e1': embed(STORES[0]), 'e2': embed(STORES[1])}
    graph = [
        breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                           ('New South Wales', SITE + '/trophies/new-south-wales/'), ('Sydney', canon)]),
    ] + [store_schema(s) for s in STORES] + [faq_schema(faqs)]
    page = head(pre, title, desc, canon, 3) + body + fix_footer(footer, 3) + ld({'@context': 'https://schema.org', '@graph': graph}) + \
        '\n<script src="../../../assets/js/nav.js" defer></script></body></html>\n'
    return page


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('wrote', rel, len(text))


if __name__ == '__main__':
    write('trophies/new-south-wales/index.html', state_page())
    write('trophies/new-south-wales/sydney/index.html', sydney_page())
