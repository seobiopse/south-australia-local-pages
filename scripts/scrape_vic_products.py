"""Pull live product data (name, price, url, image) from the category pages on alphatrophies.com.au.

Run: python scrape_vic_products.py   -> writes data/vic_products.json
Source: the ItemList JSON-LD on each category page. Products flagged OUT OF STOCK in the page HTML are skipped.
Re-run before publishing so prices and stock are current.
"""
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://alphatrophies.com.au/'
CATS = {
    'afl': 'products/trophies/a/aussie-rules-afl',
    'netball': 'products/trophies/n/netball',
    'soccer': 'products/trophies/s/soccer',
    'cricket': 'products/trophies/c/cricket',
    'basketball': 'products/trophies/b/basketball',
    'tennis': 'products/trophies/t/tennis',
    'lawnbowls': 'products/trophies/l/lawn-bowls',
    'golf': 'products/trophies/g/golf',
    'hockey': 'products/trophies/h/hockey',
    'athletics': 'products/trophies/a/athletics',
    'swimming': 'products/trophies/s/swimming',
    'equestrian': 'products/trophies/e/equestrian',
    'fishing': 'products/trophies/f/fishing',
    'rowing': 'products/trophies/r/rowing',
    'cycling': 'products/trophies/c/cycling',
    'dance': 'products/trophies/d/dance',
    'motorsports': 'products/trophies/m/motorsports',
    'sailing': 'products/trophies/s/sailing',
    'schoolmedals': 'products/medals/aa/academic-medals',
    'aflmedals': 'products/medals/aa/aussie-rules-afl-medals',
    'netballmedals': 'products/medals/nn/netball-medals',
    'soccermedals': 'products/medals/ss/soccer-medals',
    'cricketmedals': 'products/medals/cc/cricket-medals',
    'basketballmedals': 'products/medals/bb/basketball-medals',
    'plaques': 'products/corporate-awards/plaques',
}
KEEP = 60


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'replace')


def out_of_stock(html):
    """Slugs whose card text (up to the next product link) contains OUT OF STOCK."""
    oos = set()
    parts = re.split(r'(?=<a [^>]*href="https://alphatrophies\.com\.au/product/)', html)
    for p in parts[1:]:
        m = re.match(r'<a [^>]*href="https://alphatrophies\.com\.au/product/([^"]+)"', p)
        if m and 'OUT OF STOCK' in p[:1500].upper():
            oos.add(m.group(1))
    return oos


def main():
    out = {}
    for key, path in CATS.items():
        html = get(BASE + path)
        title = re.search(r'<title>(.*?)</title>', html, re.S).group(1).strip()
        items = []
        for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            try:
                d = json.loads(blk)
            except ValueError:
                continue
            for node in (d if isinstance(d, list) else [d]):
                if node.get('@type') == 'ItemList':
                    for li in node.get('itemListElement', []):
                        it = li.get('item', {})
                        if it.get('@type') == 'Product':
                            items.append({'name': it['name'], 'slug': it['url'].split('/product/')[1],
                                          'price': it['offers']['price'], 'img': it['image']})
        oos = out_of_stock(html)
        live = [i for i in items if i['slug'] not in oos]
        out[key] = {'path': path, 'title': title, 'total': len(items), 'oos': len(items) - len(live), 'items': live[:KEEP]}
        print('%-16s %-45s total %3d  out-of-stock %2d  kept %d' % (key, title[:45], len(items), len(items) - len(live), len(out[key]['items'])))
    with open(os.path.join(ROOT, 'data', 'victoria', 'vic_products.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
