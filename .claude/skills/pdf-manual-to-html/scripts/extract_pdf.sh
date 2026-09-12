#!/usr/bin/env bash
# Extract everything needed to rebuild a pedal manual as HTML from one PDF.
# Poppler (pdfinfo/pdffonts/pdftotext/pdfimages/pdftocairo), plus qpdf and
# python3 for fonts-used.txt — read-only.
#
# Usage: extract_pdf.sh <manual.pdf> <out_dir>
# Produces in <out_dir>/:
#   info.txt      metadata + embedded font list (font list drives the CSS font choice)
#   fonts-used.txt  each embedded face, its CSS weight, and sample text it sets
#   text.txt      layout-preserving text dump (the copy source)
#   raw/          embedded raster images, original resolution and format
#   pages/        full-page renders at 150dpi (visual reference; crop figures from here
#                 when embedded images are sliced, vector, or missing)
set -euo pipefail

pdf=${1:?path to PDF}
out=${2:?output dir}
mkdir -p "$out/raw" "$out/pages"

{
  echo "=== pdfinfo ==="; pdfinfo "$pdf"
  echo; echo "=== pdffonts ==="; pdffonts "$pdf"
} > "$out/info.txt"

if command -v qpdf >/dev/null; then
  python3 "$(dirname "$0")/font_usage.py" "$pdf" > "$out/fonts-used.txt"
else
  echo "qpdf not found (brew install qpdf): fonts-used.txt skipped" >&2
fi
pdftotext -layout "$pdf" "$out/text.txt"
# -all keeps each image in its native format, so a cover photo comes out as the
# original JPEG instead of a re-encoded PNG; -p keeps the page number in the name
pdfimages -all -p "$pdf" "$out/raw/img"
# cairo, not pdftoppm: Splash silently drops some vector art, e.g. the dotted
# rules under the BOSS NS-1X sub-headings
pdftocairo -png -r 150 "$pdf" "$out/pages/page"

echo "done -> $out"
ls -R "$out"
