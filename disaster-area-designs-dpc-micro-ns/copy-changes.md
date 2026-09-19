# Copy changes — Disaster Area Designs DPC.micro NS

## Sources

| File | Role | Where it came from |
|---|---|---|
| `DPC.micro+NS+manual.pdf` | full manual, the base page | Handed over by the user. Byte-identical (md5 `7a67c0a9325a93c9c861c2024ab9db76`) to `https://www.disasterareadesigns.com/s/DPCmicro-NS-manual.pdf`, linked from the maker's support page. Printed `v1.00 11/11/2019`; PDF CreationDate is 2020-12-16. |
| `DAD-firmware-update.pdf` | generic firmware procedure, folded in as the "Installing Firmware" appendix | `https://www.disasterareadesigns.com/s/DAD-firmware-update.pdf`, listed on the support page under Firmware Update Utilities. Not model-specific, but its Table 2 names the DPC.micro NS explicitly, and the manual has no firmware section at all. |

`www.disasterareaamps.com` — the domain printed on older Disaster Area material —
is a stale "coming soon" page; the live site is `disasterareadesigns.com`. The
maker's DPC.micro product page (`/shop/p/dpc-micro`) now sells the Gen4 and links
no manual; the support page is the only provenance for the PDF. The maker
publishes no HTML online manual, and there is no same-brand page in this repo, so
the style was derived from the PDF itself.

