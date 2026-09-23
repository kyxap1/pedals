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

Some of what a manual does is not a style but a device resting on the page
being a page — a measure fixed by hand, a known sheet size, a facing spread.
Move it across and the support is gone, so copying the appearance ships
something that no longer does its job: a manual holds table columns apart with
whitespace alone because six inches of measure make that enough, and the same
table full-width on screen needs rules to stay legible. Carry the intent over
on a mechanism this medium has and count that as fidelity, the way a
print-sized diagram scrolls instead of shrinking (conventions, the breakpoint)
and light-on-dark line art is recoloured onto the page ground (step 3).

`wampler-terraform/` is the reference implementation, and
`references/conventions.md` distils it: HTML skeleton, CSS pattern, multi-PDF
recipe, font table; `assets/base.css` is the structure every `style.css`
starts from. Read `conventions.md` before building, and a same-brand
sibling's `style.css` when one exists (step 3). Don't read `wampler-terraform/index.html` (~85 KB) whole; grep it for a
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

The shared files — root `index.html`, `catalog.txt`, this skill's `SKILL.md`
and `references/` — take concurrent edits, and a commit has to keep a
sibling's work out of it. `references/parallel-sessions.md` has both rules;
read it before editing a shared file and before any git command.

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
decide the next piece, write it, run it.

Every response also re-sends the whole conversation, so a job costs roughly
its context size times its round trips, and whatever enters the context is
paid for again on every later call until the job ends. An image costs about
width × height / 750 tokens once scaled to fit 2,000 px on its long edge:
~2,500 for a 3,000-px screenshot segment, ~2,800 for a 150-dpi page render,
~450 for a 60-dpi thumbnail. The Collider job read 104 images and all of
`text.txt` into the main conversation, and by its screenshot pass every
request re-sent over 300K tokens.

- **Bulk looking happens in a subagent.** What a subagent (`Agent` tool,
  general-purpose) reads leaves with it; the main conversation gets back a
  text brief. A subagent starts at 25–45K tokens of context, a fraction of
  the main one mid-job, so the two bulk passes run there: the survey
  (step 2) and the screenshot verification (step 7). The main conversation
  keeps the looks that feed the edit at hand — the page a section is written
  from, the crop being checked. This is the rule most often lost mid-job:
  the focusrite job pulled some twenty montages and screenshot segments into
  the main conversation itself, shooting and looking after each small fix,
  and every one of them was re-sent on every request that followed.
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
- Let a script answer what a script can, and read its text instead of looking:
  `check_page.py` for anchors and images, `crop_figure.py --check` for a crop
  that cuts the drawing, the `scrollWidth` line `screenshot.mjs` prints for
  horizontal scroll, `check_columns.mjs` for broken column breaks.
- Never poll. A subagent's result and a background command's exit arrive as
  a notification; until then do the next independent piece of work, or end
  the turn. A `sleep`/`ls`/`cat` loop watching for them is a round trip per
  check: the ENGL job spent some 300 calls, each re-sending 150K+ tokens,
  watching its reviewer's scratch directory. The scripts here finish in
  seconds — run them in the foreground.
- Batch independent tool calls into one response; every extra round trip
  re-sends everything.
- After a compaction the summary carries the decisions. Re-read only what the
  next step needs — the next section's passage, the region of the file being
  edited — not the extracts.

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

Not every job starts empty. Folding in a newer revision, re-deriving an
existing page and auditing one somebody else converted are all this workflow,
run over a page that already exists — and in those, step 7 cannot lean on your
own memory of what you chose. Whatever the earlier job decided is either
written down beside the page or has to be derived from the PDFs again before
anything can be called wrong. Establish which before reporting a defect.

- **Pick a device:** check the root `catalog.txt`. Where devices are listed
  without a leading `+ `, take ONE unprocessed device — one session, one
  device.
- **Download official manuals:** find the latest official PDFs for this exact
  model **on the manufacturer's own site**, and take the main manual together
  with *all* the extra documents offered (quick start, MIDI map, addendum,
  firmware guide) into the repository root. "Official" is not one place: a
  maker serves the same document from its product page, its manuals index and
  its downloads index, and those drift apart by revisions that change real
  specifications. Compare what each offers rather than taking the first hit,
  and record which one the file came from — provenance is a fact about the
  page, not a step you did once. If downloading is impossible (blocked, not
  found, no PDF exists), **stop**, tell the user, and offer to compile the
  page from the descriptions and images on the maker's site.
