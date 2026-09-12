#!/usr/bin/env python3
"""Isolate an icon cropped from beside text: keep the largest dark shape.

Usage: clean_crop.py <in.png> <out.png>      (no arguments: self-test)

A pictogram printed in a box next to copy (a warning triangle, a jack icon)
drags letters and rule ends into any box that holds all of it. Every
connected non-white shape except the largest is painted white, and the
result is trimmed to that shape plus a 6 px white border. The icon must be
the largest connected shape in the box. Flood-filling from the crop edges
instead erases an icon that touches the edge.
"""
import sys
from collections import deque

from PIL import Image, ImageOps

WHITE = 235  # luminance at or above this counts as paper


def clean(im):
    im = im.convert("RGB")
    lum = im.convert("L").load()
    w, h = im.size
    seen, blobs = set(), []
    for sx in range(w):
        for sy in range(h):
            if (sx, sy) in seen or lum[sx, sy] >= WHITE:
                continue
            blob, q = [], deque([(sx, sy)])
            seen.add((sx, sy))
            while q:
                x, y = q.popleft()
                blob.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and lum[nx, ny] < WHITE:
                        seen.add((nx, ny))
                        q.append((nx, ny))
            blobs.append(blob)
    if not blobs:
        raise SystemExit("no dark pixels in the crop")
    blobs.sort(key=len)
    px = im.load()
    for blob in blobs[:-1]:
        for x, y in blob:
            px[x, y] = (255, 255, 255)
    xs = [x for x, _ in blobs[-1]]
    ys = [y for _, y in blobs[-1]]
    out = im.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))
    return ImageOps.expand(out, border=6, fill="white"), len(blobs) - 1


def selftest():
    im = Image.new("RGB", (100, 60), "white")
    im.paste((0, 0, 0), (0, 10, 40, 50))  # the icon, touching the left edge
    im.paste((0, 0, 0), (70, 20, 74, 30))  # a stray letter
    out, removed = clean(im)
    assert out.size == (40 + 12, 40 + 12), out.size
    assert removed == 1, removed
    print("self-test ok")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        selftest()
    elif len(sys.argv) == 3:
        out, removed = clean(Image.open(sys.argv[1]))
        out.save(sys.argv[2])
        print(f"{sys.argv[2]} {out.size[0]}x{out.size[1]}, shapes removed: {removed}")
    else:
        raise SystemExit(__doc__)
