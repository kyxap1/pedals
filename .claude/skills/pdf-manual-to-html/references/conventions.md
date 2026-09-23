# Conventions & patterns

Everything here is distilled from `wampler-terraform/` in this repo. When in
doubt, open that page and copy what it does.

## Repo layout

```
pedals/
  index.html                 root catalog — searchable list of pedals
  favicon.svg
  <brand>-<model>[-<variant>]/
    index.html               the manual
    style.css                per-pedal stylesheet (each pedal has its own look)
    index-<year>.html        archived older revision (only when a newer PDF was folded in)
    Images/                  figures referenced by index.html
    *.pdf                    every source PDF, kept in-tree
```

- Directory and `id` names: kebab-case, ASCII.
- One stylesheet per pedal. Do **not** try to share a stylesheet across pedals —
  the whole point is that each manual looks like itself.
- The root `index.html` is hand-maintained; just add a `<li>` row.

## HTML skeleton

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="style.css" />
    <title>&lt;Brand&gt; &lt;Model&gt; Pedal Manual</title>
  </head>
  <body>
    <nav id="side-nav">
      <header>
        <div class="nav-container">
          <h3>Contents</h3>
          <h4><a href="#intro">Welcome</a></h4>
          <!-- one entry per section; h4 = section, h5 = sub-section -->
        </div>
      </header>
    </nav>
    <main id="main-doc">
      <div id="masthead">
        <div class="flex-container">
          <div class="half-container no-columns">
            <!-- the wordmark cropped out of the cover render, over the cover's ground -->
            <h1><img src="Images/wordmark.png" alt="&lt;Brand&gt; &lt;Model&gt;" /></h1>
            <img src="Images/header.jpg" alt="&lt;Brand&gt; &lt;Model&gt; User Guide" />
          </div>
        </div>
      </div>
      <!-- the id goes on the heading, not the <section>: search results
           link only to headings with an id -->
      <section>
        <div class="flex-container">
          <div class="half-container flow">
            <header><h2 id="intro">Welcome</h2></header>
            <!-- one .topic per heading: it carries the columns -->
            <div class="topic level-3">
              <h3 id="what-it-does">What it does</h3>
              <p>…</p>
            </div>
            <div class="topic level-4">
              <h4 id="controls">Controls</h4>
              <p>…</p>
            </div>
          </div>
          <div id="toc-mobile" class="half-container">
            <h2>Contents</h2>
            <!-- same links as the side nav, shown only below 900px -->
          </div>
        </div>
      </section>
      <!-- more <section><…><h2 id="…"> … -->
    </main>
    <footer>…</footer>
  </body>