- **PDF handed over by the user:** still check the maker's site. `cmp` the
  file against the official copy (a newer revision may be up) and download the
  extra documents offered for the model — quick start, firmware update guide,
  addendum; they fold in like any second PDF.
- Identify **brand** and **model** from the downloaded PDF(s) — title, cover,
  footer.
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

`text.txt` is one projection of the PDF, not the PDF. Whatever isn't glyphs —
a link annotation hiding behind words, the rotation an image is placed at, the
revision in the metadata, a cell the printed layout truncates — leaves no gap
behind when it's dropped, so nothing downstream ever reports it missing. Work
out what the source carries besides its text before building the page from the
text.

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
render only where a sheet is too small to read, and to return a text brief.
A manual of four pages or fewer is surveyed inline instead: its pages cost
less to look at than a subagent costs to start. The brief covers:

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
   one in HTML; the survey searches for it. If it exists, its CSS *is* the
   answer: font stack, colours, heading treatment, often the section structure
   too. This is how `wampler-terraform` was built.
3. **The PDF.** Map each embedded font to the nearest Google Font with the
   table in conventions (e.g. `MyriadPro` → "Source Sans 3"). For the palette,
   run `scripts/sample_colors.py <product photo> <cover render>` — the
   enclosure colour is the accent, the cover's ground is the dark band. Product
   photos usually come out of `raw/` as `.jpg`, so don't glob `*.png` only.

Start `style.css` as a copy of `assets/base.css` (`cp`, not retyped): it
carries the layout, the column-break rules and the breakpoint every page
needs. Set its tokens — palette, font families, the Google Fonts import —
with the font mapping, face → family and weight, recorded in its first
comment, and write the brand layer under its last line.

Map weights as well as families. Every `font-weight` in the stylesheet comes
from a face in `fonts-used.txt` (Regular → 400, Semibold → 600, Bold → 700,
Black → 900): look up there which face sets the table labels, step
instructions and run-in heads instead of picking a weight by eye. A web
semibold standing in for a print Bold reads as a washed-out label. No semibold
face setting body text means no 600 anywhere on the page.

Where the manual encodes information in type itself — a word set in the colour
it names, a state shown only by which circle is filled — carry over the one
property that does the encoding, not the whole look of the sample it was taken
from. The sample also carries its context: a colour word in a table header is
bold because it sits in a header, not because it is a colour, and a class that
bakes in both is wrong everywhere else it lands. Read it the other way too —
anything carried by one property alone is missing from `text.txt`, which is
how a live table can survive extraction as a column of bare labels.

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

- **Masthead.** The cover's wordmark over the cover's ground, then a real
  photo of the pedal, arranged the way a same-brand page already arranges
  them, with the cover's panel ratio measured rather than guessed —
  conventions → "Masthead" has each of those and what goes wrong without it.
- `<nav id="side-nav">` fixed TOC on desktop, `#toc-mobile` in the flow for
  narrow screens, one `@media (max-width: 900px)` breakpoint that hides the nav.
- `<main>` with one `<section>` per manual section. The `id` goes on the
  section's heading, never on the `<section>`: site search links its hits
  only to headings with an `id`. `id`s are kebab-case and match the TOC
  anchors exactly; give sub-headings the reader would jump to one too.
  **A published `id` is a contract.** The MCP server keys its sections on it
  and hands agents `…/<slug>/#<id>` as the citation, so re-deriving a page
  from a newer PDF keeps every `id` it already published, even where the
  heading's wording changed — a renamed `id` breaks every link already given
  out, and nothing in CI can catch it. Put an `id` only on a heading that has
  something under it. Before publication, rename freely.
- Semantic headings (`h2` section, `h3` sub-section …) — style them, don't pick
  tags by size.
- Reference tables (MIDI maps, spec sheets) → `.doc-table` inside
  `.table-scroll`.
- Every content image carries an `alt` that says what the image tells the
  reader, not what it is a picture of — "LED C flashes red, hold to set POP
  STOP, tap to set MIDI chain", not "configuration mode". A text-only consumer
  (the MCP server, a screen reader) is handed the `alt` and nothing else, and
  a handful of headings have no prose under them at all, so a thin `alt`
  leaves that section empty.
