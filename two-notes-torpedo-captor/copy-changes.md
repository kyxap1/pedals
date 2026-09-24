# Two notes Torpedo Captor — copy changes

## Sources

- No PDF manual exists: the maker's product page
  (https://www.two-notes.com/en/torpedo-series/torpedo-captor/) links only to the online manual.
- Online manual, read 2026-09-24 at
  https://wiki.two-notes.com/doku.php?id=torpedo_captor:torpedo_captor_user_s_manual
  (DokuWiki page, "Last modified: 2026/01/28"), with its 19 images from the wiki's media store.
  No local copy of the web page is kept.
- Style: the wiki's own CSS (Nunito Sans, #404040 ink, #e1e4e5 hairlines), purple #5a3a8c from the Two notes logo.

## Structure

| Wiki | Page |
|---|---|
| Untitled front matter under the page title | "About this manual" (heading added) |
| h1 per chapter, h2 numbered sections, h3 subsections | h2 / h3 / h4, numbering kept |
| Snake_case anchors (`torpedo_captor_s_advanced_functions`) | kebab-case ids, shortened (`advanced-functions`) |
| Warning tables (icon cell + bold text cell) | `.callout.warn` with the same icon |
| Specs as label: value paragraphs | definition lists, same wording |
| Block diagram note under the image | `figcaption` |
| Using 1. Overview: intro, diagram, warning | intro and warning side by side, the diagram full width under them |

## Changes

| Section | Wiki | Page |
|---|---|---|
| About this manual | "Please refer to the safety instructions" | anchor link to #safety-instructions |
| About this manual, and throughout | `http://` links | `https://` hrefs, printed text kept |
| 1.3 Conditions for safe use | "an amp which RMS power is over" | "an amp whose RMS power is over" |
| 2. Contents of the package | "Torpedo BlendIR softwares are" | "Torpedo BlendIR software, are" |
| 5. Warranty | "repaired or replaced, (at OROSYS SAS’s" | "repaired or replaced (at OROSYS SAS’s" |
| 5. Warranty | "be required, Please contact" | "be required, please contact" |
| 5. Warranty | bold spans with stray inner spaces | trimmed |
| Loadbox 1 | "Most tube amplifiers makers" | "Most tube amplifier makers" |
| Loadbox 2 | "the “sweet spot” - the perfect … - is" | em dashes "—" |
| Loadbox 2 | "may not sound as well as you may hope … sound rather poorly" | "as good as … rather poor" |
| Loadbox 3 | "so called “silent fan”" | "so-called “silent fan”" |
| About 1 | "“load” and record !" | "“load” and record!" |
| About 2 | "A more detailled description" | "A more detailed description"; "later in this manual" linked to #using-the-captor |
| About 2.2 | "a fixed – 20dB attenuation" | "a fixed -20dB attenuation" |
| About 3 | "describes it behavior" | "describes its behavior" |
| About 3 | "the behavior or particular systems" | "the behavior of particular systems" |
| About 4 | "comes with a 16 virtual cabinets" | "comes with 16 virtual cabinets" |
| About 4.1 | "to warm-up the sound" | "to warm up the sound" |
| About 4.2 | "a powerful compressor … dynamics." / "a reverb" | "…dynamics," / "a reverb." |
| About 4.3 | "the full list of parameter, to fine tune" | "the full list of parameters, to fine-tune" |
| Using 3.1 | "this input : it's" | "this input: it's" |
| Using 3.1 | "(ie, if your Captor" | "(i.e., if your Captor" |
| Using 3.1 | "Please refer to the THRU section" | anchor link to #thru-output |
| Using 3.2 | "as a mean to" | "as a means to" |
| Using 3.3 | "a 16 ohms cabinet on a 8 ohms Captor", "a 4 ohms cabinet on a 8 ohms Captor" | "on an 8 ohms Captor" |
| Using 3.4 | "Please refer to the Wall of Sound section" | anchor link to #wall-of-sound |
| Using 3.6 | "you can use a XLR-to-jack cable" | "an XLR-to-jack cable" |
| Setting up | "Please refer to the above description of each feature" | anchor link to #features |
| Setting up 1 | "your amp is miked !", "irrelevant :", "as follow :" | "miked!", "irrelevant:", "as follows:" |
| Setting up 3 | "up to three tracks :" | "up to three tracks:" |
| Setting up 4 | "(ie, the impedance … ) is as follow:" | "(i.e., … ) is as follows:" |
| Setting up 4 | "negligeable" | "negligible" |
| Setting up 4 | "All version will work. We recommand" | "All versions will work. We recommend" |
| Specs 2 | "equiped" (8×) | "equipped" |
| Specs 2 | "Mesa Rectifier 4 x12" | "4×12" |
| Specs 2 | "Friedman® 4×12 Vntage … done infront of the v30’s" | "Vintage … done in front of the V30’s" |
| Specs 2 | "9×10“", "2×12”", "4×6”", "1×15”" | inch mark ″ throughout |
| Specs 3 | "Dynamic microphonee Electrovoice™ RE20" | "Dynamic microphone" |
| Specs 4 | "16 ohms version shows. The 4 and 8 ohms version have" | "16 ohms version shown. The 4 and 8 ohms versions have" |
| Specs 7 | "Guitar : based", "Bass : based" | "Guitar", "Bass" as definition terms |
| Specs 8 | "Voltage : 9 to 24V DC", "Current : 5mA" | definition terms |
| Support | "all sorts of useful informations" | "useful information" |
| 2. E-mail | "at the address above" | anchor link to #technical-support |

## Kept as printed (conflicts and template leftovers)

- Warranty: "OROSYS SARL warrants…" while every other line names OROSYS SAS.
- Declaration of conformity: "Category of product: digital audio signal processor" — the Captor is analog (loadbox, analog speaker sim).
- Contents of the package: "the Torpedo Remote and Torpedo BlendIR software" — the Captor has no Torpedo Remote control; carried over from other Torpedo manuals. Same for "firmware and software updates" under Two notes Website.
- 3.6 Speaker simulation / Specs 7: Bass model "Fridge 8×10", while the Wall of Sound cabinet list names "Fridge 9 … 9×10″" (a different cabinet, not corrected).

## Navigation labels

The side nav shortens five long headings; the headings themselves are verbatim:
"Disposal of waste equipment", "Proper use of a loadbox with a tube amplifier",
"Advanced functions", "Torpedo technology and Wall of Sound",
"Wall of Sound, only a speaker simulation?".
