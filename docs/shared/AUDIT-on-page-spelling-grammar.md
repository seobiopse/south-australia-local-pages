# On-page, spelling & grammar audit: local pages

Pages: `/trophies/victoria/` (State) and `/trophies/victoria/melbourne/` (City). Audited 8 Oct 2026 from source HTML. No live crawl.

Severity: **High** = fix before go-live. **Med** = should fix. **Low** = polish.

## 1. On-page SEO

| # | Sev | Page | Issue | Fix |
|---|---|---|---|---|
| 1 | High | Both | Title tags 77 / 78 chars. Google truncates around 60. The location keyword survives but "Alpha Trophies" is cut. | State: `Custom Trophies Victoria \| Free Engraving \| Alpha Trophies` (60). City: `Custom Trophies Melbourne \| Free Engraving \| Alpha Trophies` (61, or drop "Custom"). Keep Thomastown in the meta description. |
| 2 | High | Both | `og:title` copies the long title. | Match the new title. |
| 3 | High | Both | Schema `@id` `.../stores/thomastown#store` is used on both pages with a different `url` each. Same entity, conflicting URLs. Also confirm that `/stores/thomastown` resolves. | Drop `url` from the Store node, or point it at one canonical page. Use the same `@id` only if the page really is that entity. |
| 4 | High | Both | `"telephone": "+61 1300 485 645"` is invalid. 1300 numbers have no +61 form. | Use `"1300 485 645"`. |
| 5 | Med | Both | Rating "4.9 / 232 reviews" shows in the top bar and the hero, but there is no `aggregateRating` markup. Number also unconfirmed (README item 1). | Confirm the count, then add `aggregateRating` to the Store node. |
| 6 | Med | Both | Heading skips. State: "Pick up or have it shipped" and "Made for Victorian presentation nights" are `h3` with no `h2` parent. City: "Trusted by Victorian and national organisations" is `h3` after an `h2` section. | Promote to `h2`. |
| 7 | Med | Both | Hero is `<header class="hero">`, a second banner landmark. | Change to `<section>`. |
| 8 | Med | City | Eight "View" buttons share the same anchor text. | `View <product name>` or add `aria-label`. |
| 9 | Med | City | Few contextual internal links. Medals, trophy cups, school awards and corporate awards are linked only from nav and footer. | Link "medals", "school awards", "plaques" inside body copy (hero lead or fulfilment intro) to their category pages. |
| 10 | Med | State | Hub has one live city and three plain-text "Coming soon" cards. Thin as a hub. | Fine for the draft, but add 80–120 words of unique Victoria content (events, leagues, regions) before launch. Do not link Geelong, Ballarat or Bendigo until they exist. |
| 11 | Med | Both | Duplicated blocks: "Is engraving free?" FAQ answer is word for word identical. Fast Track / Priority Rush pricing and the six client names are also repeated. Hero guarantee trio is identical. | Reword the FAQ per page, for example the city version: "Yes. Every trophy, medal and plaque ordered for Melbourne pickup or delivery is engraved free." Keep client list on the City page only, or vary the order. |
| 12 | Med | City | Hero image is the same file and alt text as product card 1. | Use a different hero image or a distinct alt: "Gold footy trophy on marble base, engraved free at our Thomastown showroom". |
| 13 | Med | Both | `og:image` is the site logo. No `twitter:card`, `og:site_name` or `og:locale`. | Use a trophy photo (1200×630) and add `twitter:card=summary_large_image`, `og:site_name`, `og:locale=en_AU`. |
| 14 | Low | Both | FAQPage markup is valid but Google now shows FAQ rich results for only a few site types. It is harmless. | Keep for AI/answer engines. |
| 15 | Low | City | Suburb chips (12) are plain text. | Link when suburb pages exist. |
| 16 | Low | Both | Draft banner and no `noindex`. | Remove banner at go-live (README). If the pages are hosted on staging beforehand, add `noindex`. |
| 17 | Low | Both | Image filename typo `glass-budget-plaque-clear-fornt-with-text-6155.jpg`. | Rename to `front`. Not user-visible. |
| 18 | Low | State | 4 FAQ answers are short (some under 20 words). | Add one more sentence each, for example in "Is engraving free?" say what can be engraved. |

Lengths: meta descriptions 160 (State) and 155 (City). Both OK, State is at the limit. H1 count 1 per page. Canonical present and correct. `lang="en-AU"` set.

## 2. Local accuracy risks (copy that could be wrong)

These are not spelling, but they sit in the copy and are verifiable claims. README item 4 already flags directions. Specific doubts:

| Sev | Where | Claim | Concern |
|---|---|---|---|
| High | City, public transport | "Route 902 buses run through the area." | Route 902 is a SmartBus on the Chelsea to Airport West corridor, not obviously Thomastown / Settlement Road. Check PTV. |
| High | City, public transport | "roughly 35 minutes plus a short walk" | Nearest train station is Thomastown, about 3 km from Brock St. Not a short walk. Rewrite or remove. |
| High | City, from the CBD | "About 32 km, 35 minutes" | Thomastown is roughly 18–20 km from the CBD. 32 km looks like a long route. Recheck in Google Maps. |
| Med | City, from the north | Steps say "continue towards Dalton Road and Settlement Road" | Too vague to follow. Name the Hume Fwy to M80 exit and the Dalton Rd turn. |
| Med | City, from the west | "Western Ring Road (M80 Metropolitan Ring Road)" | Redundant naming. Say "M80 Ring Road heading east". |
| Med | City, intro | "Harvey Norman Thomastown or JB Hi-Fi Home ... a minute away" | Unverified landmarks and distance. |
| Med | City, hero | "Engraved in-house" | Confirm. |
| Med | Both | "Australia's most trusted trophy supplier" (footer) | Unsubstantiated superlative. Soften: "A trusted Australian trophy supplier since 1985". |
| Med | City, order card | Label "Priority Rush pickup: Day 3 ($15 + 20%)" | Mixed up. Priority Rush is $50 + 15% (3 days). $15 + 20% is the "Rush pickup" fee in the FAQ. Make card and FAQ say the same thing. |
| Low | State | "make up most of our Victorian orders" | Unprovable claim. Use "are among our most common orders". |

## 3. Spelling

AU English is used consistently (organisations, fulfilment, programs, colour not present). No misspellings found in visible text.

| Sev | Where | Note |
|---|---|---|
| Low | Both | Proper nouns check out: Thomastown, Craigieburn, Reservoir, Keysborough, Narre Warren, Cranbourne, Glen Waverley, Southbank. |
| Low | Both | Image filename typo "fornt" (see #17). |

## 4. Grammar, punctuation and consistency

| # | Sev | Where | Current | Suggested |
|---|---|---|---|---|
| 1 | Med | Both (body, FAQ, order card, schema) | "after 5 working days production" | "after 5 working days of production" or "after a 5-working-day production time" |
| 2 | Med | State FAQ + schema | "Standard shipping is a $9.90 flat rate after 5 working days production." Reads as if the rate starts after 5 days. | "Standard shipping is a $9.90 flat rate. Orders are produced in 5 working days, then shipped." |
| 3 | Low | State hero | "Collect free from our Thomastown showroom" | "Collect for free from..." |
| 4 | Low | State body | "Footy, netball, cricket and soccer clubs, school presentation nights and workplace recognition programs make up most of our Victorian orders." Mixes groups and events. | "Footy, netball, cricket and soccer clubs, school presentation nights and workplace recognition programs are our most common Victorian orders." |
| 5 | Low | City directions | "We're at 11/8–20." Elsewhere "We are on Brock Street". Mixed contraction use. Also reads as the address fragment. | "Our showroom is at 11/8–20 Brock Street." (Pick contractions or not, then use one style.) |
| 6 | Low | Both | "Mon–Fri 9am–5pm" (top bar) vs "Mon–Fri 9:00am–5:00pm" (store block) vs "Monday to Friday 9am to 5pm" (body). | Use "Mon–Fri 9am–5pm" everywhere short, "Monday to Friday, 9am to 5pm" in prose. |
| 7 | Low | Both | "4.9 ★ Google Rating" (top bar) vs "4.9 ★ Google rating" (hero). The top bar also has a star icon plus ★, so two stars show. | One casing: "Google rating". Remove the ★ character or the icon. |
| 8 | Low | City | "Hume Freeway (National Highway M31)" | "Hume Freeway (M31)". |
| 9 | Low | State | "Victorian" appears 12+ times in about 600 words, in H2s, tile copy and body. | Vary: "state", "local clubs", region names. |
| 10 | Low | City | Cards say "Real products from our range" | Fine, or "Popular products from our range". |
| 11 | Low | Both | Hyphen use is correct (en dashes in ranges and addresses, "flat-rate shipping" as adjective, "flat rate" as noun). | No change. |

## 5. Priority order

1. Shorten titles and og:title (#1, #2).
2. Fix schema: telephone, `@id`/`url` conflict (#3, #4).
3. Verify or cut the doubtful transport and distance claims (Section 2, High).
4. Fix the Priority Rush / Rush pickup label mismatch.
5. Grammar items 1 and 2.
6. Heading levels, duplicate FAQ, link anchor text, og:image.

I can apply the safe fixes (titles, telephone, heading levels, grammar items 1–8, link labels) directly to both files. Section 2 claims need Tom's confirmation first.