</html>
```

## Masthead

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

The wordmark and the photo are separate crops: the wordmark is the logotype
alone, so a tagline or URL printed beside it on the cover is text and goes
into the HTML.

## CSS pattern

`assets/base.css` is the structure every page shares: tokens, side nav,
sections, `.topic` columns, the column-break rules, figure rows, tables,
callouts and the single 900-px breakpoint. Copy it to `<slug>/style.css`,
then set the tokens and the font import from this manual and write the brand
layer under its last line — masthead, heading treatment (`h2` reversed out or
ruled, `h3` caps or underlined), callout and card styles. Change a structural
rule only for a reason this manual gives, and say why in a comment; the
break rules and the breakpoint encode bugs earlier pages shipped.

Two things the stylesheet can't do for you:

- Figures meant to fill their box (`.grid-wrapper` shots, the panel photo) get
  `width: 100%` on their own selector; plain `img` keeps `max-width`, so a
  pictogram stays at the size its `width`/`height` give it.
- Inline pictograms (an icon named mid-sentence) carry their own class and stay
  inline; `li > img` and `.topic > img` are blocks.

## Sizing the measure

A section body at full window width sets 160+ characters a line, and the eye
loses the start of the next one. A fixed `max-width` is no fix: it leaves a
narrow strip beside a dead gutter. The measure has to come *from* the window:

```css
.topic {
  columns: 2 30rem;     /* at most two columns, one below ~63rem of room */
  column-gap: 3em;
}
.half-container > header { column-span: all; }
```

The columns go on the **topic**, not on the section. In print the page ends
the column; on a page nothing does, so a section-wide container gives a long
section two columns several screens tall — the reader walks the left one
down and climbs back up for the right. Wrap each heading with the content
that follows it (down to the next heading of any level) in a `.topic` and put
the columns there, so a column is never taller than one topic, the way the
manual gives each topic its own page. Mark the level on the wrapper
(`.topic.level-3`) to rule off the ones that open a new `h3`.

With both a count and a width, `columns` does it all: the width decides how
many columns fit, the count caps them at two, and they stretch to fill the
room — one column below ~63rem, no breakpoint, no empty right half. Size the
column in `rem`, not `em`: an `em` column grows with the body type, so a
manual set a size up from 16 px stops fitting two columns beside the side nav
at common desktop widths.

Multi-column, not a grid: a grid row is as tall as its tallest cell, so one
long knob description leaves a hole under every short one beside it.
Multi-column balances the column heights itself.

A figure or table lives *inside* its column (`max-width: 100%`), flowing with
the text, as in print. `column-span: all` is only for what the source itself
breaks the column for: a multi-image comparison grid, a table that needs every
column's width to stay legible, the section title. Spanning anything else
makes the browser balance the columns *before* the span — empty space
stranded in the shorter column, content stretched past its size. An image or
table interrupting the text flow in a screenshot, a gap above one, or list
items pushed into the wrong column mean a stray `column-span: all`: drop it
and let the figure sit in its column.

**Column breaks.** The balancer splits content wherever it likes, so:

- A heading and its first block share a `<div class="keep-together">` — an
  `h3` with its lead-in, a FAQ question with its answer. `break-after: avoid`
  is in `base.css`, but Chrome's balancer drops it whenever it gets in the way,
  and a heading wrapped alone keeps nothing with it. Scope the wrapper
  narrowly, heading plus first paragraph, and let lists and notes below flow
  free: the wrapper is indivisible, and one that doesn't fit the shorter
  column jumps whole into the other. A heading directly over a list shares
  the wrapper with it when the list is short; over a long one it stays out,
  and `check_columns.mjs` says whether it orphans.
- `p, li { break-inside: avoid; }`: a paragraph split across the gutter reads
  as two fragments. Never on a whole `ul`/`ol` — long lists flow across
  columns.
- A figure shares a column with the sentence that leads into it ("as shown
  below") and with what continues from it ("The options are:" and its list).
  Wrap exactly that — lead-in, figure, follow-up — in `.keep-together`. When
  a paragraph carries more than the lead-in, split it at its `<br>` so only
  the lead-in travels with the figure; bundling the whole paragraph moves it
  all to the other column and leaves a hole.
- A bundle that still jumps to the right column and leaves its sub-heading
  behind gets `.column-end` on it: the left column ends after it. The break is
  gated on two columns fitting — in a single column a forced column break
  overflows sideways.
- A lead-in ending in ":" (`go to:`) never ends a column above its menu path;
  the `:has()` rule below holds that without a wrapper per pair.
- A figure taller than the prose beside it ends its column most of a screen
  below the other one, and no break rule fixes that: the column simply has
  more to hold. Give that topic `.no-columns` and let the figure run under its
  paragraph at a capped width (`max-width: min(44em, 100%)`), or pull the next
  block up into the same topic so the second column has something to fill
  with. `check_columns.mjs` reports it as `unbalanced`.


Column breaks move with every viewport width, so one screenshot proves
nothing about them: `scripts/check_columns.mjs` sweeps 1000–2600 px and
reports, with the widths where each happens, a figure stranded from its
lead-in (`figure`), a `:` lead-in split from what it introduces (`lead-in`),
a sub-heading left at a column's foot (`orphan`), a column ending far above
the other (`unbalanced`) and an unbreakable string pushing past its column
(`overflow`).

**Short sections.** A blurb under ~10–14 lines (an "About this manual" or
"Support") split into columns leaves a tiny isolated column; its container
gets `.no-columns` and runs full width:

```html
<div class="half-container no-columns">...</div>
```
```css
.no-columns { columns: auto !important; }
```

**Picking the layout per section.** Decide section by section from the shape
of its content, not from where the print page happened to fit it:

| Section content | Layout |
|---|---|
| Running prose, bullet lists | The default two columns |
| A short blurb — little *height*: under ~10–14 lines, no figures | `.no-columns` |
| Numbered steps with a figure per step | The default two columns, each figure inside its `<li>` under the step text. Short on words but tall: `.no-columns` leaves the right half of the screen empty |
| One figure plus a procedure (changing the battery) | The default two columns, the figure first in the flow, no `column-span` |
| Per-part description cards around a panel diagram | The diagram beside the cards (`grid-template-columns: minmax(12em, 17em) 1fr`, figure `position: sticky`), the cards in `columns: 2 16em`, leader lines painted out of the diagram — they point at print positions that no longer exist. Never a grid of cards: each row stretches to its tallest card and leaves the rest mostly empty tint. Every card `break-inside: avoid`; only a card taller than a column may break, or a mid-length one splits its sub-heads from its title across the gutter |
| An ordered run of look-alike cards (presets, modes, sequential settings) | One column, or a grid whose rows follow the print order. Equal-height cards in two columns read as a table, row by row, while the columns flow top to bottom, so the sequence scrambles |
| Reference table (specs, MIDI map) | `.no-columns`, or `column-span: all` on the table |

Symptoms in a desktop screenshot: the right half of a section empty → a
`.no-columns` on content that is tall rather than short; a tinted card with a
large empty bottom → cards in grid rows; one column ending a screen above the
other → a figure taller than the text sharing its topic.

## Figure craft

- `pdfimages` also dumps alpha masks and technical layers as separate
  grayscale images; ship the colour figure, not its mask (look at it, or
  `file` it for 3-channel RGB). A mask right after a colour image of the same
  size is that image's transparency — icons (warning sign, "!") come this
  way: merge it in with PIL `putalpha` and ship a `.png`.
- Figures that belong together (front and back panel, a before/after pair)
  are checked side by side in one `montage` at equal display width. Each one
  looks right alone; margins left in one of them shrink its subject by half
  next to the other, and at `width: 100%` the page shows exactly that.
- An icon printed in a box beside text drags letters and rule ends into any
  crop that holds all of it: crop the box, then `scripts/clean_crop.py in.png
  out.png` keeps the largest dark shape, whitens the rest and trims.
- Pictograms carrying printed labels (toggle positions, jack names) ship at
  their 300-dpi crop's native size, `width`/`height` equal to the file's;
  scaled down, the labels blur into 4-px smudges.
- A figure whose printed background doesn't match its container (a
  white-ground icon in a tinted card, a dark-ground diagram on a light page)
  is a rendering problem, not a reason to cut it: recolour the background
  (safe on flat line art — replace the near-white/near-black pixels, keep the
  strokes), move it where its background belongs, or give it an untinted
  spot, then re-screenshot. Never delete manual content to get a clean
  screenshot.

## Multiple PDFs (revisions / addenda / quick-starts)

The repo folds them into one page rather than publishing three:

1. Newest full manual = the base page (`index.html`).
2. Fold the extra PDFs in where they belong:
   - a **quick-start** → its own `<section id="quick-start">` at the end, linked
     from the TOC. Where it carries something the full manual simply lacks —
     a power specification, a service address — that material gets a proper
     section of its own where a reader would go looking for it, marked with the
     inline note class; leaving it buried in the quick-start summary means
     nobody finds it.
   - an **addendum / errata** → apply the corrections inline at the relevant
     sections, and add a `<section id="addendum">` summarising what changed.
   - a **spec/warranty revision** → overwrite the affected lines inline.
3. Mark inline changes so a reader can see what the update touched:

```css
.v1-note {                         /* rename to match the update, e.g. .v2-note */
  border-left: 3px solid var(--accent);
  padding-left: 0.75em;
}
```

4. Put a changelog banner right under the first heading:

```css
.doc-update {
  background: var(--paper);
  border-left: 4px solid var(--accent);
  padding: 1em 1.25em;
}
.doc-update > strong { display: block; text-transform: uppercase; }
```

   It carries only what changes how the page is read: which hardware variant
   the manual describes, or that an appendix comes from a second document in a
   different voice. Which file came from where, under what name, at which
   revision, and what was reworded are facts about the conversion rather than
   about the product — they go in the footer line and in `copy-changes.md`.
   The test is whether the maker would have printed it.
   *Note: If no official PDF manual exists, use this same `.doc-update` banner for a single short sentence without a heading: "No official PDF manual, compiled from the official website."*
5. If an older revision differs enough to be worth keeping, save it as
   `index-<year>.html` (older tokens, older content, its own trimmed TOC) and
   link it from the changelog banner: "Own an earlier pedal? Read the archived
   <year> revision."

## Reference tables

```html
<div class="table-scroll">
  <table class="doc-table">
    <thead><tr><th>CC#</th><th>Parameter</th><th>Range</th></tr></thead>
    <tbody><tr><td>…</td><td>…</td><td>…</td></tr></tbody>
  </table>
