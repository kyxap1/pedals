# Reviewer's checklist

Handed to the review subagent in step 7 together with the page, the screenshot
segments, the PDF `pages/` and the survey's section → page map.

The reviewer edits nothing. Each finding is reported as text: section id,
segment file, what the page shows, what the PDF shows. A check that passes is
reported with what it could not see, so a row of green ticks isn't read as
coverage nothing measured.

## Against the source

- Desktop segments against the PDF `pages/`: every section present, figures in
  the right place, nothing garbled.
- Images used where live text or a table should be — a hard fail, not a style
  note. Logotypes are the only figures allowed to carry text.
- Crookedly cropped figures: cut off at the edges, or carrying stray letters
  and rule ends from whatever was printed beside them.
- Text formatting that departs from the original: missing bold or italic,
  wrong heading levels, inconsistent font weights (a web semibold standing in
  for a print bold).
- Missing footnotes or callout boxes.
- Header/masthead position and layout against the cover art, including the
  colour-panel/photo ratio.

## On the page itself

- The menu / TOC: broken anchors, missing items, ordering.
- Columns and lists: crooked or unaligned columns, items pushed into the wrong
  column, a figure separated from the sentence that leads into it.
- Word wraps: orphans, a bare URL breaking the layout.
- Tables: missing or misaligned borders and divider rules, cell alignment.
- Every table and callout cropped out of the desktop shot and set beside the
  same block on the page render, at the same scale, in one `montage` sheet.
- Mobile: the `scrollWidth` line answers horizontal scroll, so look only at the
  first segment (nav gone, mobile TOC shown) and the ones holding wide tables
  or figure grids.
- The palette on both the light surroundings and the reversed-out header.
