---
name: pdf-manual-to-html
description: >
  Convert a guitar-pedal (or similar hardware) PDF manual into a clean, responsive
  HTML page that keeps the source's visual identity — its fonts, colours, headings
  and figure layout — rather than a pixel-frozen PDF dump. Make sure to use this
  skill whenever the user drops one or more manual PDFs into this repo, mentions a
  pedal's manual or spec sheet, or wants a pedal added to the catalog or site — even
  without the words "PDF" or "HTML". Also covers "convert this manual", "make an
  HTML version of this PDF", folding in a newer PDF revision, restyling or
  re-deriving an existing pedal page from its PDFs, and pulling better
  colours/fonts straight from a manual. Each pedal has its own look, so the skill
  derives the style per manual instead of reusing a template.
---

# PDF manual → styled HTML

## What "preserve the style" means here

Not a pixel reproduction: fold-out panels, bleed and absolute positioning don't
belong on a web page. The brand lives in the **design language** — display and
body typefaces, header/accent colours, the section-title treatment (reversed-out
block, underline, all-caps) and the figure-plus-caption rhythm. Rebuild the
document as semantic, responsive HTML wearing that language. A reader who knows
the pedal should recognise the manual instantly; a screen-reader user should get
a clean document outline.

`wampler-terraform/` is the reference implementation, and
`references/conventions.md` distils it: HTML skeleton, CSS pattern, multi-PDF
recipe, font table. Read `conventions.md` and `wampler-terraform/style.css`
before building. The page's `index.html` is ~85 KB — grep it for a specific
pattern instead of reading it whole; conventions already carries its structure.

## Workflow

### 1. Frame the job

- Identify **brand** and **model** from the PDF (title, cover, footer).
- One PDF → one page. Several PDFs for one pedal → give each a role by reading
  it, not by date or file name: **full manual** (every control), **quick
  start** (small foldout card: hook-up and a few settings), **addendum /
  errata**, **older revision**. The full manual is the base page and the rest
  fold in (conventions → "Multiple PDFs"); a newer quick start doesn't outrank
  an older full manual.
- No PDF at all → compile the page from the maker's site and say so in a
  `.doc-update` banner (conventions → "Multiple PDFs", step 4).
- Target directory: `<brand>-<model>[-<variant>]/`, kebab-case, always in that
  order whatever the maker's wording. `model` is the core name without the
  effect-type word (`compressor`, `overdrive`, `delay`, `pedal`); `variant` is
  the qualifier (`mini`, `deluxe`, `v2`), omitted when there is none. Don't
  abbreviate or invent words: "Mini Ego Compressor" → `wampler-ego-mini/`.

### 2. Extract

Run once per PDF (poppler only, nothing to install):

```
.claude/skills/pdf-manual-to-html/scripts/extract_pdf.sh <manual.pdf> _cctmp.extract/<pdf-stem>/
```

It writes `info.txt` (metadata + **embedded fonts**, which drive the font
choice), `text.txt` (copy source), `raw/` (embedded images in their native
format) and `pages/` (150 dpi renders). `text.txt` loses layout and colour, so
also open the PDF with the Read tool (`pages:`) to see the real thing.

A near-empty `text.txt` and no fonts in `info.txt` mean the type was converted
to outlines at export — the file is fine, the words are curves. Read the copy
off the `pages/` renders and judge the fonts by eye.

An empty `raw/` means the art is vector and every figure gets cropped from
renders. Crop from a 300 dpi render of that page (`pdftoppm -png -r 300 -f N
-l N <pdf> <prefix>`) — the 150 dpi `pages/` give figures too small for a
high-density screen.

Printed page numbers rarely match the PDF page index (covers and TOCs shift
them). Confirm the index (`pdftotext -f N -l N`) before cropping or quoting by
page, or you'll pull from the neighbouring section.

### 3. Decide the style

Two sources, in order of preference:

1. **The brand's own online manual.** Many makers (Wampler included) publish
   one in HTML — search for it. If it exists, its CSS *is* the answer: font
   stack, colours, heading treatment, often the section structure too. This is
   how `wampler-terraform` was built.
2. **The PDF.** Map each embedded font to the nearest Google Font with the
   table in conventions (e.g. `MyriadPro` → "Source Sans 3"). For the palette,
   run `scripts/sample_colors.py <product photo> <cover render>` — the
   enclosure colour is the accent, the cover's ground is the dark band. Product
   photos usually come out of `raw/` as `.jpg`, so don't glob `*.png` only.

Put the result in a handful of CSS custom properties at the top of `style.css`
so the palette is swappable, with the font mapping recorded in a comment.

The page ground is light on every pedal in this repo, whatever the manual is
printed on. A manual set light-on-dark keeps its dark ground for the masthead
band and reversed-out headings, not for `body` — a whole dark page reads as a
print file and breaks with the rest of the site. Figures follow suit: line art
printed light-on-dark is recoloured onto the page ground (ground → white, light
strokes → dark), keeping brand colours such as red callouts and the white
numerals inside them. Check the result by eye; a blanket invert turns red
cyan and those numerals black.

Match the *weight* of the treatment, not just the values. If the manual sets
titles as bold text over a hairline rule, don't reverse them into solid blocks
because the reference page does. Keep the accent for rules, links and table
headers: an accent-coloured heading is the manual's look, an accent-coloured
table of contents is just loud.

### 4. Build the page

The reference supplies the *chrome* — nav, breakpoint, figure grid, table
styling. The *outline* comes from the PDF being converted: its sections, its
order, its headings. Don't reshape a manual into Terraform's section list, and
don't invent sections it doesn't have.

