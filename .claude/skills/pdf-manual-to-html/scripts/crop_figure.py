#!/usr/bin/env python3
"""Crop a figure off a page render without cutting it, from a rough box.

Usage:
  crop_figure.py <page.png> <out.png> X Y W H [--pad 12] [--tol 40] [--step 8] [--max 240]
  crop_figure.py --check <crop.png> [--tol 40]
  crop_figure.py                                (no arguments: self-test)

A box drawn by eye off a 300 dpi render cuts arrowheads, leader lines and the
tail of a label, and the loss is invisible until the page is next to the PDF.
This takes the rough box and grows only the edges ink crosses, until no stroke
runs off the boundary, then trims the slack back and pads. Growth is capped:
hitting the cap means the figure runs into neighbouring content, and the box
needs a human eye rather than more growth.

Ground is the commonest luminance on the whole render, so light-on-dark line
art works the same way as ink on paper.

--check reports which edges of a finished crop ink runs off — the same test, run
on a crop somebody else made. An edge the figure's own ground fills (a photo, a
tinted panel) is reported separately and is not a failure.
"""
import sys

from PIL import Image

BLEED = 0.6  # an edge this wet is the figure's own ground, not a severed stroke


def ground_level(lum):
    """The page's own background: the commonest luminance across the whole render."""
    hist = lum.histogram()
    return max(range(256), key=lambda v: hist[v])


def ink_mask(im, tol):
    """Everything that differs from the ground — ink on paper, or light art on a dark page.

    Transparent pixels are ground: an RGBA figure flattens to black otherwise,
    and every edge then reads as cut.
    """
    lum = im.convert("L")
    g = ground_level(lum)
    mask = lum.point(lambda v: 255 if abs(v - g) > tol else 0, "L")
    if "A" in im.getbands():
        opaque = im.getchannel("A").point(lambda a: 255 if a > 8 else 0, "L")
        from PIL import ImageChops
        mask = ImageChops.multiply(mask, opaque)
    return mask


def edge_lines(box):
    x0, y0, x1, y1 = box
    return {
        "top": (x0, y0, x1, y0 + 1),
        "bottom": (x0, y1 - 1, x1, y1),
        "left": (x0, y0, x0 + 1, y1),
        "right": (x1 - 1, y0, x1, y1),
    }


def edge_ink(mask, box):
    """Fraction of each border line that carries ink."""
    out = {}
    for name, line in edge_lines(box).items():
        band = mask.crop(line)
        n = band.size[0] * band.size[1]
        out[name] = (sum(band.point(lambda v: 1 if v else 0, "L").getdata()) / n) if n else 0.0
    return out


def cut_edges(mask, box):
    """Which of the box's own border lines carry ink, i.e. where a stroke runs off."""
    return {k: v > 0 for k, v in edge_ink(mask, box).items()}


def grow(mask, box, page, step, cap):
    """Push out every edge ink crosses until the box holds the whole drawing."""
    x0, y0, x1, y1 = box
    pw, ph = page
    grown = 0
    while grown < cap:
        cut = cut_edges(mask, (x0, y0, x1, y1))
        if not any(cut.values()):
            return (x0, y0, x1, y1), grown, False
        moved = False
        if cut["top"] and y0 > 0:
            y0, moved = max(0, y0 - step), True
        if cut["bottom"] and y1 < ph:
            y1, moved = min(ph, y1 + step), True
        if cut["left"] and x0 > 0:
            x0, moved = max(0, x0 - step), True
        if cut["right"] and x1 < pw:
            x1, moved = min(pw, x1 + step), True
        if not moved:  # every cut edge is already at the page border
            return (x0, y0, x1, y1), grown, False
        grown += step
    return (x0, y0, x1, y1), grown, True


