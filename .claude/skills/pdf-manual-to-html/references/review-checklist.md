# Reviewer's checklist

Handed to each review subagent in step 7 together with its group of
sections, their PDF page indexes and screenshot segments, the page,
`copy-changes.md`, the `check_copy.py` output and its progress file.

The reviewer edits nothing but its progress file. Each finding is reported as
text: section id, segment file, what the page shows, what the PDF shows. A
check that passes is reported with what it could not see, so a row of green
ticks isn't read as coverage nothing measured.

## How to work

Every image you read is re-sent on every later call of your run, so a long
run gets expensive fast. None of this narrows what you check:

- **Your sections only, in order, once.** After each section, mark its line
  in your progress file `done` and write its findings under it before moving
  on. If an image you read earlier is no longer in your context, its verdict
  is in the progress file: reopen it only for a question still open, not to
  review the section again.
- **Look at what needs eyes.** `check_copy.py` has already compared the copy
  and table cells with the PDF text; its misses that aren't in
  `copy-changes.md` are findings. Spend your looks on what text can't
  show: layout, figures, formatting, tables' structure, the masthead.
- **Sheets first.** Set a section's segments and its PDF pages side by side
  in a `montage` sheet; open a full image only where the sheet is too small
  to answer, cropped to that region.
- **Use what you were given.** Don't shoot new screenshots — name a missing
  width in the report. Weights are in the extract's `fonts-used.txt`; read
  it, don't re-run the extraction. The skill, memory and other pedals'
  pages are outside the review.
- **Safety stop.** If you reach the image budget at the top of your progress
  file with sections still `todo`, hand back what you have: the findings are in the progress file, and a new
  reviewer takes the remaining lines. Either way, end the report with how
  many images you read.

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
