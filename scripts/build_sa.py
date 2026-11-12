"""Generate every South Australia page: state hub, Adelaide hub, 19 Adelaide suburbs, 7 SA towns.

Run (from anywhere):
    python scripts/build_sa.py
    python scripts/build_nav.py        # injects the Trophies/Medals menu
    python scripts/check_unique.py     # uniqueness report (docs/south-australia/SA-UNIQUENESS.md)

Data: data/sa/sa_locations.json (suburbs, towns, drive data from the Prospect showroom),
      data/victoria/vic_products.json (live products, shared by all states).
Reuses the Victoria builder helpers (chrome, product cards, hero) so the look stays identical.
Products already used on Victoria pages are avoided first, so SA sets differ from VIC sets.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_vic as V  # noqa: E402

B = V.B
ROOT = V.ROOT
SITE = V.SITE
PHONE = '(08) 7070 1111'  # Prospect store line (Tom, 12 Nov 2026); site-wide chrome keeps 1300 485 645
TEL = 'tel:+61870701111'
escape = V.escape

# optional local customer names for SA (same format as data/victoria/vic_proof.json); empty until Tom supplies them
_PROOF_FILE = os.path.join(V.ROOT, 'data', 'sa', 'sa_proof.json')
PROOF = {}
if os.path.isfile(_PROOF_FILE):
    with open(_PROOF_FILE, encoding='utf-8') as _f:
        PROOF = {k: v for k, v in json.load(_f).items() if not k.startswith('_')}

with open(os.path.join(ROOT, 'data', 'sa', 'sa_locations.json'), encoding='utf-8') as _f:
    LOC = json.load(_f)
SUBS = LOC['suburbs']
TOWNS = LOC['towns']
SUB = {s['slug']: s for s in SUBS}
TOWN = {t['slug']: t for t in TOWNS}
LAT, LNG = LOC['store']['lat'], LOC['store']['lng']

STORE_ADDR = '56 Prospect Road, Prospect SA 5082'
GMAPS_STORE = 'https://maps.google.com/?q=Alpha+Trophies+56+Prospect+Rd+Prospect+SA+5082'
EMBED = 'https://maps.google.com/maps?q=%s,%s&amp;hl=en&amp;z=15&amp;output=embed' % (LAT, LNG)
LINK = V.LINK

# keep SA product sets different from the Victoria ones where the pools allow it
# (cached in data/sa/vic_used_slugs.json so the SA repo rebuilds identically without the Victoria pages)
_VIC_USED = os.path.join(ROOT, 'data', 'sa', 'vic_used_slugs.json')
_vic_dir = os.path.join(ROOT, 'trophies', 'victoria')
if os.path.isdir(_vic_dir):
    _slugs = set()
    for _dp, _, _fs in os.walk(_vic_dir):
        if 'index.html' in _fs:
            with open(os.path.join(_dp, 'index.html'), encoding='utf-8') as _f:
                _slugs.update(re.findall(r'/product/([a-z0-9-]+)"', _f.read()))
    with open(_VIC_USED, 'w', encoding='utf-8', newline='\n') as _f:
        json.dump(sorted(_slugs), _f, indent=0)
else:
    with open(_VIC_USED, encoding='utf-8') as _f:
        _slugs = set(json.load(_f))
V.USED.update(_slugs)


def drive_sentence(name, d):
    if not d['km']:
        return 'Our showroom is in Prospect itself, on Prospect Road, so pickup is a short trip for local clubs and schools.'
    return ('%s is about %s km by road from our Prospect showroom, via %s. Google Maps shows about %s in afternoon traffic.'
            % (name, V.km_text(d['km']), d['route'], d['time']))


def maps_dir(name):
    return 'https://www.google.com/maps/dir/%s+SA/56+Prospect+Rd,+Prospect+SA+5082/' % name.replace(' ', '+')


def store_schema():
    return {
        '@type': ['Store', 'LocalBusiness'], '@id': SITE + '/stores/prospect#store', 'name': 'Alpha Trophies Prospect',
        'telephone': '+61 8 7070 1111', 'email': 'sales@alphatrophies.com.au', 'image': SITE + '/assets/frontend/img/logo.png',
        'priceRange': '$$', 'currenciesAccepted': 'AUD',
        'address': {'@type': 'PostalAddress', 'streetAddress': '56 Prospect Road', 'addressLocality': 'Prospect',
                    'addressRegion': 'SA', 'postalCode': '5082', 'addressCountry': 'AU'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': LAT, 'longitude': LNG},
        'hasMap': GMAPS_STORE,
        'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification',
                                       'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                                       'opens': '09:00', 'closes': '17:00'}],
        'sameAs': ['https://www.facebook.com/alphatrophiesaustralia', 'https://www.instagram.com/alphatrophies/'],
        'parentOrganization': {'@type': 'Organization', 'name': 'Alpha Trophies', 'url': SITE},
        'areaServed': {'@type': 'State', 'name': 'South Australia'},
    }


def store_bar(note=None):
    note = ' &nbsp;·&nbsp; %s' % escape(note) if note else ''
    return ('<div class="store-bar" id="store"><div class="wrap store-bar-inner">\n'
            '  <div class="store-location"><div class="store-icon-wrap"><i class="fa-solid fa-shop"></i></div>\n'
            '  <div class="store-details"><h4>Prospect showroom <span class="store-badge"><i class="fa-solid fa-circle-check"></i> Free pickup</span></h4>\n'
            '  <p>%s &nbsp;·&nbsp; Mon–Fri 9am–5pm%s</p></div></div>\n'
            '  <div class="store-actions"><a class="btn-store-action" href="%s" target="_blank" rel="noopener"><i class="fa-solid fa-location-arrow"></i> Google Maps</a>\n'
            '  <a class="btn-store-action" href="tel:+61870701111"><i class="fa-solid fa-phone"></i> %s</a></div>\n'
            '</div></div>' % (escape(STORE_ADDR), note, GMAPS_STORE, PHONE))


# ---------------------------------------------------------------------------
# suburb page  /trophies/south-australia/adelaide/<suburb>/   (depth 4)
# ---------------------------------------------------------------------------

def suburb_page(s):
    depth = 4
    name = s['name']
    canon = '%s/trophies/south-australia/adelaide/%s/' % (SITE, s['slug'])
    d = s['drive']
    prods = V.product_set(s['sports'], 1)
    p0 = prods[0]
    here = not d['km']
    title = 'Trophies in %s, Adelaide | Alpha Trophies' % name
    if here:
        desc = 'Custom trophies, medals and plaques from our Prospect showroom on Prospect Road. Free engraving, free pickup, $9.90 flat-rate delivery.'
    else:
        desc = ('Custom trophies, medals and plaques for %s. Free engraving, %s km from our Prospect showroom, $9.90 flat-rate delivery.' % (name, V.km_text(d['km'])))
    drive_line = drive_sentence(name, d)
    near = [SUB[n] for n in s['near']]
    chips = ''.join('<a class="chip" href="../%s/" style="text-decoration:none">%s</a>' % (o['slug'], escape(o['name'])) for o in near)
    fact = (' ' + s['fact']) if s['fact'] else ''
    pickup_q = ('Where do I pick up trophies in Prospect?' if here else 'Can I pick up trophies from Prospect if I live in %s?' % name)
    faqs = [
        (pickup_q,
         '%s Orders are ready for pickup at %s, Monday to Friday 9am to 5pm, after 5 working days production. Priority Rush pickup is available from day 3 ($15 plus 20%% of the order, capped at $300). There is plenty of on-site parking.' % (drive_line, STORE_ADDR)),
        ('Do you deliver trophies to %s?' % name,
         'Yes. Standard shipping to %s is a $9.90 flat rate and express is $25, after 5 working days production. Pickup from Prospect has no shipping charge.' % name),
        ('Can I order %s trophies for a %s club or school?' % (V.SPORT_NAME[s['sports'][0]], name),
         'Yes. %s is one of the popular categories in the area, alongside %s. A good starting point is the %s, from $%s. Every item includes free engraving and there is no minimum order.' % (
             V.SPORT_NAME[s['sports'][0]].capitalize(), V.words(s['sports'][1:]), p0['name'], p0['price'])),
        ('How fast can I get trophies for a %s presentation day?' % name,
         'Standard production is 5 working days. Fast Track is 4 working days ($40 plus 10% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15%, capped at $300), plus delivery or pickup. Tell us the event date when you order.'),
    ]
    if here:
        left = ('<h3>Our showroom on Prospect Road</h3><p>%s</p><p><a class="btn-store-action" href="%s" target="_blank" rel="noopener"><i class="fa-solid fa-route"></i> Open in Google Maps</a></p>'
                % (escape(drive_line), GMAPS_STORE))
    else:
        left = ('<h3>Getting from %s to Prospect</h3><p>%s</p><p><a class="btn-store-action" href="%s" target="_blank" rel="noopener"><i class="fa-solid fa-route"></i> Directions from %s</a></p>'
                % (escape(name), escape(drive_line), maps_dir(name), escape(name)))
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
  <div>%(left)s</div>
  <div><h3>Pickup or delivery to %(name)s</h3>
  <p>Collect from Prospect after 5 working days, or from day 3 with Priority Rush pickup. Prefer delivery? Standard shipping is a $9.90 flat rate and express is $25, after production.</p>
  <p>Typical orders from %(name)s include %(occ)s.</p></div>
</div></section>

<section class="sec"><div class="wrap copy-two">
  <div><h3>About %(name)s</h3>
  <p>%(blurb)s %(name)s is in the City of %(lga)s, in %(region)s, with %(pop)s (one of the 20 largest areas on our Adelaide list).%(fact)s</p></div>
  <div><h3>Nearby Adelaide suburbs</h3>
  <div class="chip-list">%(chips)s</div>
  <p style="margin-top:14px;font-size:15px;color:var(--text-muted)">See the full <a href="../" %(link)s>Adelaide trophies page</a> or call <a href="tel:+61870701111" %(link)s>%(phone)s</a>.</p></div>
</div></section>

%(proof)s<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(name)s</span><h2 class="sec-title">%(name)s trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

%(foot)s

''' % {'proof': V.proof_html(name, PROOF.get(s['slug'])),
       'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('South Australia', '../../'), ('Adelaide', '../'), (escape(name), None)]),
       'hero': V.hero(name, '%s Engraved in-house, ready for pickup in Prospect or delivered to %s clubs, schools and businesses.' % (s['blurb'], name),
                      s['region'], p0, '#directions', 'Our showroom' if here else 'Getting to Prospect'),
       'store': store_bar(None if here else '%s km from %s' % (V.km_text(d['km']), name)), 'name': escape(name),
       'sportline': escape(s['sportline']), 'cards': '\n'.join(V.card(p) for p in prods), 'left': left,
       'occ': escape(s['occasion']), 'blurb': escape(s['blurb']), 'lga': escape(s['lga']), 'region': escape(s['region']),
       'pop': escape(s['pop_text']), 'fact': escape(fact), 'chips': chips, 'link': LINK, 'phone': PHONE,
       'faq': B.faq_html(faqs),
       'foot': V.FOOT_STRIP % ('<a href="../" %s><i class="fa-solid fa-arrow-left"></i> Trophies in Adelaide</a>'
                               '<span style="margin:0 10px;color:#cbd5e1">|</span><a href="../../" %s>All South Australia trophies</a>' % (LINK, LINK))}
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                             ('South Australia', SITE + '/trophies/south-australia/'),
                             ('Adelaide', SITE + '/trophies/south-australia/adelaide/'), (name, canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies in %s' % name, 'url': canon,
         'about': {'@type': 'Place', 'name': '%s, Adelaide' % name}},
        V.itemlist('Featured products in %s' % name, prods),
        B.faq_schema(faqs),
    ]
    return V.page(depth, title, desc, canon, body, graph)


# ---------------------------------------------------------------------------
# town page  /trophies/south-australia/<town>/   (depth 3)
# ---------------------------------------------------------------------------

def town_page(t):
    depth = 3
    name = t['name']
    short = t['short']
    canon = '%s/trophies/south-australia/%s/' % (SITE, t['slug'])
    d = t['drive']
    km = V.km_text(d['km'])
    prods = V.product_set(t['sports'], 2)
    p0 = prods[0]
    title = 'Trophies in %s | Alpha Trophies' % name
    desc = ('Custom trophies, medals and plaques delivered to %s, about %s km from Adelaide. Free engraving, $9.90 flat-rate shipping, no minimum order.' % (short, km))
    drive_line = drive_sentence(short, d)
    fact = (' ' + t['fact']) if t['fact'] else ''
    faqs = [
        ('Do you deliver trophies to %s?' % short,
         'Yes. %s is about %s km from our Adelaide showroom, and we deliver there with standard shipping at a $9.90 flat rate or express at $25, after 5 working days production.' % (short, km)),
        ('Can you make %s trophies for %s clubs?' % (V.SPORT_NAME[t['sports'][0]], short),
         'Yes. %s and %s are among the main categories for %s, and every item includes free engraving. Popular picks include the %s, from $%s. There is no minimum order.' % (
             V.SPORT_NAME[t['sports'][0]].capitalize(), V.SPORT_NAME[t['sports'][1]], short, p0['name'], p0['price'])),
        ('How fast can I get trophies to %s for a presentation day?' % short,
         'Standard production is 5 working days, plus delivery to %s. Fast Track is 4 working days ($40 plus 10%% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15%% of the order, capped at $300), also plus delivery. Tell us the event date when you order.' % short),
        ('Can I collect my order instead of having it delivered to %s?' % short,
         'Yes, if you are coming to Adelaide. Pickup is from %s, Monday to Friday 9am to 5pm, with no shipping charge. %s' % (STORE_ADDR, drive_line)),
        ('Is engraving free?', 'Yes, free engraving on every order, and there is no minimum order.'),
    ]
    near = [TOWN[n] for n in t['near']]
    chips = ''.join('<a class="chip" href="../%s/" style="text-decoration:none">%s</a>' % (o['slug'], escape(o['name'])) for o in near)
    body = '''
%(crumbs)s

%(hero)s

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Popular in %(short)s</span><h2 class="sec-title">Trophies and medals for %(short)s clubs and schools</h2>
  <p class="sec-sub">%(sportline)s Every item includes free engraving.</p></div>
  <div class="product-grid" style="grid-template-columns:repeat(4,1fr)">
%(cards)s
  </div>
</div></section>

<section class="sec sec-alt"><div class="wrap copy-two">
  <div><h3>Delivered to %(short)s</h3>
  <p>%(drive)s Every order is engraved in-house, then sent by standard shipping at a $9.90 flat rate or express at $25, after 5 working days production.</p>
  <p>The %(name)s area has about %(pop)s residents (ABS estimate, June 2025), %(growth)s over the past ten years, and ranks number %(rank)d of the South Australian urban areas on our list.</p></div>
  <div><h3>Presentation days in %(region)s</h3>
  <p>%(blurb)s%(fact)s</p>
  <p>We regularly see orders from the area for %(occ)s. Fast Track (4 working days) and Priority Rush (3 working days) are available at checkout when a date is fixed.</p></div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Also delivering nearby</span><h2 class="sec-title">Other South Australian towns near %(short)s</h2></div>
  <div class="chip-list" style="justify-content:center">%(chips)s</div>
  <p style="text-align:center;margin-top:24px;font-size:15px;color:var(--text-muted)">Order online and we deliver, or collect from our Prospect showroom. Questions? Call <a href="tel:+61870701111" %(link)s>%(phone)s</a> or email <a href="mailto:sales@alphatrophies.com.au" %(link)s>sales@alphatrophies.com.au</a>. See the <a href="../adelaide/" %(link)s>Adelaide page</a> for directions to the showroom.</p>
</div></section>

%(proof)s<section id="faq" class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">%(short)s</span><h2 class="sec-title">%(short)s trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

%(foot)s

''' % {'proof': V.proof_html(short, PROOF.get(t['slug'])),
       'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('South Australia', '../'), (escape(name), None)]),
       'hero': V.hero(name, '%s Engraved in-house and delivered to %s clubs, schools and businesses.' % (t['blurb'], short),
                      t['region'], p0, '#faq', 'Delivery and FAQs'),
       'name': escape(name), 'short': escape(short), 'sportline': escape(t['sportline']),
       'cards': '\n'.join(V.card(p) for p in prods), 'drive': escape(drive_line), 'pop': V.fmt_pop(t['pop']),
       'growth': V.growth_text(t['growth']), 'rank': t['rank'], 'region': escape(t['region']), 'blurb': escape(t['blurb']),
       'fact': escape(fact), 'occ': escape(t['occasion']), 'chips': chips, 'link': LINK, 'phone': PHONE, 'faq': B.faq_html(faqs),
       'foot': V.FOOT_STRIP % ('<a href="../" %s><i class="fa-solid fa-arrow-left"></i> All South Australia trophies</a>'
                               '<span style="margin:0 10px;color:#cbd5e1">|</span><a href="../adelaide/" %s>Adelaide showroom</a>' % (LINK, LINK))}
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                             ('South Australia', SITE + '/trophies/south-australia/'), (name, canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies in %s' % name, 'url': canon,
         'about': {'@type': 'City', 'name': short}},
        V.itemlist('Featured products in %s' % short, prods),
        B.faq_schema(faqs),
    ]
    return V.page(depth, title, desc, canon, body, graph)


# ---------------------------------------------------------------------------
# Adelaide hub  /trophies/south-australia/adelaide/   (depth 3)
# ---------------------------------------------------------------------------

def adelaide_page():
    depth = 3
    canon = SITE + '/trophies/south-australia/adelaide/'
    title = 'Custom Trophies Adelaide | Prospect Pickup | Alpha Trophies'
    desc = ('Custom trophies, medals and awards in Adelaide. Free engraving, free pickup from our Prospect showroom on Prospect Road, or delivered across Adelaide.')
    prods = V.product_set(['afl', 'soccer', 'netball', 'cricket', 'basketball', 'lawnbowls', 'schoolmedals', 'plaques'], 1)
    faqs = [
        ('Where can I pick up trophies in Adelaide?',
         'From our Prospect showroom at %s, Monday to Friday 9am to 5pm. It is on Prospect Road, about 4 km north of the CBD, with plenty of on-site parking.' % STORE_ADDR),
        ('How fast can you engrave for a presentation night?',
         'Standard production is 5 working days. Fast Track is 4 working days ($40 plus 10% of the order, capped at $300) and Priority Rush is 3 working days ($50 plus 15%, capped at $300). Rush pickup is $15 plus 20% of the order, capped at $300.'),
        ('Do you deliver to outer suburbs like Aldinga Beach and Gawler?',
         'Yes. Standard shipping is a $9.90 flat rate and express is $25, after 5 working days production.'),
        ('Is engraving free?', 'Yes, free engraving on every order, and there is no minimum order.'),
        ('Is there parking at the Prospect showroom?', 'Yes, there is plenty of on-site parking at the Prospect showroom.'),
        ('Can I see products before I order?', 'Yes. Visit the Prospect showroom during opening hours to see samples and talk to the team.'),
    ]
    cards = []
    for s in SUBS:
        d = s['drive']
        km_line = ('Our showroom is here on Prospect Road.' if not d['km']
                   else '%s km from our store via %s.' % (V.km_text(d['km']), escape(d['route'])))
        cards.append('    <div class="suburb-card"><h4><a href="%s/" style="color:var(--navy-900)">%s</a></h4><p>%s %s</p></div>'
                     % (s['slug'], escape(s['name']), km_line, escape(s['sportline'])))
    def card_dir(title_, rows):
        lis = ''.join('<p style="font-size:14px;color:var(--text-muted);margin-bottom:8px"><strong>%s:</strong> %s km, about %s via %s.</p>'
                      % (escape(n), V.km_text(k), tm, escape(rt)) for n, k, tm, rt in rows)
        return '<div class="dir-card"><h4><i class="fa-solid fa-compass"></i> %s</h4>%s</div>' % (title_, lis)
    dirs = ''.join([
        card_dir('From the CBD and North Adelaide', [('Adelaide CBD', 4.2, '15 min', 'Prospect Road and King William Road'),
                                                      ('North Adelaide', 2.4, '6 min', 'Prospect Road and Jeffcott Road')]),
        card_dir('From the northern suburbs', [('Mawson Lakes', 12.5, '21 min', 'the A22'), ('Parafield Gardens', 14.3, '21 min', 'the A22 and Port Wakefield Road'),
                                                ('Salisbury North', 23.2, '27 min', 'the Northern Expressway (M2)')]),
        card_dir('From the southern suburbs', [('Hallett Cove', 27.1, '49 min', 'the Southern Expressway (M2)'),
                                                ('Happy Valley', 25.9, '47 min', 'the Southern Expressway (M2)'),
                                                ('Morphett Vale', 28.7, '49 min', 'the Southern Expressway (M2)')]),
        card_dir('From the Hills and the outer north', [('Athelstone', 12.6, '24 min', 'Gorge Road (B31)'),
                                                         ('Mount Barker', 38.3, '47 min', 'the South Eastern Freeway (M1)'),
                                                         ('Gawler', 50.5, '40 min', 'the Northern Expressway (M2)')]),
    ])
    body = '''
%(crumbs)s

%(hero)s

%(store)s

<section class="product-showcase-strip"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Popular with Adelaide clubs and schools</span><h2 class="sec-title">Featured trophies, medals and plaques</h2>
  <p class="sec-sub">Real products from our range, all with free engraving. Prices are the starting price on the product page.</p></div>
  <div class="product-grid" style="grid-template-columns:repeat(4,1fr)">
%(cards)s
  </div>
  <p style="text-align:center;margin-top:28px"><a class="btn-card-action" style="padding:12px 24px;font-size:14px" href="%(site)s/products/trophies">Browse all trophies</a></p>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Adelaide fulfilment</span><h2 class="sec-title">Two ways to get your trophies in Adelaide</h2></div>
  <div class="order-ways-grid">
    <div class="order-card featured"><div>
      <div class="order-card-header"><div class="order-card-icon"><i class="fa-solid fa-warehouse"></i></div><span class="order-pill free">Free pickup</span></div>
      <h3>Pick up in Prospect</h3>
      <p>Order online, we engrave it, you collect Monday to Friday 9am to 5pm.</p>
      <ul class="timeline-list"><li><span>Standard pickup</span><strong>5 working days, no surcharge</strong></li><li><span>Priority Rush pickup</span><strong>Day 3 ($15 + 20%%, max $300)</strong></li><li><span>Showroom</span><strong>56 Prospect Road, Prospect</strong></li></ul></div>
      <a href="#how-to-find-us" class="btn-primary" style="justify-content:center"><i class="fa-solid fa-map-location-dot"></i> Directions</a></div>
    <div class="order-card"><div>
      <div class="order-card-header"><div class="order-card-icon"><i class="fa-solid fa-truck-moving"></i></div><span class="order-pill rate">From $9.90</span></div>
      <h3>Delivered across Adelaide</h3>
      <p>Delivery timing is the same across metro Adelaide: 5 working days production, then shipping.</p>
      <ul class="timeline-list"><li><span>Standard shipping</span><strong>$9.90 flat rate</strong></li><li><span>Express shipping</span><strong>$25 flat rate</strong></li><li><span>Fast Track / Priority Rush</span><strong>4 / 3 working days production</strong></li></ul></div>
      <a href="%(site)s/delivery-information" class="btn-secondary" style="background:var(--navy-900);border-color:var(--navy-900);justify-content:center"><i class="fa-solid fa-circle-info"></i> Full delivery information</a></div>
  </div>
</div></section>

<section id="how-to-find-us" class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Local showroom</span><h2 class="sec-title">How to find our Prospect store</h2>
  <p class="sec-sub">We are at <strong>56 Prospect Road</strong>, Prospect, about 4 km north of the Adelaide CBD. Distances and times below are from Google Maps in afternoon traffic.</p></div>
  <div class="find-us-layout">
    <div>
      <h3 style="font-size:20px;font-weight:700;color:var(--navy-900);margin-bottom:8px"><i class="fa-solid fa-car" style="color:var(--gold-500);margin-right:8px"></i>By car or van (best for bulk pickups)</h3>
      <p style="font-size:14px;color:var(--text-muted);margin-bottom:16px">Bulk trophy orders are boxed and heavy, so driving is the easiest way to collect.</p>
      <div class="directions-grid">%(dirs)s</div>
      <div style="background:#fff;border:1px solid var(--border);border-radius:var(--radius-md);padding:18px;margin-top:20px">
        <h4 style="font-size:15px;font-weight:700;color:var(--navy-900);margin-bottom:6px"><i class="fa-solid fa-square-parking" style="color:var(--gold-500);margin-right:6px"></i>Parking</h4>
        <p style="font-size:13.5px;color:var(--text-muted)">Plenty of on-site parking at the Prospect showroom, so loading a boxed order is easy.</p>
      </div>
    </div>
    <div class="interactive-map-panel">
      <div class="map-embed-wrapper"><iframe title="Alpha Trophies Prospect map" src="%(embed)s" loading="lazy"></iframe></div>
      <div class="map-meta-box"><p style="margin-bottom:8px"><strong>Address:</strong> %(addr)s</p><p style="margin-bottom:8px"><strong>Hours:</strong> Mon–Fri 9:00am–5:00pm</p><p style="margin-bottom:14px"><strong>Contact:</strong> %(phone)s | sales@alphatrophies.com.au</p>
      <a class="btn-primary" href="%(gm)s" target="_blank" rel="noopener" style="font-size:13.5px;padding:10px 18px;width:100%%;justify-content:center"><i class="fa-solid fa-arrow-up-right-from-square"></i> Open in Google Maps</a></div>
    </div>
  </div>
</div></section>

<section id="suburbs" class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Adelaide suburbs</span><h2 class="sec-title">Close by, or delivered to you</h2>
  <p class="sec-sub">Pick your suburb for the drive to our Prospect showroom and a trophy range for local clubs. Distances are by road, from Google Maps.</p></div>
  <div class="suburb-grid-pickup">
%(subs)s
  </div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-header"><span class="sec-eyebrow">Adelaide</span><h2 class="sec-title">Adelaide trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

%(foot)s

''' % {'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('South Australia', '../'), ('Adelaide', None)]),
       'hero': V.hero('Adelaide', 'Engraved in-house and ready for free pickup at our Prospect showroom, or delivered to your club, school or office anywhere in Adelaide.',
                      'Prospect showroom & Adelaide metro', prods[0], '#how-to-find-us', 'How to find our store'),
       'store': store_bar('Prospect Road, 4 km north of the CBD'), 'cards': '\n'.join(V.card(p) for p in prods), 'site': SITE,
       'dirs': dirs, 'embed': EMBED, 'addr': escape(STORE_ADDR), 'phone': PHONE, 'gm': GMAPS_STORE,
       'subs': '\n'.join(cards), 'faq': B.faq_html(faqs),
       'foot': V.FOOT_STRIP % ('<a href="../" %s><i class="fa-solid fa-arrow-left"></i> All South Australia trophies</a>'
                               '<span style="margin:0 10px;color:#cbd5e1">|</span><a href="../#cities" %s>More SA cities</a>' % (LINK, LINK))}
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'),
                             ('South Australia', SITE + '/trophies/south-australia/'), ('Adelaide', canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies Adelaide', 'url': canon, 'about': {'@type': 'City', 'name': 'Adelaide'}},
        store_schema(), V.itemlist('Featured products in Adelaide', prods),
        {'@type': 'ItemList', 'name': 'Adelaide suburbs', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': s['name'], 'url': '%s%s/' % (canon, s['slug'])} for i, s in enumerate(SUBS)]},
        B.faq_schema(faqs),
    ]
    return V.page(depth, title, desc, canon, body, graph)


# ---------------------------------------------------------------------------
# South Australia state page   (depth 2)
# ---------------------------------------------------------------------------

STATE_TILES = [
    ('afl', 'Premiership, best-and-fairest and junior footy awards', 'Winter favourite'),
    ('netball', 'Team, player and association awards', 'Association sport'),
    ('soccer', 'Junior clubs through to senior leagues', 'Club season'),
    ('cricket', 'Batting, bowling and premiership awards', 'Summer favourite'),
    ('lawnbowls', 'Club pennants, pairs and fours', 'Club events'),
    ('schoolmedals', 'Presentation-day medals for every subject and sport', 'School awards'),
]


def state_page():
    depth = 2
    canon = SITE + '/trophies/south-australia/'
    title = 'Custom Trophies South Australia | Free Engraving | Alpha Trophies'
    desc = ('Custom trophies, medals and awards for South Australian clubs, schools and businesses. Free engraving, flat-rate delivery statewide, Adelaide showroom.')
    faqs = [
        ('Do you deliver trophies across South Australia?',
         'Yes. We deliver to every part of South Australia, from Adelaide to regional towns such as Mount Gambier, Whyalla and Port Lincoln. Standard shipping is a $9.90 flat rate and express is a $25 flat rate, after 5 working days production.'),
        ('Where is your South Australian store?',
         'Our South Australian showroom is at %s. It is open Monday to Friday 9am to 5pm, with plenty of on-site parking.' % STORE_ADDR),
        ('Can I pick up my order in Adelaide?',
         'Yes. Pickup from Prospect has no shipping charge. Standard pickup is after 5 working days production and Priority Rush pickup is available from day 3 ($15 plus 20% of the order, capped at $300).'),
        ('How fast can I get trophies for a presentation day?',
         'Fast Track is 4 working days ($40 plus 10% of the order, capped at $300). Priority Rush is 3 working days ($50 plus 15% of the order, capped at $300). Tell us your event date when you order.'),
        ('Do you do trophies for AFL, netball and cricket clubs?',
         'Yes. These are among our most popular South Australian categories, and every item includes free engraving. Browse the categories above or the full trophy range.'),
        ('Is engraving free?', 'Yes, free engraving on every order. There is no minimum order.'),
    ]
    feat = []
    for key, blurb, badge in STATE_TILES:
        items = V.PROD[key]['items']
        rep = items[min(4, len(items) - 1)]
        label = {'schoolmedals': 'School medals'}.get(key, V.LABEL[key] + ' trophies')
        feat.append('<a class="feat-card" href="%s/%s"><div class="feat-img"><img src="%s" alt="%s" loading="lazy" width="320" height="240"><span class="feat-badge">%s</span></div>\n'
                    '      <div class="feat-body"><h3>%s</h3><p>%s</p>\n'
                    '      <div class="feat-chips"><span><i class="fa-regular fa-clock"></i> 3–5 days production</span><span><i class="fa-regular fa-circle-check"></i> Free engraving included</span></div>\n'
                    '      <div class="feat-price"><div><span class="feat-label">Starting price</span><strong>From $%.2f</strong></div><span class="feat-btn">Explore range <i class="fa-solid fa-arrow-right"></i></span></div></div></a>'
                    % (SITE, V.PROD[key]['path'], rep['img'], escape(V.unescape(rep['name'])), badge, label, blurb, V.min_price(key)))
    featured = (
        '<section class="sec sec-alt"><div class="wrap">\n'
        '  <div class="feat-head"><div><span class="sec-eyebrow" style="text-align:left">Statewide presentation favourites</span><h2 class="sec-title" style="text-align:left">Popular in South Australia: trophies for SA clubs and schools</h2>\n'
        '  <p class="sec-sub" style="text-align:left;margin:0">Browse the categories South Australian clubs order most. Every award includes free engraving.</p></div>\n'
        '  <span class="feat-pill"><i class="fa-regular fa-circle-check"></i> Includes free engraving</span></div>\n'
        '  <div class="feat-grid">\n      %s\n  </div>\n</div></section>' % '\n'.join(feat))
    cards = ['    <a class="dir-city" data-group="metro" data-search="adelaide metropolitan prospect showroom suburbs" href="adelaide/"><span class="dir-top"><span class="dir-tag dir-tag-gold">Greater Adelaide</span><i class="fa-solid fa-store"></i></span><h3>Adelaide</h3><p>Our Prospect showroom with free pickup, plus a suburb guide covering 19 Adelaide suburbs from Henley Beach to Aldinga Beach.</p><span class="dir-go">Trophies in Adelaide <i class="fa-solid fa-arrow-right"></i></span></a>']
    for t in TOWNS:
        cards.append('    <a class="dir-city" data-group="%s" data-search="%s" href="%s/"><span class="dir-top"><span class="dir-tag">%s</span><i class="fa-solid fa-truck"></i></span><h3>%s</h3><p>%s</p><span class="dir-go">Trophies in %s <i class="fa-solid fa-arrow-right"></i></span></a>'
                     % (t['group'], escape((t['name'] + ' ' + t['region']).lower()), t['slug'], escape(t['region']), escape(t['name']), escape(t['blurb']), escape(t['short'])))
    total = len(TOWNS) + 1
    cities = (
        '<section id="cities" class="sec"><div class="wrap">\n'
        '  <div class="sec-header"><span class="sec-eyebrow">Statewide directory <span class="dir-count">%d locations</span></span><h2 class="sec-title">Find trophies near you across South Australia</h2>\n'
        '  <p class="sec-sub">From Adelaide to the Fleurieu, the Limestone Coast and the Spencer Gulf, we engrave and deliver trophies, medals and awards to every corner of South Australia.</p></div>\n'
        '  <div class="dir-tabs" role="group" aria-label="Filter locations">\n'
        '    <button type="button" class="dir-tab is-active" data-filter="all">All %d locations</button>\n'
        '    <button type="button" class="dir-tab" data-filter="metro">Greater Adelaide</button>\n'
        '    <button type="button" class="dir-tab" data-filter="south">Fleurieu, Murraylands &amp; South East</button>\n'
        '    <button type="button" class="dir-tab" data-filter="north">Spencer Gulf &amp; Eyre Peninsula</button>\n'
        '  </div>\n'
        '  <div class="dir-search"><i class="fa-solid fa-magnifying-glass"></i><input type="search" id="dir-q" placeholder="Type your city or region (e.g. Adelaide, Mount Gambier, Whyalla)" aria-label="Search South Australian locations"></div>\n'
        '  <div class="dir-grid" id="dir-grid">\n%s\n  </div>\n'
        '  <p class="dir-empty" id="dir-empty" hidden>No match yet. Call %s and we will help.</p>\n'
        '</div></section>' % (total, total, '\n'.join(cards), PHONE))
    suburbs = (
        '<section class="sec sec-alt"><div class="wrap">\n'
        '  <div class="sec-header"><span class="sec-eyebrow">Adelaide suburbs</span><h2 class="sec-title">Trophies in your Adelaide suburb</h2>\n'
        '  <p class="sec-sub">Each suburb page shows the drive to our Prospect showroom and a trophy range for local clubs.</p></div>\n'
        '  <div class="chip-list" style="justify-content:center">%s</div>\n'
        '</div></section>' % ''.join('<a class="chip" href="adelaide/%s/" style="text-decoration:none">%s</a>' % (s['slug'], escape(s['name'])) for s in SUBS))
    delivery = """<section class="sec"><div class="wrap dlv-grid">
  <div class="dlv-card">
    <div class="dlv-top"><span class="dlv-eyebrow"><i class="fa-solid fa-truck"></i> Statewide delivery</span><span class="dlv-badge">Flat-rate shipping</span></div>
    <h3>Delivered across South Australia</h3>
    <p>Every South Australian order is engraved in-house and sent to your door, whether you are in Adelaide, the Fleurieu, the Limestone Coast or the Spencer Gulf. Standard shipping is a $9.90 flat rate and express is $25, after 5 working days production.</p>
    <div class="dlv-opts">
      <div class="dlv-opt"><div class="dlv-opt-top"><span><i class="fa-solid fa-box"></i> Standard delivery</span><em>Regular</em></div><strong>$9.90 flat rate</strong><small>5 working days production, then shipping</small></div>
      <div class="dlv-opt"><div class="dlv-opt-top"><span><i class="fa-solid fa-bolt"></i> Express delivery</span><em class="hot">Faster</em></div><strong>$25 flat rate</strong><small>Express shipping after 5 working days production</small></div>
    </div>
    <div class="dlv-rush"><h4><i class="fa-regular fa-clock"></i> Rush options for deadlines</h4>
      <ul><li><span>Fast Track (4 working days)</span><strong>$40 + 10%, capped $300</strong></li><li><span>Priority Rush (3 working days)</span><strong>$50 + 15%, capped $300</strong></li></ul></div>
    <div class="dlv-foot"><span>Free engraving on every order</span><span>Questions? Call 1300 485 645</span></div>
  </div>
  <div class="dlv-card dlv-dark">
    <span class="dlv-eyebrow"><i class="fa-solid fa-trophy"></i> Built for South Australian clubs</span>
    <h3>Made for South Australian presentation days</h3>
    <p>Built for AFL and netball clubs, cricket associations, soccer clubs, lawn bowls pennants and school presentation days. More than 70 trophy categories are available.</p>
    <ul class="dlv-list">
      <li><i class="fa-solid fa-football"></i> Football-netball premierships and best-and-fairest awards</li>
      <li><i class="fa-solid fa-baseball-bat-ball"></i> Summer cricket club and association awards</li>
      <li><i class="fa-solid fa-futbol"></i> Soccer and basketball season awards</li>
      <li><i class="fa-solid fa-school"></i> School presentation days and sports carnivals</li>
    </ul>
    <div class="dlv-note"><strong>Free pickup in Prospect</strong><span>Every piece includes free laser engraving</span></div>
  </div>