- Print layout yields to HTML semantics: never break an `<ol>`/`<ul>` to drop
  an image in — the figure goes inside its `<li>` or above/below the list.
  Pick each section's layout (columns, `.no-columns`, `column-span`) from
  conventions → "Sizing the measure".
- The layout comes from the source section by section, like the outline. A
  manual mixes its own page layouts — the pages where UI screenshots carry
  the instructions are often set in one wide column while the rest runs in
  two — so match each section to its own pages instead of imposing one grid
  on the whole document. A screenshot squeezed into half a column is
  unreadable, and no amount of column tuning fixes that.

**Copy.** Pull each section's passage when you reach it (`pdftotext -layout
-f A -l B <pdf> -`) and look at its page render once beside it. Faithful to
the manual — same wording, same order — with the typos
fixed. Print manuals ship with them ("Smmoths everything out", "an experience
radio/TV technician", "the option or repairing"), and reproduced verbatim they
look like the page's mistake. Correct spelling, grammar and mangled phrases;
leave the author's voice, slang and deliberate informality alone. Where one PDF
garbles a sentence another prints cleanly, take the clean one. No `[sic]` — it
helps nobody in a pedal manual.

What print can only point at, the page links. A cross-reference ("see
chapter 8", "on page 12", "the MIDI Implementation chapter", "see Global
Settings") becomes an anchor on its words — `See <a href="#message-stacks">chapter
8</a>` — aimed at the sub-heading it means when it names one (give that
heading an `id`). Every URL and e-mail address becomes `<a href>` /
`mailto:` with its printed text kept; a printed `www.` host still gets an
`https://` href. `check_page.py` lists any left bare.

Log every departure as you write it, in `_cctmp.<slug>/copy-changes.md`:
section, printed wording, page wording. Added words ("so", "in") count, and so
do dropped or added punctuation and respacing. The reviewer's list of allowed
changes and the report's **Copy changes** both come from this log;
reconstructed from memory at the end, the NUX Atlantic list missed eight edits
the reviewer then flagged.

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
- `raw/` numbers images in content-stream order, not reading order. When a
  page carries several look-alike images — a row of preset thumbnails, a set
  of knob shots — match each one to its place against the render, never by
  file index: the mix-up looks plausible on the page and survives every
  script.
- Draw the box by eye off the render, never from text coordinates, then let
  `scripts/crop_figure.py <page.png> <out.png> X Y W H` finish it: it pushes
  out every edge ink still crosses until no stroke runs off the boundary,
  trims the slack back and pads. A box drawn tight by eye cuts arrowheads,
  leader lines and the tail of a label, and the loss only shows up later,
  beside the PDF. `CAPPED` in its output means the growth limit was reached —
  the figure runs into body text or a neighbouring drawing there, so look
  before shipping. It reads light-on-dark line art the same way.
- `crop_figure.py --check <crop.png>` runs that test on a finished file: use
  it on every figure before the screenshots, and on figures an earlier job
  cropped when re-deriving a page. Edges the figure's own ground fills (a
  photo, a tinted panel, a circular badge) are reported apart from cut
  strokes and are not a failure. An image shipped from `raw/` uncropped
  carries the maker's own frame: `cut` there means the source frames its
  subject tight, and the fix, if any, is padding, not a new crop.