def crop(page_im, box, pad=12, tol=40, step=8, cap=240):
    box = tuple(box)
    mask = ink_mask(page_im, tol)
    box, grown, capped = grow(mask, box, page_im.size, step, cap)
    tight = mask.crop(box).getbbox()
    if tight is None:
        raise SystemExit("no ink in the box — wrong page or wrong coordinates")
    x0, y0, x1, y1 = box
    box = (
        max(0, x0 + tight[0] - pad),
        max(0, y0 + tight[1] - pad),
        min(page_im.size[0], x0 + tight[2] + pad),
        min(page_im.size[1], y0 + tight[3] + pad),
    )
    return page_im.crop(box), box, grown, capped


def selftest():
    page = Image.new("RGB", (400, 300), "white")
    page.paste((20, 20, 20), (100, 100, 200, 180))          # the figure
    page.paste((20, 20, 20), (200, 138, 260, 142))          # a leader line running right
    out, box, grown, capped = crop(page, (110, 110, 190, 170), pad=5, step=5)
    assert not capped, "clean art should never hit the cap"
    assert box == (95, 95, 265, 185), box                   # whole figure + leader + pad
    assert out.size == (170, 90), out.size

    dark = Image.new("RGB", (200, 200), (10, 10, 10))       # light-on-dark line art
    dark.paste((240, 240, 240), (60, 60, 140, 140))
    _, dbox, _, _ = crop(dark, (70, 70, 130, 130), pad=4, step=4)
    assert dbox == (56, 56, 144, 144), dbox

    tight = Image.new("RGB", (60, 60), "white")
    tight.paste((0, 0, 0), (0, 20, 60, 30))                 # ink out of both sides
    m = ink_mask(tight, 40)
    cut = cut_edges(m, (0, 0, 60, 60))
    assert cut["left"] and cut["right"] and not cut["top"], cut
    frac = edge_ink(m, (0, 0, 60, 60))
    assert 0 < frac["left"] < BLEED, frac                   # a severed band, not a bleed

    rgba = Image.new("RGBA", (60, 60), (0, 0, 0, 0))        # transparent ground
    rgba.paste((0, 0, 0, 255), (10, 10, 50, 50))
    assert not any(cut_edges(ink_mask(rgba, 40), (0, 0, 60, 60)).values()), "alpha must read as ground"
    print("self-test ok")


def main(argv):
    if not argv:
        return selftest()
    tol = int(_opt(argv, "--tol", 40))
    if argv[0] == "--check":
        im = Image.open(argv[1])
        # keep alpha: a palette or RGBA figure flattened to RGB turns its
        # transparent ground into black ink
        im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
        w, h = im.size
        frac = edge_ink(ink_mask(im, tol), (0, 0, w, h))
        # a stroke running off the edge wets a few percent of that line; a photo or a
        # panel that fills the frame wets all of it and was never a cut
        cut = [f"{e} ({frac[e]:.0%})" for e in frac if 0 < frac[e] < BLEED]
        bleed = [e for e in frac if frac[e] >= BLEED]
        if cut:
            print(f"cut: ink runs off {', '.join(cut)} — the crop is missing part of the drawing")
        if bleed:
            print(f"full-bleed edges (a photo or a filled panel, not a cut): {', '.join(bleed)}")
        if not cut and not bleed:
            print("clear: no ink on any edge")
        return 1 if cut else 0
    page, out = argv[0], argv[1]
    x, y, w, h = (int(v) for v in argv[2:6])
    im = Image.open(page).convert("RGB")
    cropped, box, grown, capped = crop(
        im, (x, y, x + w, y + h),
        pad=int(_opt(argv, "--pad", 12)), tol=tol,
        step=int(_opt(argv, "--step", 8)), cap=int(_opt(argv, "--max", 240)),
    )
    cropped.save(out)
    print(f"{out} {cropped.size[0]}x{cropped.size[1]} box={box} grown={grown}px")
    if capped:
        print("CAPPED: ink still crosses the box at the growth limit — the figure runs "
              "into neighbouring content. Look at it before shipping.")
        return 1
    return 0


def _opt(argv, name, default):
    return argv[argv.index(name) + 1] if name in argv else default


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
