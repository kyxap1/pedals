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
recipe, font table. Read `conventions.md` and one `style.css` before
building: a same-brand sibling's when one exists (step 3), else Wampler's.
Don't read `wampler-terraform/index.html` (~85 KB) whole; grep it for a
pattern, conventions already carries its structure.

## Parallel sessions

Several sessions may convert different manuals in this checkout at once. A job
owns only the paths keyed by its slug — the `<brand>-<model>` directory name
from step 1:

- `<slug>/` — the page, its images and source PDFs;
- `_cctmp.<slug>/` — every scratch file: extracts, 300 dpi renders, crops,
  screenshots, one-off scripts. Nothing loose in the repo root. `_cctmp.*` is
  gitignored;
- the PDF(s) the user handed over, until they move into `<slug>/`.

Anything else in `git status` — another untracked pedal directory, other
`_cctmp.*` dirs, unfamiliar PDFs in the root, uncommitted hunks in the catalog
or in this skill — is a sibling session's work in progress. That is normal:
don't open, move, delete, tidy, commit or ask about it; carry on. The one
exception is your own slug: `<slug>/` or `_cctmp.<slug>/` already present,
uncommitted and not created in this conversation means another session is on
the same pedal — stop and ask the user.

Shared files — root `index.html`, `catalog.txt`, this skill's `SKILL.md` and
`references/` — take concurrent edits:

- Change them with small `Edit` calls only; `Write` rewrites the file from your
  copy and drops everyone else's hunks. Read right before editing; if Edit
  reports the file changed since it was read, re-read and redo the edit.
- Leave hunks you didn't write alone — no reverting, reformatting, reordering.

Git, only when the user asks for a commit:

- Stage your own paths by name and commit by path, so whatever another session
  staged stays out: `git add <slug>/ && git commit -m "…" -- <slug>/
  index.html catalog.txt`. Never `git add -A`, `git add .`, `git commit -a`,
  `git stash`.
- A shared file is committed whole. `git diff` it first; if it carries another
  session's hunk (a card for an uncommitted page deploys as a broken link), ask
  the user before committing it.
- `.git/index.lock` exists → another session is mid-commit; wait and retry,
  never delete the lock.
- Push rejected because another session pushed first → tell the user; don't
  pull or rebase on your own.

## Token budget

Save tokens by not doing work twice and by not carrying what you are done
with, never by checking less: every rule below keeps the verification the
workflow asks for.

A response's output is capped (64K tokens here, thinking included), and a
response that hits the cap is cut off with whatever it was drafting lost.
Build `index.html` in pieces: write the skeleton (masthead, both TOCs, empty
`<section>`s) first, then fill one or two sections per response with `Edit`,
writing the copy straight into the file instead of drafting the page in
thinking first. The same holds for `style.css` and image-processing scripts:
decide the next piece, write it, run it. The Collider job lost two responses
to the cap, one of them all thinking.

Every response also re-sends the whole conversation, so a job costs roughly
its context size times its round trips. Whatever enters the context — a page
render, a screenshot, a chunk of `text.txt` — is paid for again on every
later call until the job ends, so the earlier it comes in, the more it costs.
An image costs about width × height / 750 tokens once scaled to fit 2,000 px
on its long edge: ~2,500 for a 3,000-px screenshot segment, ~2,800 for a
150-dpi page render, ~450 for a 60-dpi thumbnail. The Collider job read 104
images and all of `text.txt` into the main conversation, and by its
screenshot pass every request re-sent over 300K tokens.

- **Bulk looking happens in a subagent.** What a subagent (`Agent` tool,
  general-purpose) reads leaves with it; the main conversation gets back a
  text brief. A subagent starts at 25–45K tokens of context, a fraction of
  the main one mid-job, so the two bulk passes run there: the survey
  (step 2) and the screenshot verification (step 7). The main conversation
  keeps the looks that feed the edit at hand — the page a section is written
  from, the crop being checked.
