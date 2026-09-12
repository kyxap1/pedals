#!/usr/bin/env python3
"""Shrink a built page's images for the web and tag them for lazy loading.

Usage: optimize_images.py <pedal-dir>

In place, on <pedal-dir>/Images and <pedal-dir>/index.html:
- images wider than MAX_W px are scaled down to it (ImageMagick);
- PNGs are quantised (pngquant) and recompressed (oxipng); JPEGs are
  recompressed at quality 85, progressive, metadata stripped (jpegoptim);
- every <img> gets its width/height, so the layout doesn't jump while images
  arrive, and every <img> after the masthead gets loading="lazy". style.css
  needs `img { height: auto }` so those attributes don't stretch a scaled image.

Lossy by design: the verify screenshots are where a banded gradient or a
fuzzed hairline would show. Safe to re-run after adding or re-cropping a figure.
"""
import os
import re
import subprocess
import sys

from PIL import Image

# ponytail: one cap for every figure, 2x a column-spanning figure at laptop
# width; size per figure from its CSS width if a page ever needs more
MAX_W = 2400

if len(sys.argv) != 2:
    sys.exit(__doc__.strip())
root = sys.argv[1]
page = os.path.join(root, "index.html")
img_dir = os.path.join(root, "Images")


def run(*cmd):
    subprocess.run(cmd, check=True)


before = after = 0
for f in sorted(os.listdir(img_dir)):
    p = os.path.join(img_dir, f)
    ext = f.lower().rsplit(".", 1)[-1]
    if ext not in ("png", "jpg", "jpeg"):
        continue
    before += os.path.getsize(p)
    with Image.open(p) as im:
        wide = im.width > MAX_W
    if wide:
        run("magick", "mogrify", "-resize", f"{MAX_W}x>", p)
    if ext == "png":
        r = subprocess.run(["pngquant", "--force", "--skip-if-larger",
                            "--quality=70-95", "--ext", ".png", p])
        # 98: quantised file would be larger, 99: below the quality floor;
        # either way the original is kept, which is the point
        if r.returncode not in (0, 98, 99):
            sys.exit(f"pngquant failed on {p}")
        run("oxipng", "-q", "-o", "4", "--strip", "safe", p)
    else:
        run("jpegoptim", "-q", "--strip-all", "--all-progressive", "--max=85", p)
    after += os.path.getsize(p)

html = open(page, encoding="utf-8").read()
# the skeleton puts the masthead before the first <section>; its images are
# the first thing on screen, so they load eagerly
first_section = html.find("<section")
changed = 0


def tag(m):
    global changed
    t = m.group(0)
    src = re.search(r'src=["\']([^"\']+)', t)
    if not src or src.group(1).startswith(("http:", "https:", "data:")):
        return t
    add = ""
    if "width=" not in t:
        with Image.open(os.path.join(root, src.group(1))) as im:
            add += f' width="{im.width}" height="{im.height}"'
    if m.start() > first_section and "loading=" not in t:
        add += ' loading="lazy"'
    if add:
        changed += 1
    return re.sub(r"\s*/?>$", lambda e: add + e.group(0), t)


html = re.sub(r"<img\b[^>]*>", tag, html)
open(page, "w", encoding="utf-8").write(html)
print(f"Images/: {before // 1024} KB -> {after // 1024} KB; <img> tags updated: {changed}")

css = os.path.join(root, "style.css")
if os.path.isfile(css) and not re.search(r"height:\s*auto", open(css, encoding="utf-8").read()):
    print("style.css has no `height: auto`: add `img { height: auto }`, or every "
          "image with a CSS width is stretched to its height attribute")
