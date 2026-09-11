---
name: pdf-manual-to-html
description: >
  Convert a guitar-pedal (or similar hardware) PDF manual into a clean, responsive
  HTML page that keeps the source's visual identity — its fonts, colours, headings
  and figure layout — rather than a pixel-frozen PDF dump. Use this whenever the
  user drops one or more manual PDFs into this repo and wants them rendered
  as HTML, says "convert this manual", "make an HTML version of this PDF", "add
  this pedal to the catalog", or brings a newer PDF revision to fold into an
  existing page. Also use when asked to restyle or re-derive an existing pedal
  page from its PDFs. Each pedal has its own look, so the skill derives the style
  per manual instead of reusing a template.
---

# PDF manual → styled HTML

## What "preserve the style" means here

Not a pixel reproduction. Print PDFs use fold-out panels, bleed, absolute
positioning — none of that belongs on a web page. What carries the brand is the
**design language**: the display typeface, the body typeface, the header/accent
colours, how section titles are set (reversed-out block, underline, all-caps),
and the figure-plus-caption rhythm. Rebuild the document as semantic, responsive
HTML wearing that design language. A reader who knows the pedal should recognise
the manual instantly; a screen-reader user should get a clean document outline.

The existing `wampler-terraform/` page is the reference implementation — read it
and its `style.css` before building a new one.

## Workflow

### 1. Frame the job

- Identify **brand** and **model** from the PDF (title, cover, footer).
- One PDF → one page. Several PDFs for the same pedal → give each a role by
  reading it, not by its date or file name: **full manual** (covers every
  control), **quick start** (a card: hook-up and a few settings), **addendum /
  errata**, **older revision** of the full manual. The full manual is the base
  page and the rest fold in (`references/conventions.md` → "Multiple PDFs");
  a newer quick start does not outrank an older full manual. Page size gives it
  away fast — a quick start is a small foldout card, a manual is full-size.
- Target directory: `<brand>-<model>[-<variant>]/` in kebab-case, always in
  that order regardless of how the maker words it. `model` is the core name
  without the effect-type word (`compressor`, `overdrive`, `delay`, `pedal`);
  `variant` is the qualifier (`mini`, `deluxe`, `v2`), omitted when there is
  none. Never abbreviate or invent words. "Mini Ego Compressor" →
  `wampler-ego-mini/`; "Terraform" → `wampler-terraform/`.

### 2. Extract

Run the bundled script once per PDF (poppler only, nothing to install):

```
.claude/skills/pdf-manual-to-html/scripts/extract_pdf.sh <manual.pdf> _cctmp.extract/<pdf-stem>/
```

`_cctmp.extract/` is scratch space in the repo root — delete it once the page is
built so it never gets committed. It writes `info.txt` (metadata + **embedded fonts** — these drive the font
choice), `text.txt` (copy source), `raw/` (embedded images) and `pages/`
(150dpi page renders). Also open the PDF with the Read tool (`pages:`) to see the
real layout and colours — `text.txt` loses all of that.