- **Nothing that reads as text ships as pixels.** A table printed as a
  screenshot is transcribed into a real `<table>` (conventions → "Reference
  tables"): a reader can't scan or search a flat picture, and it goes
  illegible the moment it's scaled for mobile. Body text printed inside a figure goes into the HTML
  and is painted out of the image with the background colour; integral labels
  (numbered pointers) stay. No exceptions for row or column count —
  logotypes are the only figures allowed to carry text.
- Copy across only the images the page shows, named for what they depict
  (`setting-1.png`, `ego-mini-header.jpg`). Most of the dump is print
  furniture — gradient strips a few pixels tall, slivers of rules, repeated
  logos; their dimensions give them away. `Images/` is kept forever, so it
  holds figures, not leftovers.
- Photos are `.jpg` (`.png` when they need transparency); line art, wordmarks
  and screenshots are `.png`.
- Masks and technical layers in `raw/`, icons cropped from beside text,
  pictograms with printed labels, a pair of figures that must match, and a
  figure whose background fights its container: conventions → "Figure craft".

### 5. Place the assets

```
<brand>-<model>/
  index.html
  style.css
  Images/            figures used by the page
  <original>.pdf     keep every source PDF alongside
  copy-changes.md    every departure from the print, and where each PDF came from
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
`loading="lazy"` (`screenshot.mjs` forces those to load before it captures).
`style.css` needs `img { height: auto }` so those
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

Do all verification **before** deleting the `_cctmp.<slug>/` extract directory, so you don't have to extract twice if you need to fix something.

Every check below is narrow, and a clean run is a claim about that check's own
scope, never about the page. Report one as clean together with what it cannot
see, or a row of green ticks reads as coverage that nothing measured.

A step's own tool is not that step's verification. A script written to fill in
what's missing leaves what is wrong exactly as wrong, and re-running it after
an edit proves only that it is idempotent. Check a result against the source
with something that had no hand in producing it.

A scan over the copy has to reach the short text too. A length threshold
picked to hold the noise down cuts out headings, captions and labels — the
text most likely to be invented, and the worst place for it, because a reader
takes it for the document's own structure.

**The checks are cheap; the cycles around them are not.** A script run costs a
few hundred tokens of text, while a fix cycle costs a screenshot pass, a look
and a round trip that re-sends the whole conversation. So run each check once,
take everything it found, fix the lot in one editing pass, and only then run
it again: the focusrite job ran `check_columns.mjs` twelve times and
`screenshot.mjs` ten, mostly one finding at a time, and spent more context on
the loop than on building the page. Between passes, re-check with the text
tools — `check_columns.mjs` and `crop_figure.py --check` answer in words —
and re-shoot only at the width a finding named. The screenshot pass for the
reviewer runs once, when the page is ready.

`figure`, `lead-in`, `orphan`, `split` and `overflow` from `check_columns.mjs`
are defects every reader at that width sees — a heading at a column's foot, a
sentence cut by the gutter — so the page ships with none of them between 1200
and 2000 px. `unbalanced`, a finding only at the sweep's edges, a badge whose
round edge reads as 1% wet: note it in the report and move on. Most column
findings share one cause (a heading outside its `.keep-together`, a missing
`break-inside`), so fix the cause across the page, not the one heading named.

- `scripts/check_page.py <pedal-dir>/index.html` — dangling TOC anchors,
  missing images and unreferenced files in `Images/`; none of them shows in a
  screenshot.
- Every shipped figure through `crop_figure.py --check`, which sees a severed
  stroke the page screenshots can't — on the page the crop looks deliberate:

  ```
  for f in <pedal-dir>/Images/*.png; do
    printf '%s: ' "$f"
    .claude/skills/pdf-manual-to-html/scripts/crop_figure.py --check "$f"
  done
  ```
- `scripts/check_columns.mjs "file://$PWD/<pedal-dir>/index.html"` sweeps
  1000–2600 px — one screenshot width proves nothing about breaks that move
  with the viewport — and names six failures with the widths they happen at:

  | kind | what it found | fix |
  |---|---|---|
  | `figure` | a figure starting the right column while its lead-in stays left | `.keep-together` around lead-in + figure + follow-up |
  | `lead-in` | a block ending in ":" split from its list or menu path | the `:has()` rule, or `.keep-together` |
  | `orphan` | a sub-heading left at a column's foot, its content in the next | `.keep-together` around the heading and its first block; `break-after: avoid` alone doesn't hold |
  | `split` | a paragraph or list item cut across the gutter | `break-inside: avoid` on it (in `base.css`); a paragraph taller than a column is split by hand at a sentence |
  | `unbalanced` | one column ending far above the other | usually a tall figure or an over-wide `.keep-together`; conventions → "Sizing the measure" |
  | `overflow` | an unbreakable string pushing its block past the column | `overflow-wrap: anywhere` on that block |

  Exits 1 on any finding; fix with conventions → "Column breaks" and re-run
  until clean. Headless Chrome needs a real bound: `timeout 320`. The
  `figure` and `lead-in` checks read the flow two blocks back and skip tables
  and figure grids, so a finding whose *immediately* preceding block sits in
  the same column is the tool looking past the pair, not a break to chase —
  confirm which it is by measuring before editing.
- When a block lands somewhere the CSS says it shouldn't, measure it before
  rewriting the rule: read `getBoundingClientRect()` and the computed style
  of the element and its container over CDP. A rule that reads as correct
  can still resolve to something else — `auto-fit` sizing its track count off
  a definite max, an `img` laying out inline, a `break-after: avoid` the
  balancer cannot honour. Guessing at the cascade burns a round trip per
  guess.
- Screenshot the whole page with `scripts/screenshot.mjs` at 1400 and 390.
  Breaks at other widths are `check_columns.mjs`'s job, in words; shoot
  another width only to look at a finding it named there. It drives Chrome over CDP, captures the page's real height as
  numbered segments (`w1400-01.png`, `w1400-02.png`, …; a single capture
  past ~16,000 px repeats the page from the top) and prints the page's
  `scrollWidth`. Don't use `chrome --headless --screenshot --window-size=W,H`
  by hand: it crops to exactly W×H instead of the page's real height, and it
  has no timeout flag, so a bad size hangs with no way to detect it.

  ```
  mkdir -p _cctmp.<slug>/shot
  for w in 1400 390; do
    node .claude/skills/pdf-manual-to-html/scripts/screenshot.mjs \
      "file://$PWD/<pedal-dir>/index.html" "$PWD/_cctmp.<slug>/shot/w$w.png" $w
  done
  ```

- Hand the looking to a fresh subagent, the **reviewer**: it checks what
  converted wrong and tells you (the main model) what to fix. Give it the
  page, the segment files, `pages/`, the survey's section → page map and
  `references/review-checklist.md` — the checklist is its mandate, and it
  reads it itself rather than having it repeated here. It edits nothing and
  reports each finding as text: section id, segment file, what the page
  shows, what the PDF shows.
- **Redo Loop:** If the reviewer finds issues, **kick yourself (the main model) to fix the glitching parts**. You must redo the broken parts and re-screenshot them. You can loop this review-fix cycle **a maximum of 2 times in a row**. A re-review gets the previous findings and checks those and the sections the fixes touched, not the whole page again — a full pass costs as much as the build's own looking.
- **Only after passing review or hitting the retry limit**, move
  `copy-changes.md` out of the scratch and into `<pedal-dir>/`, then delete
  your `_cctmp.<slug>/` — only that one; other `_cctmp.*` dirs belong to
  sessions still running. The log is what makes the page reviewable later:
  without it nobody can tell a deliberate departure from the print apart from
  a conversion error without deriving every difference from the PDFs again.
  Don't end a job by destroying the record of its decisions.

### 8. Ask for review, propose skill updates

Respond to the user in the same language they used for their request.

Don't declare the job done unprompted — show the result and ask the user
whether it looks right, and wait for their acceptance or corrections.

Show it as a short report under three headings, so the user can review it
without opening the diff. Keep it to about thirty lines: one line per check,
one per copy change, and point at `copy-changes.md` for the rest. A report
the user has to wade through gets skimmed, and what it was meant to surface
gets missed.

- **What's inside** — the sections, in the PDF's order; where the style came
  from (sibling page, online manual, the PDF) and the heading, step and table
  treatment it gave; each layout call a reader would notice (a sticky diagram,
  a table restacked on mobile); what `check_page.py`, `crop_figure.py
  --check`, `check_columns.mjs` and the screenshots at each width showed.
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
anything under `references/` when the user explicitly says to add it.

### 9. Deploy

Don't commit or push unless the user asks. The repo auto-deploys via GitHub
Actions on push to `master`; source PDFs live in the repo on purpose.

## Bundled files

- `assets/base.css` — the shared structure every `style.css` starts from.
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
- `scripts/check_columns.mjs` — orphaned headings, split paragraphs, figures
  and `:` lead-ins parted from their text, swept over viewport widths.
- `scripts/clean_crop.py` — an icon crop stripped of neighbouring letters and
  rule ends.
- `scripts/crop_figure.py` — a rough box grown into a crop that cuts nothing,
  and `--check` on a finished crop.
- `references/conventions.md` — repo layout, the full HTML/CSS pattern from the
  reference implementation, the multi-PDF merge recipe, font-mapping table.
- `references/parallel-sessions.md` — editing a shared file and committing
  while other sessions work in the same checkout.
- `references/review-checklist.md` — the step 7 reviewer's mandate, handed to
  the subagent.
