# Fortin Fuzz))) — copy changes

## Source

- `FORTIN_fuzz_2023_manual.pdf` (2 pages, PDF24, created 2023-02-24), handed over
  by the user. Byte-identical (`cmp`) to both official copies checked on
  2026-09-23:
  - product page https://fortinamps.com/products/fortin-fuzz →
    `//fortinamps.com/cdn/shop/files/FORTIN_fuzz_2023_manual.pdf?v=12006766557990360768`
  - manuals index https://fortinamps.com/pages/product-manuals →
    `https://cdn.shopify.com/s/files/1/0607/5115/1331/files/FORTIN_fuzz_2023_manual.pdf`
- No other documents (quick start, addendum) are offered for this model.

## Departures from the print

| Section | Printed | Page |
|---|---|---|
| intro | "previous-ly unchartered sonic realms" | "previously uncharted sonic realms" (malapropism) |
| intro, getting-started | line-end hyphenation "pack-age", "recom-mend", "relia-bility" | joined: "package", "recommend", "reliability" |
| getting-started | "this is the kind on control" | "this is the kind of control" |
| getting-started | "This pedal sounds MONSTOROUS on bass!" | "MONSTROUS" |
| controls / bypass | "True Bypass footwitch." | "footswitch" |
| controls / girth | "get that bass turned up, pregain, to allow you" | "pre-gain" (spelling on the maker's product page) |
| controls / power | "external adapter/power supplyor battery" | "supply or battery" |
| controls | run-in labels "BYPASS -", "LEVEL -" … | same, the caps and the dash come from CSS (`text-transform`, `::after`) |
| intro, getting-started, controls | no headings in the print | headings "The Fuzz)))", "Getting the Best out of Your Pedal" (from "to get the absolute best out of your new pedal"), "Controls" added at the document's seams |
| warranty | small bold caps label "WARRANTY" | h2 "Warranty" in the page's section band |
| setting-suggestions | knob positions shown only in the pedal thumbnails | read off the thumbnails into each image's `alt` as approximate clock positions |

## Conflicts left as printed

- Battery: controls / POWER says "external adapter/power supply or battery (not
  included)"; the same page says "you can only power the fuzz))) via the DC
  inlet", and the maker's product page says "external adapter/power supply only".
- Knob names: the manual's controls list says LEVEL and GAIN; the enclosure
  (cover photo and thumbnails) labels them "vol" and "fuzz". Girth matches.
