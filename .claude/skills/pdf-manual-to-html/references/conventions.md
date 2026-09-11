# Conventions & patterns

Everything here is distilled from `wampler-terraform/` in this repo. When in
doubt, open that page and copy what it does.

## Repo layout

```
pedals/
  index.html                 root catalog — grid of pedal cards
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
- The root `index.html` is hand-maintained; just add a `<li>` card.

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
      <section id="welcome">
        <div class="flex-container">
          <div class="half-container flow">
            <header><h2 id="intro">Welcome</h2></header>
            <p>…</p>
          </div>
          <div id="toc-mobile" class="half-container">
            <h2>Contents</h2>
            <!-- same links as the side nav, shown only below 900px -->
          </div>
        </div>
      </section>
      <!-- more <section id="…"> … -->
    </main>
    <footer>…</footer>
  </body>
</html>
```

## CSS pattern

Start `style.css` with the design tokens so the palette is swappable:

```css
/* Fonts: <PDF font>  -> <web font chosen>, ... (record the mapping) */
@import url("https://fonts.googleapis.com/css2?family=…&display=swap");

:root {
  --ink:      #1c0d43;  /* body text */
  --accent:   #0f062b;  /* reversed-out headers, rules, table header bg */
  --paper:    #f3f1fa;  /* tint block behind callouts / cards */
}
```

Layout rules that make the reference page work:

| Selector | Purpose |
|---|---|
| `#side-nav` | `position: fixed; width: 20vw; height: 100%` — the desktop TOC |
| `main` | `margin-left: 20vw` to clear the fixed nav |
| `.flex-container` | `display: flex; padding-left: 2em` — section body; never size it in `vw`, it lives inside a `main` already inset by the nav |
| `.half-container` | `width: 100%; padding: 0 1em` — a column inside the flex row |
| `.half-container` (measure) | `columns: 2 30em; column-gap: 3em` — see "Sizing the measure" |
| `.half-container > header` | `column-span: all` — the title rules across the section |
| `section + section` | `margin-top: 3em` — keeps sections from running together |
| `.flow > * + *` | `margin-bottom: 1em` — vertical rhythm without touching every element |
| `.grid-wrapper` | `column-span: all; display: grid; grid-template-columns: repeat(auto-fit, minmax(12em, 18em))` — figure shots across the section, never upscaled past their native size |
| `img` | `width: 100%; margin-bottom: 0.75em` |
| `h2` | reversed out: `color: #fff; background: var(--accent); text-transform: uppercase; padding: 0.25em` |
| `h3` | `text-transform: uppercase; text-decoration: underline` |
| `#side-nav a` | `color: inherit` — a global `a { color: var(--accent) }` otherwise paints the whole TOC in the accent |

Responsive — a single breakpoint:

```css
@media (max-width: 900px) {
  .flex-container { flex-direction: column; }
  .half-container { width: 100%; padding: 0; }
  nav { display: none; }
  main { margin: 0 auto; }
  #toc-mobile { display: block; }
}
/* 901, not 900: both queries match at exactly 900px, and the later one would
   hide the mobile TOC on the same width that hides the nav — no TOC at all */
@media (min-width: 901px) { #toc-mobile { display: none; } }
```

Adjust the *values* (fonts, colours, whether h2 is reversed-out or just ruled) to
the manual being converted. Keep the *structure*.

## Sizing the measure

A section body that inherits the full window sets text 160+ characters wide,
which is where a page stops being readable — the eye misses the start of the
next line and re-reads. But the fix is not a fixed `max-width`: that leaves a
narrow strip of text with a dead gutter beside it, which reads worse than the
long lines did. The measure has to come *from* the window.

```css
.half-container {
  columns: 2 30em;      /* at most two columns, one below ~63em of room */
  column-gap: 3em;
}
.half-container > header { column-span: all; }
```

`columns` with both a count and a width is the whole mechanism: the width
decides how many columns actually fit, the count caps it at two, and the columns
then stretch to fill whatever is there. The window widens, the columns widen;
the window narrows past two columns' worth, it becomes one. No breakpoint, no
fixed strip of text, no empty right-hand half.

Multi-column, not a grid: a grid's rows are as tall as their tallest cell, so
one long knob description leaves a hole under every short one beside it, and
manual sections are never evenly sized. Multi-column balances the column heights
itself and lets a long paragraph split across the gutter, which is what keeps
them even.

Things that shouldn't live inside one column get `column-span: all` — the
section title, a figure grid, a wide table.

**Controlling Column Breaks & Logical Blocks:**
- When using multi-column layout, the browser will balance content by splitting it arbitrarily. To prevent related text from breaking in half, you **must wrap logical blocks** (e.g., an `h3` plus its following paragraphs, a FAQ question plus its answer) in a `<div class="keep-together">` wrapper.
- List items should never split in half. Add `li { break-inside: avoid; }` to the stylesheet. Do *not* restrict the entire `ul` or `ol` though, as long lists should be allowed to flow across multiple columns.
- Sub-headings should receive `break-after: avoid` so they never sit alone at the foot of a column.

```css
.keep-together { break-inside: avoid; }
li { break-inside: avoid; }
h3, h4, h5, h6 { break-after: avoid; }
```

**Disabling Columns for Short Sections:**
If a section contains very little text (e.g., under 10–14 lines like an "About this manual" or "Support" blurb), multi-column balancing will awkwardly split the single paragraph in half or create a tiny isolated column. For these short sections, explicitly disable columns so the text flows naturally at full width:

```html
<div class="half-container no-columns">...</div>
```
```css
.no-columns { columns: auto !important; }
```

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

   It names each source PDF (link to the maker's URL when known, else the local
   file) and says in one or two sentences what changed.
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
.doc-table th { background: var(--accent); color: #fff; text-transform: uppercase; }
.table-scroll { overflow-x: auto; }
```

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
    <span class="note">&lt;pedal type, e.g. Compressor&gt;</span>
  </a>
</li>
```