Not used, downloaded only to audit footswitch-variant leftovers:
`https://www.disasterareadesigns.com/s/DPCmicro-manual.pdf` (the footswitch
variant's manual, `v1.00 11/04/2019`).

## Template leftovers corrected

The NS has no footswitches — one LOOP SEL (SAVE) button on the side of the
enclosure and three LEDs on the lid. The manual is an edit of the footswitch
version's and still carries its wording in three places.

| Section | Printed | On the page |
|---|---|---|
| Introduction | "Each loop may be individually controlled using **the footswitches on the DPC.micro** or by MIDI remote control." | "…using **the button on the DPC.micro** or by MIDI remote control." |
| Loop Selection | "The loop states are indicated by the LED **next to each footswitch**." | "The loop states are indicated by the LED **for each loop**." |
| MIDI Control | "To edit, use **the Loop mode** on the DPC.micro to change the loop assignments and then hold **the C (SAVE) footswitch**." | "To edit, **tap the LOOP SEL switch** on the DPC.micro to change the loop assignments and then hold **the LOOP SEL / SAVE switch**." The NS dropped the footswitch version's LOOP and PRESET modes; the save gesture is the one the Saving a Preset section already gives. |

## Typos and grammar fixed

| Section | Printed | On the page |
|---|---|---|
| Configuration | "power on the DPC.micro and then hold LOOP SEL switch" | "…and then hold **the** LOOP SEL switch" |
| MIDI Control | "from your controller on the DPC.micro MIDI channel" | "…on the **DPC.micro's** MIDI channel" (the footswitch manual prints the apostrophe-s) |
| MIDI Control | "program changes 0-119", "a value from 0-63", "64-127" | en dashes: "0–119", "0–63", "64–127" |
| Installing Firmware, step 11 | "Uploading - do not unplug the pedal…" | em dash: "Uploading — do not unplug the pedal…" |

## Print references turned into links

| Section | Printed | On the page |
|---|---|---|
| Controlling Your Pedals | "Please consult the MIDI Control section **on the next page** for full details." | "Please consult the [MIDI Control](#midi-control) section **below** for full details." |
| Installing Firmware, §4 | "Find the control for your product **in Table 2**." | "Find the control for your product **in the table below**." (the table is directly under the step; the source's numbered captions are not reproduced as running heads) |
| Installing Firmware | "do section 4 again", "Do section 6.1", "section 5" — plain text throughout §4, §5 and Table 3 | anchored to the matching heading |

## Structure

- **Loop Selection Order** is a real `<table>`. The print carries the LED state in
  vector circles only — nothing survives `pdftotext` — so each cell is a CSS
  circle plus a visually-hidden state word ("off" / "red" / "green" / "blue").
  A header row (`C` / `B` / `A` / `Loops active`) was **added**; the print has
  none. The circles run C, B, A left to right, as on the lid — note the print
  labels the same row "A & B & C", i.e. the label order is the reverse of the
  circle order.
- The print sets the eight rows as two side-by-side blocks of four; the page runs
  them as one eight-row table in the same sequence.
- **MIDI program changes 120–127** are set in print as two columns of four
  colon-separated lines; the page makes them a two-column table (`PC` /
  `Loops active`). The header row is added.
- **Colour words** — `RED`, `GREEN`, `BLUE`, `ORANGE`, and the `0 (RED)` …
  `3 (ORG)` table header — are printed in the colour they name. The page keeps
  that, but darkens green, blue and orange for text so they pass on white
  (`#2c7a28`, `#0077a8`, `#9a6100`); the LED circles keep the panel values
  (`#d22027`, `#41b23b`, `#00adef`, `#f9a72b`).
- **Figure 1 of the firmware PDF is dropped.** It is a screenshot of the
  application showing the same Product/Control table that is printed as live
  Table 2 immediately above it; shipping it would be a table as an image. The
  five surviving figures are renumbered 1–5, so the first figure a reader meets
  is not captioned "Figure 2".
- **`CONFIGURATION MENU` and `FACTORY RESET:` are both `<h3>`.** In print both
  are the same run-in treatment — MyriadPro-Bold at body size, no rule — not
  headings at all. The page promotes both so the reader can jump to them, and
  ranks them equally because the print does.
- **Masthead order.** The cover runs title, subtitle, photo, `user manual`,
  chevron stripes with the oval logo, version. The page hoists the logo above
  the title so the page opens on a labelled wordmark, and drops the chevron
  stripes as print furniture; the rest keeps the cover's order and its near-equal
  sizing of the title and `user manual`.
- **Firmware Table 2** is reproduced in full, including the seven rows for other
  Disaster Area products. The DPC.micro NS row is called out in the banner above
  the appendix instead of being emphasised inside the table.
- The §6.2 heading keeps the print's straight quotes around
  "Windows protected your PC".
- The firmware PDF's section 5 restarts its visible numbering after each figure;
  the page runs one continuous `<ol>` of 15 steps, which is what the document's
  own cross-references ("step 14 before step 15") assume.
- Figure labels (`DC 9V`, `LOOP SEND`, `USB MIDI`, `LOOP A/B/C`, `MIDI THRU`, the
  `HOLD` arrow, `C LED FLASHES`, `HOLD TO SET POP STOP`, `TAP TO SET MIDI CHAIN`)
  are rasterised or vector pointer labels inside their drawings and stay in the
  figures; each figure's `alt` text lists them.
- The Configuration figure is cropped from a 300 dpi render, not lifted from
  `raw/`: the embedded image shows the normal LED states, while the flashing-red
  starburst on LED C and the darkened LED B that the section describes are vector
  overlays drawn on top in the PDF.

## Conflicts left as printed

- **Hold LOOP SEL, two outcomes.** In configuration mode, "Hold the LOOP SEL
  switch to set the automatic pop reduction" and "hold down the LOOP SEL switch
  for 5 seconds to clear all preset data and configuration" describe the same
  gesture in the same mode, separated only by duration. The manual never
  reconciles them; both are on the page as printed.
- **Factory defaults name settings the NS cannot reach.** "The factory default
  settings are MIDI channel 16, Chain ID 0, Pop reduction OFF, RED / GREEN / BLUE
  LEDs, Brightness 4." The NS config menu offers only Chain ID and pop reduction —
  LED colour and brightness lived in the footswitch version's display menu, which
  the NS dropped. Kept as printed: it is a true statement of the defaults.
- **"DPC.micro NS" vs "DPC.micro".** The cover and a few sentences say NS, the
  rest of the body says plain DPC.micro, sometimes both in one paragraph. Not
  normalised.
- **Version vs file date.** The manual prints `v1.00 11/11/2019`; the PDF was
  produced 2020-12-16. The printed version is what the masthead shows.