- **Read text when you use it.** Past a few pages, don't read `text.txt`
  whole: the survey gives the outline with PDF page ranges, and each
  section's passage comes from `pdftotext -layout -f A -l B <pdf> -` right
  before you write it.
- Look at an image to answer a specific question, and look once. A render or
  screenshot you have seen doesn't change until you re-shoot it; step 7 says
  what to re-check after a fix.
- Set a handful of crops side by side in one contact sheet instead of
  reading them one by one, as long as each stays legible; tokens follow the
  pixels shown, so nine third-size tiles cost about what one full image
  does. `montage` labels each tile with its file name and native size (print
  furniture gives itself away by size):

  ```
  montage -font /System/Library/Fonts/Supplemental/Arial.ttf -label '%f %wx%h' \
    <images…> -tile 3x -geometry '600x>+8+8' -background white sheet.png
  ```
- Let a script answer what a script can: `check_page.py` for anchors and
  images, the `scrollWidth` line `screenshot.mjs` prints for horizontal
  scroll.
- Batch independent tool calls into one response; every extra round trip
  re-sends everything.
- After a compaction the summary carries the decisions. Re-read only what the
  next step needs — the next section's passage, the region of the file being
  edited — not the extracts: the Collider job re-read all of `text.txt` after
  its `/compact`.

## Workflow

### 0. Check the tools

```
.claude/skills/pdf-manual-to-html/scripts/check_tools.sh
```

It names whatever is missing with the `brew install` line that fixes it. If
anything is, stop and ask the user to install it rather than writing a
workaround: a hand-rolled PIL script for what `montage` does in one line
costs tokens on every job, the tool costs one install.

### 1. Frame the job

- **Pick a device:** Check the root `catalog.txt`. If there are devices listed without a leading `+ `, pick ONE unprocessed device (1 session = 1 device).
- **Download official manuals:** Find the latest official PDF manuals for this specific model **strictly on the manufacturer's website**. Download the main manual and *all* additional manuals offered (quick start guides, MIDI maps, addendums, etc.) into the repository root. If downloading is impossible (e.g. blocked, not found, or no PDF exists), **stop**, report this to the user, and offer to compile a DIY page from the descriptions and images available on the manufacturer's site.
- Identify **brand** and **model** from the downloaded PDF(s) (title, cover, footer).
- One PDF → one page. Several PDFs for one pedal → give each a role by reading
  it (the survey in step 2 does), not by date or file name: **full manual**
  (every control), **quick start** (small foldout card: hook-up and a few
  settings), **addendum / errata**, **older revision**. The full manual is the
  base page and the rest fold in (conventions → "Multiple PDFs"); a newer
  quick start doesn't outrank an older full manual.
- No PDF at all → compile the page from the maker's site and say so in a
  `.doc-update` banner (conventions → "Multiple PDFs", step 4).
- Target directory: `<brand>-<model>[-<variant>]/`, kebab-case, always in that
  order whatever the maker's wording. `model` is the core name without the
  effect-type word (`compressor`, `overdrive`, `delay`, `pedal`); `variant` is
  the qualifier (`mini`, `deluxe`, `v2`), omitted when there is none. Don't
  abbreviate or invent words: "Mini Ego Compressor" → `wampler-ego-mini/`.

### 2. Extract

Run once per PDF:

```
.claude/skills/pdf-manual-to-html/scripts/extract_pdf.sh <manual.pdf> _cctmp.<slug>/extract/<pdf-stem>/
```

It writes `info.txt` (metadata + **embedded fonts**, which drive the font
choice), `fonts-used.txt` (which text each face sets, and its CSS weight),
`text.txt` (copy source), `raw/` (embedded images in their native format) and
`pages/` (150 dpi renders). `text.txt` loses layout and colour, so every
passage is read beside its page render or the PDF itself (Read, `pages:`).