Print PDFs are often exported with the type converted to outlines, so `text.txt`
comes back near-empty (only the layout tool's slug line) and `info.txt` lists no
fonts. Nothing is wrong with the file — the words are curves now. Read the copy
off the `pages/` renders instead, and take the fonts from the renders by eye.

### 3. Decide the style

Two sources, in order of preference:

1. **The brand's own online manual.** Many makers (Wampler included) publish an
   HTML manual. Search for it. If it exists, its CSS *is* the answer — capture the
   font stack, colours and heading treatment, and often the section structure
   too. This is how `wampler-terraform` was built.
2. **The PDF itself.** Map each embedded font to the nearest Google Font
   (`Futura-CondensedLight` → "Oswald"/"Archivo Narrow"; `Helvetica` → system
   sans or "Inter"; `MyriadPro` → "Source Sans 3"; a rounded techy face →
   "Chakra Petch"). For the palette, run
   `scripts/sample_colors.py _cctmp.extract/*/raw/*.png _cctmp.extract/*/pages/*.png`
   — the enclosure colour of the pedal photo is the accent, the cover's ground
   is the dark band.

Write these as a handful of CSS custom properties at the top of `style.css` so
the palette is swappable. Record the mapping in a comment.

Match the *weight* of the treatment too, not just the values. If the manual
sets its titles as bold text over a hairline rule, don't reverse them out into
solid blocks because the reference page does. And keep the accent for rules,
links and table headers: an accent-coloured heading is the manual's look, an
accent-coloured table of contents is just loud.

### 4. Build the page

The reference implementation supplies the *chrome* — nav, breakpoint, figure
grid, table styling. The *outline* comes from the PDF being converted: its own
sections, in its own order, under its own headings. Don't reshape a manual into
Terraform's section list, and don't invent sections it doesn't have.

Manuals often carry no explicit headings at all — the compressor's is running
prose plus a block of knob descriptions. Then cut sections at the document's
own seams (what a compressor is → controls → suggested settings → specs /
warranty) and name each one after the manual's own wording. The test: someone
holding the PDF can follow the page section by section without losing their
place.

With that settled, mirror the reference implementation (`references/conventions.md`
has the full checklist and CSS snippets):

- A masthead carrying the pedal's name. The cover photo embedded in the PDF
  usually holds no lettering — the wordmark is separate vector art, so crop it
  out of the page render and set it as `<h1><img alt="<Brand> <Model>"></h1>`
  over the cover's own ground colour. Without it the page opens on an unlabelled
  photo, and the model name lives only in the `<title>`. `wampler-terraform/`
  predates this and starts on a bare `<img>` — follow the skeleton in
  `references/conventions.md`, not that page.
- `<nav id="side-nav">` fixed TOC on desktop, `#toc-mobile` inside the flow for
  narrow screens, one `@media (max-width: 900px)` breakpoint that hides the nav.
- `<main>` with one `<section id="...">` per manual section; `id`s are kebab-case
  and match the TOC anchors exactly.
- Semantic headings only (`h2` section, `h3` sub-section …) — style them, don't
  pick tags by size.
- Figures: `<img>` at `width: 100%` in a `.grid-wrapper` when the manual shows a
  row of knob shots. Prefer embedded images from `raw/`; if they are sliced,
  vector or absent, crop from the `pages/` renders.
- **Image Validation**: PDF extraction tools often extract alpha masks or technical layers as separate grayscale/black-and-white images. When selecting any figure or header image, visually verify (or use `file` to check for 3-channel RGB) that you have chosen the full-color image, not a single-channel artifact.
- **Accurate Extraction**: Never crop images blindly based on text coordinates (OCR boxes) alone. Always visually inspect the rendered page or source image before cropping to guarantee no part of the diagram is cut off.
- **Image Purity**: Extracted images must contain only graphics. Any body text present in the original image must be transcribed into HTML and removed or masked out from the image (e.g. painted over with the background color), except for integral labels (like numbered pointers).
- **Semantic Flow over Print Layout**: Do not blindly copy print layouts if they break HTML semantics. Never interrupt continuous lists (`<ol>` or `<ul>`) with images. Group related images above or below the continuous text block instead.
- **Multi-column Layout Caution**: Be careful when placing wide elements (`column-span: all`) inside multi-column text containers (like `.half-container`). If placing images causes unnatural text flow or forces list items into the wrong columns, apply `.no-columns` to that specific section to restore a linear, readable flow.
- **PDF Page Index vs. Printed Numbers**: The printed page numbers in a manual rarely match the actual physical page index in the PDF file (due to cover pages and TOCs). When cropping images or extracting text by page number, you must verify the actual PDF page index (e.g. using `pdftotext -f N -l N`) so you don't accidentally crop text from adjacent sections.
- Copy across only the images the page actually shows, and rename each one for
  what it depicts (`setting-1.png`, `ego-mini-header.jpg`). `pdfimages` dumps
  everything the file holds, most of it print furniture — gradient strips a few
  pixels tall, slivers of rules, repeated logos; their dimensions in the listing
  give them away. `Images/` is what the repo keeps forever, so it holds figures,
  not extraction leftovers. `scripts/check_page.py` lists any file in `Images/`
  the page never references.
- Reference tables (MIDI maps, spec sheets) → `.doc-table` inside
  `.table-scroll`.
- Keep body copy faithful to the manual — same wording, same order — but fix
  the typos. Print manuals ship with them ("Smmoths everything out", "an
  experience radio/TV technician", "the option or repairing"), and reproducing
  one makes the page look like the mistake is yours. Correct spelling, grammar
  and mangled phrases; leave the author's voice, slang and deliberate informality
  alone. Where one PDF prints a sentence the other garbles, take the clean
  version. Don't mark the corrections — a `[sic]` in a pedal manual helps nobody.

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

Append a `<li>` to the root `index.html` pedal grid, copying the markup of the
card already there (`brand` / `model` / `note`). Read that card first rather
than trusting this file — the catalog is hand-tuned and the wording drifts. The
`note` is a short descriptor of what the pedal is, e.g. `Compressor`.

### 7. Verify before declaring done

- Run `scripts/check_page.py <pedal-dir>/index.html` — dangling TOC anchors and
  missing images both survive a look at a screenshot.
- Render the page (`mkdir -p _cctmp.shot && qlmanage -t -s 1400 -o _cctmp.shot
  <pedal-dir>/index.html` — the output directory has to exist first) and compare
  section by section against the PDF `pages/`: every section present, figures in
  the right place, nothing garbled. `qlmanage` shows only the first screen and
  never loads webfonts, so judge the typography in a real browser.
- Check the 900px breakpoint: nav gone, mobile TOC shown, no horizontal scroll.
- Validate the palette against both light surroundings and the reversed-out
  header.

### 8. Deploy

Don't commit or push unless the user asks. The repo auto-deploys via GitHub
Actions on push to `master`; source PDFs live in the repo on purpose.

## Bundled files

- `scripts/extract_pdf.sh` — text, images, page renders and font list from a PDF.
- `scripts/sample_colors.py` — dominant colours of an image, as hex.
- `scripts/check_page.py` — anchor and image check on the built page.
- `references/conventions.md` — repo layout, the full HTML/CSS pattern from the
  reference implementation, the multi-PDF merge recipe, font-mapping table.
