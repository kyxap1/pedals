#!/usr/bin/env python3
"""Print the dominant colours of an image, as hex, most common first.

Usage: sample_colors.py <image> [<image> ...]

Point it at a page render or an extracted product photo to pull the manual's
real palette instead of eyeballing hex codes: the pedal's enclosure colour
becomes the accent, the cover's ground becomes the dark band.
"""
import sys
from collections import Counter

from PIL import Image

if len(sys.argv) < 2:
    sys.exit(__doc__.strip())

for path in sys.argv[1:]:
    # NEAREST, because the default filter interpolates: it would blend the
    # enclosure into the paper and report a colour the artwork never contained
    im = Image.open(path).convert("RGB").resize((80, 80), Image.Resampling.NEAREST)
    top = Counter(im.getdata()).most_common(6)
    swatches = ", ".join("#%02x%02x%02x (%d)" % (*rgb, n) for rgb, n in top)
    print(f"{path}: {swatches}")