</div></section>"""
    hero_prod = V._clean(V.PROD['afl']['items'][5], 'AFL')
    body = '''
%(crumbs)s

<header class="hero"><div class="wrap hero-grid">
  <div class="hero-content">
    <div class="hero-badge-row"><span class="hero-tag"><i class="fa-solid fa-check"></i> Free engraving</span><span class="hero-local-chip"><i class="fa-solid fa-location-dot"></i> Adelaide showroom: Prospect</span></div>
    <h1>Custom Trophies &amp; Awards in <span class="gold">South Australia</span></h1>
    <p class="lead">Trophies, medals and awards for South Australian clubs, schools and businesses. Engraved in-house, delivered anywhere in the state, with free pickup from our Prospect showroom in Adelaide.</p>
    <div class="hero-ctas">
      <a class="btn-primary" href="#cities"><span>Choose your city</span><i class="fa-solid fa-arrow-right"></i></a>
      <a class="btn-secondary" href="adelaide/"><i class="fa-solid fa-map-pin"></i><span>Adelaide store &amp; directions</span></a>
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
    <span class="sec-eyebrow" style="text-align:left">Our South Australian location</span>
    <h2 class="sec-title" style="text-align:left">Alpha Trophies in Adelaide</h2>
    <p style="font-size:15px;color:var(--text-muted);margin-bottom:14px"><strong>Prospect showroom:</strong> %(addr)s. Free pickup, with plenty of on-site parking.</p>
    <p style="font-size:15px;color:var(--text-muted);margin-bottom:14px"><strong>Hours:</strong> Mon–Fri 9am–5pm<br><strong>Phone:</strong> %(phone)s<br><strong>Email:</strong> sales@alphatrophies.com.au</p>
    <p><a class="btn-primary" href="adelaide/#how-to-find-us" style="font-size:15px;padding:12px 22px"><i class="fa-solid fa-route"></i> See how to find us</a></p>
  </div>
  <div class="interactive-map-panel"><div class="map-embed-wrapper"><iframe title="Alpha Trophies Prospect map" src="%(embed)s" loading="lazy"></iframe></div></div>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  <div class="sec-header"><h2 class="sec-title">South Australia trophy questions</h2></div>
  <div class="faq-container">
%(faq)s
  </div>
</div></section>

<div style="background:#fff;padding:22px 0;border-top:1px solid var(--border);font-size:14.5px"><div class="wrap">
  Browse: <a href="adelaide/" %(link)s>Adelaide</a> &nbsp;|&nbsp; <a href="../victoria/" %(link)s>Victoria</a> &nbsp;|&nbsp; <a href="../new-south-wales/" %(link)s>New South Wales</a>
</div></div>

''' % {'crumbs': B.crumbs([('Trophies', SITE + '/products/trophies'), ('South Australia', None)]), 'guar': V.HERO_GUARANTEES,
       'himg': hero_prod['img'], 'halt': escape(hero_prod['name']), 'cities': cities, 'featured': featured, 'delivery': delivery,
       'suburbs': suburbs, 'addr': escape(STORE_ADDR), 'phone': PHONE, 'embed': EMBED, 'faq': B.faq_html(faqs), 'link': LINK}
    graph = [
        B.breadcrumb_schema([('Home', SITE + '/'), ('Trophies', SITE + '/products/trophies'), ('South Australia', canon)]),
        {'@type': 'CollectionPage', 'name': 'Custom Trophies South Australia', 'url': canon,
         'about': {'@type': 'AdministrativeArea', 'name': 'South Australia'}},
        {'@type': 'ItemList', 'name': 'South Australian cities and towns', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'url': canon + sl + '/'}
            for i, (n, sl) in enumerate([('Adelaide', 'adelaide')] + [(t['short'], t['slug']) for t in TOWNS])]},
        store_schema(), B.faq_schema(faqs),
    ]
    return V.page(depth, title, desc, canon, body, graph, '<script src="../../assets/js/directory.js" defer></script>')


def main():
    B.write('trophies/south-australia/index.html', state_page())
    B.write('trophies/south-australia/adelaide/index.html', adelaide_page())
    for s in SUBS:
        B.write('trophies/south-australia/adelaide/%s/index.html' % s['slug'], suburb_page(s))
    for t in TOWNS:
        B.write('trophies/south-australia/%s/index.html' % t['slug'], town_page(t))
    urls = ['/trophies/south-australia/', '/trophies/south-australia/adelaide/']
    urls += ['/trophies/south-australia/adelaide/%s/' % s['slug'] for s in SUBS]
    urls += ['/trophies/south-australia/%s/' % t['slug'] for t in TOWNS]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += ['  <url><loc>%s%s</loc></url>' % (SITE, u) for u in urls]
    xml.append('</urlset>')
    os.makedirs(os.path.join(ROOT, 'sitemaps'), exist_ok=True)
    with open(os.path.join(ROOT, 'sitemaps', 'sitemap-sa.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(xml) + '\n')
    print('%d URLs in sitemaps/sitemap-sa.xml' % len(urls))


if __name__ == '__main__':
    main()
