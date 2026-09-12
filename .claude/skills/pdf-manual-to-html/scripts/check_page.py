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

if len(sys.argv) != 2:
    sys.exit(__doc__.strip())

page = sys.argv[1]
root = os.path.dirname(page) or "."
if not os.path.isfile(page):
    sys.exit(f"no such page: {page}")
html = open(page, encoding="utf-8").read()

# quotes are matched either way: a src='…' the pattern missed would be reported
# as an unreferenced stray instead, which reads as a failure on a correct page
ids = set(re.findall(r'id=["\']([^"\']+)', html))
anchors = set(re.findall(r'href=["\']#([^"\']+)', html))
images = re.findall(r'<(?:img|source)[^>]+src=["\']([^"\']+)', html)
images += re.findall(r'<link[^>]+href=["\']([^"\']+\.(?:svg|png|ico))', html)

# a figure referenced only from the stylesheet still has to exist, and still
# counts as used — otherwise it is reported as a stray and the gate fails
css = os.path.join(root, "style.css")
if os.path.isfile(css):
    images += [u for u in re.findall(r'url\(\s*["\']?([^"\')]+)',
                                     open(css, encoding="utf-8").read())
               if not u.startswith(("http:", "https:", "data:"))]  # not @import

dangling = sorted(anchors - ids)
# site search links hits only to headings with an id, so a section whose id
# sits on the <section> gets no hit of its own
off_heading = re.findall(
    r'<section\b[^>]*\bid=["\']([^"\']+)[^>]*>'
    r'(?:(?!</?section\b|<h[1-6]\b).)*<h[1-6]\b(?![^>]*\bid=)', html, re.S)
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
print(f"section ids off heading: {off_heading or 'none'}")
sys.exit(1 if dangling or missing or strays or off_heading else 0)