Render with `pdftocairo`, never `pdftoppm`: its Splash backend silently drops
some vector art (the green dotted rules under the BOSS NS-1X sub-headings),
and sampling or comparing such a render concludes the detail doesn't exist.
Something visible in a PDF viewer but missing from a render → suspect the
renderer before the PDF.

A near-empty `text.txt` and no fonts in `info.txt` mean the type was converted
to outlines at export — the file is fine, the words are curves. Read the copy
off the `pages/` renders and judge the fonts by eye.

An empty `raw/` means the art is vector and every figure gets cropped from
renders. Crop from a 300 dpi render of that page (`pdftocairo -png -r 300 -f N
-l N <pdf> _cctmp.<slug>/hires/p`) — the 150 dpi `pages/` give figures too
small for a high-density screen.

Printed page numbers rarely match the PDF page index (covers and TOCs shift
them). Confirm the index (`pdftotext -f N -l N`) before cropping or quoting by
page, or you'll pull from the neighbouring section.

**Survey in a subagent.** Once the extracts exist, hand the read-through to
one subagent so its images stay out of the main conversation. Give it the
PDFs, the extract dirs and `_cctmp.<slug>/` for its scratch; tell it to edit
nothing, to look at pages through `montage` sheets first and open a full
render only where a sheet is too small to read, and to return a text brief:

1. each PDF's role, with the line of evidence;
2. the outline — every section in the manual's order, its PDF page index
   range (not the printed number), sub-headings, and what it holds: prose,
   steps, table, knob cards, callouts;
3. the figure inventory — per figure: page index, what it shows, its
   section, and its source: a `raw/` file (the colour image, not its mask;
   say when a mask belongs merged in as alpha), or "vector, crop from page N
   at 300 dpi";
4. the style — fonts per role (body, headings, table labels, steps) with
   weights from `fonts-used.txt`; heading treatment per level; table borders;
   callout and note styles; the cover's colour-panel/photo split, measured;
   `sample_colors.py` on the cover render and product photo; whether the
   maker publishes an HTML online manual (search), and its font stack and
   colours if so;
5. what to double-check while writing — facts the PDFs disagree on, and
   jack, knob and switch names in steps or captions that contradict the
   panel description.

The brief drives steps 3 and 4; it doesn't replace your own reading. Each
section is still written from its own passage and page render (step 4), and
every copy check there stays yours.

### 3. Decide the style

Three sources, in order of preference:

1. **A same-brand page in this repo** (`ls -d <brand>-*`). Its `style.css`
   is already tuned to the maker's real palette and typefaces — reuse its
   tokens, heading treatment and callout patterns. Brands reuse one template,
   dingbat glyph set included, across whole product lines, but check before
   assuming: the fonts must match (`pdffonts` on both PDFs, or each extract's
   `info.txt`). A sibling modified in `git status` is being reworked by
   another session — read `git show HEAD:<sibling>/style.css`, not the
   working copy. Design languages also evolve: when this manual drops the
   sibling's heavy blocks, dotted rules or numbered badges for a cleaner
   look, strip that chrome rather than recolouring it.
2. **The brand's own online manual.** Many makers (Wampler included) publish
   one in HTML; the survey searches for it. If it exists, its CSS *is* the answer: font
   stack, colours, heading treatment, often the section structure too. This is
   how `wampler-terraform` was built.
3. **The PDF.** Map each embedded font to the nearest Google Font with the
   table in conventions (e.g. `MyriadPro` → "Source Sans 3"). For the palette,
   run `scripts/sample_colors.py <product photo> <cover render>` — the
   enclosure colour is the accent, the cover's ground is the dark band. Product
   photos usually come out of `raw/` as `.jpg`, so don't glob `*.png` only.

Put the result in a handful of CSS custom properties at the top of `style.css`
so the palette is swappable, with the font mapping — face → family and
weight — recorded in a comment.

