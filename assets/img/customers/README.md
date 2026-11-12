# Customer logos

One file per customer, shared by every page where that customer appears.

- **File name:** the customer slug, for example `hoppers-elite-cricket-club.png`, `bank-of-melbourne.png`, `george-and-matilda-eyecare.png`.
  The full list of names, slugs, the pages each one appears on and which logos are still missing is in `data/customers/logos-manifest.csv`.
- **Format:** PNG, 512 x 512 px, square, transparent background, logo centred with 32 px padding (SVG is also accepted as `<slug>.svg`).
- **Display:** the card tile is a fixed 64 x 64 px square on every page (white tile, 7 px padding, `object-fit: contain`), so the 512 px file stays sharp on high-density screens. Do not change the tile size per customer.
- **Missing logo:** the card shows the customer's initials in the same 64 px square until the file exists.
- **Adding logos:** put the originals in `data/customers/logos-raw/` (named after the customer), run `python scripts/prepare_logos.py` (it trims margins and writes the square PNGs here), then rebuild the pages.
- **Use:** only use logos Alpha has permission to show; record the source and permission in the manifest columns.
