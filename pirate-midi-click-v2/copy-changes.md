# Pirate MIDI CLiCK v2 — copy changes

## Sources

- `CLiCK User Manual v2.0.0.pdf` — the full manual (31 pp., May 2025), from the maker's CDN:
  https://cdn.prod.website-files.com/6458c9d09841a314da6da587/682ee1f35560ba0f0fd5f784_CLiCK%20User%20Manual%20v2.0.0.pdf
  The maker's manual index (learn.piratemidi.com/downloads/user-manuals) lists only the CLiCK v1 manuals (v1.0, v1.1).
- `web/` — local copy of the online documentation, fetched 2026-09-23 from
  https://docs.piratemidi.com/manuals/click-v2/ (overview, click-examples, click-midi-implementation,
  click-warranty) with its three images. Newer than the PDF (USB Host active from firmware v2.0.5).

The PDF is the base; online-only material is marked `.web-note` on the page.

## Changes

| Section | Print | Page |
|---|---|---|
| Overview | "9v DC connection" | "9V DC connection" (9v/9V unified to 9V throughout) |
| Hardware Layout, item 4 | "auxilliary switch input" | "auxiliary switch input" |
| Hardware Layout, item 8 | "dont’ cover" | "don’t cover" |
| Quick Start 1 | "Connect your CLiCK to your computer via the “Device” USB port always." | "Always connect your CLiCK to your computer via the “Device” USB port." |
| Quick Start 1 | "web editor" | linked to https://edit.piratemidi.com |
| Quick Start 2 | "MacOS" | "macOS" (throughout) |
| Quick Start 2 | "or using a BLE MIDI supported app" | "or a BLE MIDI supported app" |
| Quick Start 2 | "see chapter 9" | anchor link to #wireless-midi |
| 1. RGB LEDs | "More details on each LED mode is given below." | "… are given below." |
| 1. WiFi | "please go to chapter 9" | anchor link to #wifi |
| 1. MIDI In | "the LED flash purple … returns to it’s" | "the LED flashes purple … returns to its" |
| 1. Relay State, Expression | "This mode indicated" | "This mode indicates" |
| 2. Switching Presets | "MIDI implementation chart" | anchor link to #midi-implementation |
| 2. Preset Labels | "transferrable" | "transferable" |
| 3. Relay/Expression Jack | "A 1/4” TRS Jack" | "A 1/4” TRS jack"; "MIDI implementation table" linked |
| 3. TRS MIDI | "Each of the 3.5mm TRS jacks are" | "Each of the 3.5mm TRS jacks is" |
| 4. External MIDI Control | "MIDI Implementation" | anchor link |
| 5. USB | "Mac OS" | "macOS"; "Zoom multistomp" → "Zoom MultiStomp" |
| 5. USB Host (web) | "MIDI controllers etc generally" | "MIDI controllers etc. generally" |
| 5. USB Host (web) | "support@piratemidi.com" on its own line | joined to the sentence with ":", mailto link |
| Tech info | "Metric (110g)" | "Metric (110 g)" |

## Online-only material folded in

- Overview: USB MIDI host (web overview).
- Hardware item 2: "Active from firmware v.2.0.5 …" (web hardware layout).
- 1. Relay State colours (web LED modes).
- 3. USB Host / 9V DC connector notes (web overview of connectors).
- 5. USB Host subsection with its Note and Requirements callouts (web).

## Conflicts left as printed

- USB Host: PDF (hardware item 2, ch. 3, ch. 5) says inactive; web hardware layout says active from
  firmware v2.0.5; the web's own "Firmware Updates" note and "USB Host (future)" in its ch. 4 still say
  it is not supported yet.
- Default MIDI channel: PDF ch. 6 and web ch. 6 say Omni (any channel); web MIDI Implementation says
  channel 1. Both shown.
- What CC 23 saves: PDF ch. 6 and web ch. 6 say relay states; web example 5 says relay and expression.
- Expression preset value: PDF ch. 7 and web ch. 7 say 0-127; web example 2 says 0-100%.
- Aux switch: "double or triple TRS aux switch" (PDF ch. 2) vs "2-button momentary footswitch" (web example 6).

## Changes, chapters 6–12

| Section | Print | Page |
|---|---|---|
| 6. Go to a Preset | "CC’s or PC’s" | "CCs or PCs" |
| 8. Relay Switching | "auxilliary", "refered" | "auxiliary", "referred" |
| 8. Relay Switching | "normally on (N.O.)" | "normally open (N.O.)" (the web prints it this way) |
| 9. BLE macOS | "Audio MIDI Studio app … and CLiCK the MIDI Studio menu bar and choose “Bluetooth Configuration”" | "Audio MIDI Setup app … click the MIDI Studio menu bar and choose “Bluetooth Configuration”." (app name as in the screenshot) |
| 9. Windows | "CLiCK “Start”", "CLiCK “Bluetooth”, CLiCK the CLiCK BLE item" etc. | "click" (find/replace leftover) |
| 9. Windows | "you can see your WIDI device" | "you can see your CLiCK" (CME template leftover) |
| 9. WiFi | "BLE will be deactivate", "confugration" | "deactivated", "configuration" |
| 9. WiFi | "CLiCK Configure WiFi" | "Click Configure WiFi" |
| 10. Factory Reset | "CLiCKing … CLiCKing" | "clicking … clicking" |
| 10. Updating | "www.learn.piratemidi.com/ downloads/firmware-updates" (line break) | joined, linked |
| 10. Entering Update Mode | "support@piratemidi. com" (line break) | joined, mailto link |
| 11. MIDI table | no "Save to Current Preset" row | row CC 23 added from the web table, tagged |
| Examples (web) | "pre-determined states.\" | stray backslash dropped |
| Examples (web) | "possiblity" (×2), "auxilliary", "the expression pedals does" | "possibility", "auxiliary", "the expression pedal does" |
| Examples (web) | "Do this in the Web Editor" | full stop added |
| 12. Support | printed URLs / e-mail | linked |
| PDF table of contents (pp. 3–4) | page numbers | dropped; the side nav replaces it |
| PDF footer "Firmware v2.1.5" on pp. 10–11 | Bridge4 template leftover | not carried over |

## Online-only material, continued

- 9. WiFi: "Edit Saved WiFi Details" callout (web WiFi section).
- Usage Examples: the whole web click-examples page.
- 11. MIDI Implementation: the web's default-channel sentence.

## Online material left out

- Web overview "Firmware Updates" note ("the firmware does not currently support [USB MIDI Host]") —
  contradicts the web's own "Active from firmware v.2.0.5"; not carried over.