</div>
```

```css
.doc-table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
.doc-table th, .doc-table td { border: 1px solid var(--accent); padding: 0.4em 0.5em; vertical-align: top; }
.doc-table thead th { background: var(--accent); color: #fff; text-transform: uppercase; }
.table-scroll { overflow-x: auto; }
```

The baseline is a fully enclosed grid; many manuals rule rows only. Match the
render — keep only `border-bottom` on rows when the source has no vertical
dividers. One exception, and it is the page-is-a-page case: print holds columns
apart with whitespace at a measure set by hand, and a table stretched to the
full width of a screen has neither. Three or more columns with a short one
among long ones — a two-word `Version` between two columns of prose — read as a
single run-on band; rule them vertically in the hairline colour even where the
source has none, and pad the cells on both sides.

## Font mapping (PDF embedded → Google Font)

Embedded names show up in `info.txt`. Pick the closest free web font:

| PDF font (subset prefix stripped) | Web font |
|---|---|
| Helvetica, Arial | system sans, or `Inter` |
| Futura, Futura-CondensedLight | `Oswald`, `Archivo Narrow` |
| MyriadPro (all weights) | `Source Sans 3` |
| Avenir | `Nunito Sans`, `Montserrat` |
| Frutiger, Univers | `Inter`, `Roboto` |
| a rounded geometric display face | `Chakra Petch`, `Days One`, `Sora` |
| a slab / typewriter face | `Roboto Slab`, `Zilla Slab` |
| Times, Georgia, any serif body | `Source Serif 4`, `Lora` |

If the brand's online manual exists, take its actual `font-family` instead of
guessing.

## Catalog card (root index.html)

```html
<li>
  <a href="<brand>-<model>/">
    <span class="brand">&lt;Brand&gt;</span>
    <span class="model">&lt;Model&gt;</span>
    <span class="type">&lt;filter category, e.g. Dynamics&gt;</span>
    <span class="note">&lt;pedal type, e.g. Compressor&gt;</span>
  </a>
</li>
```
