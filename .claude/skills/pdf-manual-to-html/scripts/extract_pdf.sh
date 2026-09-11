#!/usr/bin/env bash
# Extract everything needed to rebuild a pedal manual as HTML from one PDF.
# Poppler-only (pdfinfo/pdffonts/pdftotext/pdfimages/pdftoppm) — no install, read-only.
#
# Usage: extract_pdf.sh <manual.pdf> <out_dir>
# Produces in <out_dir>/:
#   info.txt      metadata + embedded font list (font list drives the CSS font choice)
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

pdftotext -layout "$pdf" "$out/text.txt"
# -all keeps each image in its native format, so a cover photo comes out as the
# original JPEG instead of a re-encoded PNG; -p keeps the page number in the name
pdfimages -all -p "$pdf" "$out/raw/img"
pdftoppm -png -r 150 "$pdf" "$out/pages/page"

echo "done -> $out"
ls -R "$out"
