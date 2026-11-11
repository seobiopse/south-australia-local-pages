# Alpha Trophies: South Australia local pages

28 static pages for alphatrophies.com.au, one combined trophies, medals and awards page per location. Store: Prospect, 56 Prospect Road SA 5082.

| Tier | URL pattern | Pages |
|---|---|---|
| State hub | `/trophies/south-australia/` | 1 |
| Adelaide hub | `/trophies/south-australia/adelaide/` | 1 |
| Adelaide suburbs | `/trophies/south-australia/adelaide/<suburb>/` | 19 |
| SA towns | `/trophies/south-australia/<town>/` | 7 |

NSW (57 pages) is live and Victoria (41 pages) has its own repo.

## Layout

```
trophies/south-australia/   the pages (folders match the live URLs)
assets/                     css, js, logo (product images load from the live site)
scripts/                    build_sa.py (generator) + build_vic.py, build_nsw.py helpers it imports, build_nav.py, check_unique.py, scrape_vic_products.py
data/sa/                    sa_locations.json (drive data, copy), vic_used_slugs.json (products used on Victoria pages, so SA sets differ)
data/victoria/              vic_products.json (live products, shared), vic_locations.json and draft-backup/ (import and chrome source for the builders)
data/shared/, data/nsw/     menu.json, sports.json, nsw_locations.json (import dependencies only)
docs/south-australia/       SA-UNIQUENESS.md
sitemaps/                   sitemap-sa.xml
```

## Rebuild

```bash
python scripts/scrape_vic_products.py   # optional: refresh live products and prices
python scripts/build_sa.py              # writes the 28 pages and the sitemap
python scripts/build_nav.py             # Trophies/Medals menu
python scripts/check_unique.py          # uniqueness report
python -m http.server 8766              # preview at /trophies/south-australia/
```

## Facts used
- Drive data: Google Maps, fastest route from the Prospect showroom, 11 Nov 2026 about 5pm (afternoon traffic).
- Store coordinates (-34.8922624, 138.5942398) come from the Google Maps listing; the live Adelaide page schema is about 1.1 km off.
- Delivery: standard $9.90 flat, express $25 flat, Fast Track 4 days ($40 + 10%, cap $300), Priority Rush 3 days ($50 + 15%, cap $300), pickup at Prospect (standard 5 working days, Priority Rush pickup from day 3). No same-day pickup.
- Suburb populations: approximate figures from Tom's spreadsheet; towns: ABS June 2025.

## Confirm with Tom before publishing
1. Local clubs and schools (none supplied for SA).
2. Phone: Google listing shows +61 8 7070 1111; pages use 1300 485 645.
3. Hours: Google shows 8am opening; pages use Mon-Fri 9am-5pm.
4. General-knowledge local facts, council areas and sport mix in `data/sa/sa_locations.json`.
5. Re-run the scraper before go-live; 301 `/buy-trophies-in-adelaide` to `/trophies/south-australia/adelaide/`; submit `sitemaps/sitemap-sa.xml`; request indexing.
6. Remove the live Adelaide page's "same-day pickup" strip.

## Deployment note
This repo contains build scripts, data and docs as well as the pages. Do not deploy the whole repository as a public site. If a Pages workflow is added, publish only `trophies/` and `assets/`.
