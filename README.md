[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Kuyukbot1/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Kuyukbot1/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

# Friday 20 November 2026: 42 stories, 6 continents, one front page and a map

An entry for the [make.fun bounty](https://make.fun/bounty/news-image-20261120).

One 1024×1024 image summing up Friday 20 November 2026 — 42 verified stories
across 6 continents, drawn as a newspaper front page:

- **Masthead** — "Friday 20 November 2026" over "42 stories · 6 continents · all from Friday".
- **13 illustrated feature cards** — Trump, Xi and Putin hail a "Declaration
  Towards Peace" after the first trilateral in Shenzhen; Cyclone Akvan makes
  landfall on India's east coast; Russian strikes hit Kyiv and damage two
  embassies; Anthropic closes up 17% after a wild $2tn debut; COP31 closes
  today with a deal still unwritten; a Houthi strike hits a Riyadh tower;
  allies meet in Berlin after the Shenzhen talks; Modi opens the first SCO
  dialogue forum in Delhi; Nicholls' century lifts New Zealand in the
  Wellington Test; the FAA halts US departures after a system failure;
  Tunisia book a World Cup place with a late winner; Bangladesh's lockdown
  turns violent and Yunus's home is torched; Hagia Sophia's hidden tunnels
  explored at last.
- **"Where it happened"** — a world map with numbered pins matching the cards.
- **"Also on Friday 20 November"** — 29 further stories, country-first.
- **Footer** — every story happened or was first reported on Friday
  20 November 2026; disputed claims are attributed. Sources: AP, Reuters,
  AFP, BBC, Al Jazeera, UN News. Original drawings.

## How it is built

`draw.py` (Python 3 + Pillow, DejaVu Serif/Sans) draws `entry.png` from the
verified stories in `../RESEARCH_20NOV.md`; re-running it reproduces the
image byte-identically. `main.ts` (Node 22, standard library only) copies
`entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.

## Verification

- `entry.png` — 1024×1024, 203,915 bytes (≤1 MiB), sha256
  `3bc92f512f6c2cd3f441cd76852d9ca2ebfbd8c3020dd9866f65cf4879dfecaf`
- `draw.py` re-run reproduces the identical sha256.
- `main.ts` run twice writes byte-identical output (same sha256).
- Viewed at full size and at 300 px: all text legible and unclipped, no
  overlaps, masthead date is the biggest element.