Map weights as well as families. Every `font-weight` in the stylesheet comes
from a face in `fonts-used.txt` (Regular → 400, Semibold → 600, Bold → 700,
Black → 900): look up there which face sets the table labels, step
instructions and run-in heads instead of picking a weight by eye. A web
semibold standing in for a print Bold reads as a washed-out label. No semibold
face setting body text means no 600 anywhere on the page.

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

- **Masthead: wordmark.** The cover's wordmark is usually separate vector
  art, not part of the photo. Crop it from the render and set it as
  `<h1><img alt="<Brand> <Model>"></h1>` over the cover's ground colour;
  without it the page opens on an unlabelled photo. (`wampler-terraform/`
  predates this and opens on a bare `<img>` — follow the skeleton.) A model
  name set as live text on the cover (it's in `text.txt`) stays text:
  `<h1><img alt="<Brand>"> <span><Model></span></h1>`.
- **Masthead: photo.** A real photo of the pedal, cropped from a render when
  the manual has one. If it shows the enclosure only as line art (CAB X2),
  use the maker's own product photo from their site or listing rather than
  promoting the diagram; a third-party seller's photo needs a credit, the
  maker's doesn't.
- **Masthead: same brand, same arrangement.** Copy a same-brand page's
  masthead structure — where the photo sits, how logo, wordmark and document
  title (`Owner's Manual`) group — so the brand's pages read as one set,
  while the title block keeps this manual's lettering and ground: `boss-ge-7/`
  puts its blue header band inside `boss-rc-5/`'s photo-beside-title layout.
- **Masthead: panel proportions.** A cover split into a colour panel beside a
  photo panel gets its ratio measured on the render (crop width ÷ total),
  not picked by eye: a round 50/50 or 1:2 overweights the colour panel next
  to covers that run closer to 30/70. Set the masthead screenshot beside the
  cover render before moving on.
- `<nav id="side-nav">` fixed TOC on desktop, `#toc-mobile` in the flow for
  narrow screens, one `@media (max-width: 900px)` breakpoint that hides the nav.
- `<main>` with one `<section>` per manual section. The `id` goes on the
  section's heading, never on the `<section>`: site search links its hits
  only to headings with an `id`. `id`s are kebab-case and match the TOC
  anchors exactly; give sub-headings the reader would jump to one too.
- Semantic headings (`h2` section, `h3` sub-section …) — style them, don't pick
  tags by size.
- Reference tables (MIDI maps, spec sheets) → `.doc-table` inside
  `.table-scroll`.
- Print layout yields to HTML semantics: never break an `<ol>`/`<ul>` to drop
  an image in — the figure goes inside its `<li>` or above/below the list.
  Pick each section's layout (columns, `.no-columns`, `column-span`) from
  conventions → "Sizing the measure".

**Copy.** Pull each section's passage when you reach it (`pdftotext -layout
-f A -l B <pdf> -`) and look at its page render once beside it. Faithful to
the manual — same wording, same order — with the typos
fixed. Print manuals ship with them ("Smmoths everything out", "an experience
radio/TV technician", "the option or repairing"), and reproduced verbatim they
look like the page's mistake. Correct spelling, grammar and mangled phrases;
leave the author's voice, slang and deliberate informality alone. Where one PDF
garbles a sentence another prints cleanly, take the clean one. No `[sic]` — it
helps nobody in a pedal manual.

Where the sources disagree on a fact — the quick-start card says the power
supply is included and the manual says it isn't, one CC number is mapped to
two parameters — neither is a typo. Keep each as printed and list the conflict
in the report instead of picking one.

Makers build manuals from shared templates, and steps carry leftovers from
other products: the BOSS XS-1 manual says to plug into an "INPUT A (MONO)"
jack the pedal doesn't have. Check every jack, knob and switch a step names
against the panel descriptions, correct the ones that contradict it, and list
each in the report. Figure captions and diagram labels carry the same
leftovers — the Source Audio Collider's routing diagrams caption a
stereo-in, mono-out mode "Stereo In, Stereo Out" — so check each against the
section it illustrates.

**Figures.**

- Prefer embedded images from `raw/`; crop from a 300-dpi render (step 2)
  when they are sliced, vector or absent. A row of knob shots goes in a
  `.grid-wrapper`, `<img>` at `width: 100%`.
- `pdfimages` also dumps alpha masks and technical layers as separate
  grayscale images; ship the colour figure, not its mask (look at it, or
  `file` it for 3-channel RGB). A mask right after a colour image of the same
  size is that image's transparency — icons (warning sign, "!") come this
  way: merge it in with PIL `putalpha` and ship a `.png`.
- Crop by eye, never from text coordinates alone, then check the edges: a
  stroke or leader line running off the edge means the crop cut the drawing —
  widen it until every pointer ends at its target. When auto-trimming
  whitespace out of a generous region, a trimmed box touching the region's
  edge means the subject was cut — widen and re-trim until it sits clear.
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
- A figure whose printed background doesn't match its container (a
  white-ground icon in a tinted card, a dark-ground diagram on a light page)
  is a rendering problem, not a reason to cut it: recolour the background
  (safe on flat line art — replace the near-white/near-black pixels, keep the
  strokes), move it where its background belongs, or give it an untinted
  spot, then re-screenshot. Never delete manual content to get a clean
  screenshot.

### 5. Place the assets

```
<brand>-<model>/
  index.html
  style.css
  Images/            figures used by the page
  <original>.pdf     keep every source PDF alongside
  index-<year>.html  older revision, when folding in a newer one
```

The PDFs this job converts move from the repo root into the pedal's directory
(`git mv` if already tracked). Other PDFs in the root belong to other jobs.

Once the figures are final, shrink them for the web:

```
.claude/skills/pdf-manual-to-html/scripts/optimize_images.py <pedal-dir>
```

It caps image width, quantises PNGs and recompresses JPEGs in place, gives
every `<img>` its `width`/`height` and every one below the masthead
`loading="lazy"`. `style.css` needs `img { height: auto }` so those
attributes don't stretch a scaled image. It's lossy, so it runs before the
step 7 screenshots, where a banded gradient or a fuzzed hairline would show;
re-run it after adding or re-cropping a figure.

### 6. Add the catalog card

Add a `<li>` to the root `index.html` pedal list by copying a row already
there (`brand` / `model` / `type` / `note`), keeping the list sorted by brand,
then model. Read the file rather than trusting this one — the catalog is
hand-tuned and drifts. `type` is the filter category: reuse an existing one
(e.g. `Drive`, `Time`); a new value adds its own filter chip. `note` is a short
descriptor of what the pedal is, e.g. `Compressor`.

Then mark the pedal in the root `catalog.txt`, the list of pedals to convert:
a leading `+ ` flags a line as done. Edit the pedal's existing line rather
than adding one.

### 7. Verify before declaring done

- `scripts/check_page.py <pedal-dir>/index.html` — dangling TOC anchors,
  missing images and unreferenced files in `Images/`; none of them shows in a
  screenshot.
- Screenshot the whole page with `scripts/screenshot.mjs` at a desktop and a
  mobile width. It drives Chrome over CDP, captures the page's real height as
  numbered segments (`desktop-01.png`, `desktop-02.png`, …; a single capture
  past ~16,000 px repeats the page from the top) and prints the page's
  `scrollWidth`. Don't use `chrome --headless --screenshot --window-size=W,H`
  by hand: it crops to exactly W×H instead of the page's real height, and it
  has no timeout flag, so a bad size hangs with no way to detect it.

  ```
  mkdir -p _cctmp.<slug>/shot
  node .claude/skills/pdf-manual-to-html/scripts/screenshot.mjs \
    "file://$PWD/<pedal-dir>/index.html" "$PWD/_cctmp.<slug>/shot/desktop.png" 1400
  node .claude/skills/pdf-manual-to-html/scripts/screenshot.mjs \
    "file://$PWD/<pedal-dir>/index.html" "$PWD/_cctmp.<slug>/shot/mobile.png" 390
  ```

- Hand the looking to a fresh subagent, the verifier: a full pass is 20–40
  images, and in the main conversation each would ride along on every
  remaining request. Give it the page, the segment files, `pages/`, the
  survey's section → page map and the checks below; it edits nothing and
  reports each finding as text — section id, segment file, what the page
  shows, what the PDF shows — plus a line for each section it checked, so a
  gap in coverage shows.
  - Desktop segments against the PDF `pages/`: every section present,
    figures in the right place, nothing garbled.
  - Mobile: the `scrollWidth` line answers horizontal scroll; look only at
    the first segment (nav gone, mobile TOC shown) and the ones holding wide
    tables or figure grids.
  - Every table and callout cropped out of the desktop shot and set beside
    the same block on the page render, at the same scale, in a `montage`
    sheet. Check what a whole-page glance misses: text weight per column,
    vertical alignment in cells (labels are often centred against multi-line
    values), a rule above a table with no header row, the rule or dots under
    each sub-heading.
  - The palette on both light surroundings and the reversed-out header.
- Fix what it finds. After a local fix, re-shoot and look at the touched
  segment yourself; after a change to a shared rule (column width, figure
  sizing, body type), send a verifier over every segment the rule shows in.
  The report rests on one last full pass by a fresh verifier over the
  finished page.
- Delete your `_cctmp.<slug>/` — only that one; other `_cctmp.*` dirs belong
  to sessions still running.

### 8. Ask for review, propose skill updates

Don't declare the job done unprompted — show the result and ask the user
whether it looks right, and wait for their acceptance or corrections.

Show it as a short report under three headings, so the user can review it
without opening the diff:

- **What's inside** — the sections, in the PDF's order; where the style came
  from (sibling page, online manual, the PDF) and the heading, step and table
  treatment it gave; each layout call a reader would notice (a sticky diagram,
  a table restacked on mobile); what `check_page.py` and the screenshots at
  each width showed.
- **Copy changes** — every place the page's wording departs from the PDF, with
  the reason: typos, mangled phrases, template leftovers that contradict the
  pedal, page references turned into anchor links — plus the conflicts
  between sources left as printed. Nothing listed means verbatim.
- **Files** — the pedal directory and what moved into it, the catalog card,
  `catalog.txt`, scratch deleted, commit status.

Once they accept it, look back at what this job actually taught you: a
masthead proportion worth measuring rather than eyeballing, a same-brand quirk,
a layout call this manual forced, an extraction edge case you had to work
around. Write these as concrete, reusable suggestions for updating this skill
— framed for the *next* PDF, not a log of what you did on this one — and put
them to the user for review. Some jobs have nothing worth reporting, and
that's fine — don't manufacture a suggestion to fill the step.

Proposing a change is not permission to make it: only edit `SKILL.md` or
`references/conventions.md` when the user explicitly says to add it.

### 9. Deploy

Don't commit or push unless the user asks. The repo auto-deploys via GitHub
Actions on push to `master`; source PDFs live in the repo on purpose.

## Bundled files

- `scripts/extract_pdf.sh` — text, images, page renders and font list from a PDF.
- `scripts/font_usage.py` — which text each embedded face sets, and its CSS
  weight; `extract_pdf.sh` writes its output to `fonts-used.txt`.
- `scripts/check_tools.sh` — missing tools and the `brew install` line for them.
- `scripts/sample_colors.py` — dominant colours of an image, as hex.
- `scripts/screenshot.mjs` — full-page screenshot in segments, plus the page's
  `scrollWidth`.
- `scripts/optimize_images.py` — web-sized, recompressed images; `width`,
  `height` and `loading="lazy"` on every `<img>`.
- `scripts/check_page.py` — anchor, image and stray-file check on the built page.
- `references/conventions.md` — repo layout, the full HTML/CSS pattern from the
  reference implementation, the multi-PDF merge recipe, font-mapping table.
