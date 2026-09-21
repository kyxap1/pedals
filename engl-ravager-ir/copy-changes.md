# ENGL E725 Ravager IR — copy changes

## Source

`E725-OM-2.pdf`, revision `E725-OM-2_2025-05-06`, 10 pages. Downloaded from the
**E725 Ravager IR product page** on the maker's own site,
<https://www.engl-amps.com/shop/heads/e725-ravager-ir/>, which links it as
"English Manual" at
<https://www.engl-amps.com/wp-content/uploads/2025/08/E725-OM-2.pdf>. The copy
the user handed over is byte-identical to that download (`cmp` clean), so there
is no newer revision to fold in. ENGL offers no quick start, addendum, MIDI map
or firmware guide for this model, and publishes no HTML manual; `engl-usa.com`
lists no E725 document at all. The manual names a "separately included
pamphlet, Instructions for the Prevention of Fire, Electrical Shock and Injury"
that ENGL does not publish online.

The page carries the whole manual. Nothing was dropped except the printed runs
of hyphens and underscores that trail each section title — in the PDF those set
as a solid black bar with the title reversed out of it, and the page reproduces
the bar.

## Typographic normalisations, applied throughout

- **Apostrophes.** The manual uses the acute accent `´` as an apostrophe
  everywhere (`amp´s`, `preamp´s`, `Operator´s`, `let´s`, `o´clock`), and a left
  single quote once (p5, `power amp‘s`). All set as `’` on the page — the
  acute accent is not an apostrophe and it breaks search and screen readers.
- **Inch marks.** Printed as an opening double quote (`¼“`, `1/8”`); set as a
  straight `"` on the page.
- **Decimal separators.** The manual mixes the German comma and the point,
  sometimes within one list. Normalised to the point:
  `6,3mm` → `6.3mm` (p2 Input, p5 FX Loop Send, FX Loop Return);
  `3,5mm` → `3.5mm` (p4 Headphone Output);
  `12,00in x 6,51in x 7,67in` → `12.00in x 6.51in x 7.67in` (p6);
  `6,1kg` → `6.1kg` (p6);
  `0,4 A` → `0.4 A`, `0,8 A` → `0.8 A` (p6 Fuses).

## Typos and mangled phrases corrected

| Page | Printed | Page reads |
|---|---|---|
| 3 | `This procedure spares the tubes` (no full stop, sentence just ends) | `This procedure spares the tubes.` |
| 3 | `a built-in ENGL IR (ENGL E412XXL (V30) the other three can be loaded via USB.` — unbalanced parentheses, two clauses run together | `a built-in ENGL IR (ENGL E412XXL, V30); the other three can be loaded via USB.` |
| 3 | `Connect your the amp via a USB-B cable` | `Connect the amp via a USB-B cable` |
| 4 | `NOTE: In case the Irs are to long` | `NOTE: In case the IRs are too long` |
| 4 | `toggle this switch for ground or ground lifted.` — lower-case sentence start | `Toggle this switch for ground or ground lifted.` |
| 5 | `you can use a 8ohm cabinet or a 16ohm cabinet` | `you can use an 8 Ohm cabinet or a 16 Ohm cabinet` |
| 5 | `8 - 16 Ohm jack,` followed by a comma splice | `8 – 16 Ohm jack;` |
| 6 | `Littlefuse - 0218.100HXP` | `Littelfuse – 0218.100HXP` (the manufacturer's own spelling) |
| 6 | `Dimension` | `Dimensions` |
| 7 | `the afore mentioned knobs` | `the aforementioned knobs` |
| 8 | `(infront of the preamp and FX Loop)` | `(in front of the preamp and FX Loop)` |
| 8 | `Use a patch or guitar cable to patch he FX Send` | `…to patch the FX Send` |
| 8 | `are altogehter disconnected` | `are altogether disconnected` |
| 8 | `picking up interferrence from powerful magnetic fields` | `picking up interference from powerful magnetic fields` |
| 8 | `The  amp or speaker cords may be picking up radio signals.` — double space | single space |

## Template leftovers corrected against the panel

The manual is built from an ENGL house template and names controls this
two-channel amp does not have. Every correction below was checked against the
front-panel drawing on PDF page 2 and ENGL's own product photograph: the amp has
**Clean Gain, Lead Gain, Bass, Middle, Treble, Clean Volume, Lead Volume,
Master, a Lead/Clean toggle, Stand By and Power**, and a single Poweramp Output
jack. There is no Crunch channel, no Presence knob, no noise gate and no second
speaker jack.

| Page | Printed | Page reads | Why |
|---|---|---|---|
| 2 | `Press this push button to toggle between the Clean and the Lead channel.` | `Use this switch to toggle between the Clean and the Lead channel.` | The panel drawing and the product photo both show a two-position mini toggle, not a push button. |
| 2 | `This feature can also be controlled via the respective ENGL Z4 (TRS) footswitch connected.` | `This feature can also be controlled via a connected ENGL Z4 (TRS) footswitch.` | Mangled word order. |
| 7 | `This occurs primarily when Crunch and Lead channels (that is, all channels whose preamp is easily overdriven) are activated` | `This occurs primarily when the Lead channel (whose preamp is easily overdriven) is activated` | No Crunch channel; only the Lead channel is a high-gain channel. |
| 7 | bullet `Gain and / or Lead Gain knob past the 12 o´clock position` | `Clean Gain and / or Lead Gain knob past the 12 o’clock position` | No knob is labelled plain "Gain" — the panel prints `Gain` as the bracket under *both* gain knobs. |
| 7 | bullet `Crunch / Lead Volume knob past the 12 o´clock position` | `Clean / Lead Volume knob past the 12 o’clock position` | The volume pair is Clean and Lead. |
| 7 | bullet `Presence knob past the 12 o´clock position` | **dropped** | The E725 has no Presence knob; its EQ is Bass / Middle / Treble. |
| 7 | `by turning the Lead channel Gain knobs down. The same applies to these channel´s Treble and Presence knob settings.` | `by turning the Lead channel Gain knob down. The same applies to that channel’s Treble setting.` | One Lead channel, one Lead Gain knob, no Presence. |
| 7 | `particularly noticeable in high-gain Lead channels. This is because the Lead channels provide a very high gain factor` | `particularly noticeable in the high-gain Lead channel. This is because the Lead channel provides a very high gain factor` | One Lead channel. |
| 8 | `Is at least one speaker connected to the speaker outputs?` | `Is a speaker connected to the speaker output?` | One Poweramp Output jack; page 5 says "One cabinet can be connected". |
| 8 | `Is the power amp activated ( Stand By switch to ON)?` | `Is the power amp activated (Stand By switch out of the Stand By position)?` | No panel position is labelled `ON`; the switch is legended `Stand By` only. Also removes a stray space after `(`. |
| 5 | `when connecting one or more cabinets to your amp` | `when connecting a cabinet to your amp` | The amp takes one cabinet on one jack. |

**Left as printed:** the troubleshooting bullet `Is the Noise Gate activated?
(Relevant only, if the amplifier is equipped with a Noise Gate).` The E725 has
no noise gate, but the manual hedges itself in the same sentence, so the
sentence stands.

## Additions

- **`IR Balanced Output`** (p4) is printed as a heading with no body text at
  all. The page adds one sentence — "The balanced XLR output carrying the signal
  of the selected IR, for a mixing desk or recording interface." — derived from
  the rear-panel drawing, which legends that XLR `IR Balanced Output`. Without
  it the heading is empty to a screen reader and to any text-only consumer.
- **`Service`** (p9) is a block of contact instructions the manual prints with
  no heading at all. The page gives it the heading `Service` so it can be
  linked and cited; no wording was changed.
- **`Front Panel`, `Rear Panel`, `Packaging`** are section titles the page adds.
  Only three sections carry a printed banner (`Technical Data`, `A Few Comments
  on Tube Amplifiers`, `Troubleshooting`); pages 2–5 and 9 run their control
  descriptions with no heading at all. The added titles cut the document at its
  own seams — the two panel drawings and the shipping advice — and use the
  manual's own wording (`Packaging` is a printed run-in head, promoted to a
  section title).
