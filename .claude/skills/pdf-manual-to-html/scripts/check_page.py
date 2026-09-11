#!/usr/bin/env python3
"""Check a built manual page: anchors resolve, images exist, Images/ has no strays.

Usage: check_page.py <pedal-dir>/index.html

Broken anchors and missing images are the two failures that survive a visual
check, because a screenshot of the top of the page looks perfect either way.
Unreferenced files are extraction leftovers that would otherwise live in the
repo forever.
"""
import os
import re
import sys

page = sys.argv[1]
root = os.path.dirname(page) or "."
html = open(page, encoding="utf-8").read()

ids = set(re.findall(r'id="([^"]+)"', html))
anchors = set(re.findall(r'href="#([^"]+)"', html))
images = re.findall(r'<img[^>]+src="([^"]+)"', html)

dangling = sorted(anchors - ids)
missing = [s for s in images if not s.startswith(("http:", "https:", "data:"))
           and not os.path.exists(os.path.join(root, s))]

used = {os.path.normpath(s) for s in images}
img_dir = os.path.join(root, "Images")
strays = sorted(
    os.path.join("Images", f)
    for f in os.listdir(img_dir)
    if os.path.normpath(os.path.join("Images", f)) not in used
) if os.path.isdir(img_dir) else []

print(f"sections: {html.count('<section')}  anchors: {len(anchors)}  images: {len(images)}")
print(f"dangling anchors:      {dangling or 'none'}")
print(f"missing images:        {missing or 'none'}")
print(f"unreferenced in Images/: {strays or 'none'}")
sys.exit(1 if dangling or missing or strays else 0)