Manuals often have no explicit headings — the Mini Ego's is running prose plus
a block of knob descriptions. Then cut sections at the document's own seams
(what a compressor is → controls → suggested settings → specs / warranty) and
name each after the manual's wording. The test: someone holding the PDF can
follow the page section by section without losing their place.

**Structure** (full skeleton and CSS in conventions):

- **Masthead: wordmark.** The cover photo in the PDF usually carries no
  lettering — the wordmark is separate vector art. Crop it from the page render
  and set it as `<h1><img alt="<Brand> <Model>"></h1>` over the cover's ground
  colour; without it the page opens on an unlabelled photo and the model name
  lives only in `<title>`. `wampler-terraform/` predates this and opens on a
  bare `<img>` — follow the skeleton, not that page.
- **Masthead: photo.** A real photo of the pedal, cropped from a page render
  when one has it. Some manuals (CAB X2's) show the enclosure only as line art;
  then use the manufacturer's own product photo from their site or listing
  rather than promoting the diagram to hero image. A maker's promo shot of its
  own product needs no credit; a third-party seller's photo does.
- `<nav id="side-nav">` fixed TOC on desktop, `#toc-mobile` in the flow for
  narrow screens, one `@media (max-width: 900px)` breakpoint that hides the nav.
- `<main>` with one `<section id="…">` per manual section; `id`s are kebab-case
  and match the TOC anchors exactly.
- Semantic headings (`h2` section, `h3` sub-section …) — style them, don't pick
  tags by size.
- Reference tables (MIDI maps, spec sheets) → `.doc-table` inside
  `.table-scroll`.
- Print layout yields to HTML semantics. Never break an `<ol>`/`<ul>` to drop an
  image in — group the images above or below the list. If a
  `column-span: all` figure makes text in a multi-column `.half-container` flow
  oddly or pushes list items into the wrong column, give that section
  `.no-columns`.

**Copy.** Faithful to the manual — same wording, same order — with the typos
fixed. Print manuals ship with them ("Smmoths everything out", "an experience
radio/TV technician", "the option or repairing"), and reproduced verbatim they
look like the page's mistake. Correct spelling, grammar and mangled phrases;
leave the author's voice, slang and deliberate informality alone. Where one PDF
garbles a sentence another prints cleanly, take the clean one. No `[sic]` — it
helps nobody in a pedal manual.

**Figures.**

- Prefer embedded images from `raw/`; crop from the `pages/` renders when they
  are sliced, vector or absent. A row of knob shots goes in a `.grid-wrapper`,
  `<img>` at `width: 100%`.
- `pdfimages` also dumps alpha masks and technical layers as separate grayscale
  images. Look at each image you pick (or `file` it for 3-channel RGB) so you
  ship the colour figure, not its mask.
- Crop by eye, never from text coordinates alone, and look at the edges of the
  result: a stroke or leader line running off the edge means the crop cut the
  drawing. Widen it until every pointer ends at the thing it points to.
- A figure holds graphics only. Body text printed inside an image goes into the
  HTML and is painted out of the image with the background colour; integral
  labels (numbered pointers) stay. A wordmark crop is the logotype alone — a
  tagline or URL printed beside it is text, so it goes in the HTML.
- Copy across only the images the page shows, named for what they depict
  (`setting-1.png`, `ego-mini-header.jpg`). Most of the dump is print
  furniture — gradient strips a few pixels tall, slivers of rules, repeated
  logos; their dimensions give them away. `Images/` is kept forever, so it
  holds figures, not leftovers.
- Photos are `.jpg` (`.png` when they need transparency); line art, wordmarks
  and screenshots are `.png`.

### 5. Place the assets

```
<brand>-<model>/
  index.html
  style.css
  Images/            figures used by the page
  <original>.pdf     keep every source PDF alongside
  index-<year>.html  older revision, when folding in a newer one
```

PDFs dropped in the repo root move into the pedal's directory (`git mv` if
already tracked).

### 6. Add the catalog card

Append a `<li>` to the root `index.html` pedal grid by copying a card already
there (`brand` / `model` / `note`). Read the file rather than trusting this
one — the catalog is hand-tuned and drifts. `note` is a short descriptor of
what the pedal is, e.g. `Compressor`.

### 7. Verify before declaring done

- `scripts/check_page.py <pedal-dir>/index.html` — dangling TOC anchors,
  missing images and unreferenced files in `Images/`; none of them shows in a
  screenshot.
- Screenshot the whole page with headless Chrome at a desktop and a mobile
  width, raising the height until the footer is in frame:

  ```
  mkdir -p _cctmp.shot
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
    --hide-scrollbars --window-size=1400,4000 \
    --screenshot="$PWD/_cctmp.shot/desktop.png" "file://$PWD/<pedal-dir>/index.html"
  ```

  Repeat with `--window-size=800,4000` → `mobile.png`. Compare desktop against
  the PDF `pages/`: every section present, figures in the right place, nothing
  garbled. On mobile: nav gone, mobile TOC shown, no horizontal scroll.
- The palette works on both light surroundings and the reversed-out header.
- Delete `_cctmp.extract/` and `_cctmp.shot/` so they never get committed.

### 8. Deploy

Don't commit or push unless the user asks. The repo auto-deploys via GitHub
Actions on push to `master`; source PDFs live in the repo on purpose.

## Bundled files

- `scripts/extract_pdf.sh` — text, images, page renders and font list from a PDF.
- `scripts/sample_colors.py` — dominant colours of an image, as hex.
- `scripts/check_page.py` — anchor, image and stray-file check on the built page.
- `references/conventions.md` — repo layout, the full HTML/CSS pattern from the
  reference implementation, the multi-PDF merge recipe, font-mapping table.