- **ENGL's own product photograph of the head** (`Images/ravager-ir-head.jpg`)
  sits under the masthead. The manual draws the enclosure only as line art, so
  the page adds the photograph; it is ENGL's, taken from the E725 product page.
- The back cover's `www.engl-amps.com` is vector outline art, invisible to text
  extraction; it is re-typed into the footer as a link. The one live link
  annotation in the PDF (`mailto:service@engl-amps.com`, p9) is kept as a
  `mailto:` link, and the printed "ENGL amps website" (p4) and "technical data"
  (p4) cross-references become anchors.

## Run-in heads promoted, no wording changed

Print sets these as bold lead-ins ending in a colon, on their own line, with the
body following. The page promotes them to real headings and drops the colon, so
they can be linked and cited:

| Page | Printed lead-in | Page heading |
|---|---|---|
| 4 | `Supported IR Files:` | `<h4>` Supported IR Files |
| 8 | `The output volume fluctuates or drops:` | `<h3>` The output volume fluctuates or drops |
| 8 | `The amp is not providing a proper output signal / no or low sound is emanating from the speaker:` | `<h3>` same wording, colon dropped |
| 8 | `The speaker is emitting humming noises:` | `<h3>` The speaker is emitting humming noises |

## Layout decisions, no wording changed

- The three `CAUTION!` / `Important Note:` paragraphs take one tinted block with
  a red left rule. In print they are marked by weight alone, and inconsistently:
  the headphone caution is bold end to end, the other two bold only the first
  word. The short lead-ins (`Please note:`, `NOTE:`, `Tip:`, `Ring:`, `Default
  (no footswitch connected):`) stay inline and bold, as printed.
- `Technical Data` is a whitespace-aligned two-column list in print, with no
  rules of any kind. On screen at full width that alignment stops holding, so it
  becomes a real table with hairline rules.
- The `Important: Replace these with fuses of the same type and rating only!`
  line sits inside the Power Tube Fuses block in print. On the page it follows
  the table as a caution, reworded to `Replace the power tube fuses with fuses
  of the same type and rating only!` so it still names what it refers to once
  it is out of the row.
- **Technical Data, Power Tube Fuses.** Print breaks `Recommended:`,
  `Littelfuse - 0218.100HXP` and `Schurter - 0034.3107` onto three lines; the
  page sets the two part numbers on one comma-separated line inside the cell.
