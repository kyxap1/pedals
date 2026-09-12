#!/usr/bin/env bash
# Report the tools this skill runs that aren't installed, with the command
# that installs them. Exit 1 when anything is missing.
#
# Usage: check_tools.sh

status=0
pkgs=()
need() { command -v "$1" >/dev/null || { pkgs+=("$2"); status=1; }; }

need pdftocairo poppler
need qpdf qpdf
need montage imagemagick
need pngquant pngquant
need oxipng oxipng
need jpegoptim jpegoptim
need node node

if ! python3 -c 'import PIL' 2>/dev/null; then
  echo "missing: Pillow — python3 -m pip install pillow"; status=1
fi
# same path screenshot.mjs launches
if [ ! -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  echo "missing: Google Chrome — brew install --cask google-chrome"; status=1
fi
if [ ${#pkgs[@]} -gt 0 ]; then
  echo "missing: brew install ${pkgs[*]}"
fi
[ $status = 0 ] && echo "all tools present"
exit $status
