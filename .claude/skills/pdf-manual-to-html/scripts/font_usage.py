#!/usr/bin/env python3
"""Which embedded face sets which text, and the CSS weight each face maps to.

`pdffonts` only lists the faces; this shows where each one is used, so table
labels, step instructions and run-in heads get the weight the manual gives
them instead of one picked by eye.

Usage: font_usage.py <manual.pdf> [samples per face, default 8]
Needs qpdf. Not pdftohtml: its XML can file text under the wrong face.
Text goes through each font's /ToUnicode CMap, so CID-keyed subsets
(Identity-H) print words too. A face with neither a CMap nor a standard
encoding prints glyph codes instead; its face and weight lines still hold.
"""
import base64
import functools
import json
import re
import subprocess
import sys
from collections import defaultdict

# Checked in order: "SemiBold" and "ExtraBold" must win over "Bold"
WEIGHTS = [
    ("thin|hairline", 100),
    ("extralight|ultralight", 200),
    ("semibold|demibold", 600),
    ("extrabold|ultrabold|heavy", 800),
    ("black", 900),
    ("light", 300),
    ("medium", 500),
    ("bold", 700),
]

TOKEN = re.compile(
    rb"/([^\s/\[\]()<>]+)\s+[-\d.]+\s+Tf"  # font change
    rb"|/([^\s/\[\]()<>]+)\s+Do"  # form XObject
    rb"|\(((?:\\.|[^\\)])*)\)"  # literal string
    rb"|<([0-9A-Fa-f\s]*)>"  # hex string: glyph codes, readable only through a CMap
    rb"|(?<![\w/])(q|Q|ET)(?!\w)",  # graphics state save/restore, end of text
    re.S,
)


def weight(face):
    style = face.split("-", 1)[1] if "-" in face else ""
    for pattern, value in WEIGHTS:
        if re.search(pattern, style, re.I):
            return value
    return 400


pdf = sys.argv[1]
per_face = int(sys.argv[2]) if len(sys.argv) > 2 else 8

doc = json.loads(
    subprocess.run(
        ["qpdf", "--json=2", "--json-stream-data=inline", "--decode-level=generalized", pdf],
        capture_output=True,
        check=True,
    ).stdout
)
objects = doc["qpdf"][1]


def resolve(x):
    if isinstance(x, str) and re.fullmatch(r"\d+ \d+ R", x):
        o = objects["obj:" + x]
        return o["value"] if "value" in o else o["stream"]["dict"]
    return x


def stream(ref):
    return base64.b64decode(objects["obj:" + ref]["stream"].get("data", ""))


ESCAPES = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f", b"\n": b""}


def literal(b):
    """Bytes of a literal string, escapes resolved in one pass."""

    def unescape(m):
        e = m[1]
        return bytes([int(e, 8) & 255]) if e[:1] in b"01234567" else ESCAPES.get(e, e)

    return re.sub(rb"\\([0-7]{1,3}|.)", unescape, b, flags=re.S)


def hexstring(h):
    h = re.sub(rb"\s", b"", h).decode()
    # an odd final digit is padded with 0, as the PDF spec reads it
    return bytes.fromhex(h + "0" * (len(h) % 2))


def utf16(h):
    return bytes.fromhex(h).decode("utf-16-be", "replace")


@functools.lru_cache(None)
def to_unicode(ref):
    """(code width in bytes, code -> text) from a /ToUnicode CMap stream."""
    data = stream(ref).decode("latin-1")
    space = re.search(r"begincodespacerange\s*<([0-9A-Fa-f]+)>", data)
    width = len(space[1]) // 2 if space else 1
    table = {}
    for block in re.findall(r"beginbfchar(.*?)endbfchar", data, re.S):
        for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]*)>", block):
            table[int(src, 16)] = utf16(dst)
    for block in re.findall(r"beginbfrange(.*?)endbfrange", data, re.S):
        ranges = re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]*>|\[[^\]]*\])", block)
        for lo, hi, dst in ranges:
            lo, hi = int(lo, 16), int(hi, 16)
            if dst[0] == "[":
                for code, d in enumerate(re.findall(r"<([0-9A-Fa-f]*)>", dst), lo):
                    table[code] = utf16(d)
            else:
                # the destination counts up with the code
                start, digits = int(dst[1:-1], 16), len(dst) - 2
                for code in range(lo, hi + 1):
                    table[code] = utf16(f"{start + code - lo:0{digits}X}")
    return width, table


def decode(raw, cmap):
    """Text of a string's bytes: through the font's CMap, else as cp1252."""
    if not cmap:
        return raw.decode("cp1252", "replace")
    width, table = cmap
    codes = (raw[i : i + width] for i in range(0, len(raw) - width + 1, width))
    # a one-byte code the CMap leaves out is most likely plain cp1252
    fallback = lambda c: c.decode("cp1252", "replace") if width == 1 else "#"
    return "".join(table.get(int.from_bytes(c, "big"), fallback(c)) for c in codes)


def font_entry(ref):
    font = resolve(ref)
    cmap = font.get("/ToUnicode")
    cmap = to_unicode(cmap) if isinstance(cmap, str) and re.fullmatch(r"\d+ \d+ R", cmap) else None
    # Only Type0 fonts take multi-byte codes; simple fonts are one byte a code
    # even when their CMap declares a <0000> <FFFF> code space, as Roland's do
    if cmap and font.get("/Subtype") != "/Type0":
        cmap = (1, cmap[1])
    return font.get("/BaseFont", "?").split("+")[-1], cmap


def walk(data, resources, page, out, depth=0):
    resources = resolve(resources) or {}
    fonts = {name: font_entry(ref) for name, ref in (resolve(resources.get("/Font", {})) or {}).items()}
    xobjects = resolve(resources.get("/XObject", {})) or {}
    face, cmap, saved, text = None, None, [], ""

    def flush():
        nonlocal text
        # control codes stand in for spaces in some custom encodings
        text = re.sub(r"[\x00-\x1f]", " ", text)
        if face and text.strip():
            out.append((face, page, " ".join(text.split())))
        text = ""

    for m in TOKEN.finditer(data):
        if m[1]:
            flush()
            face, cmap = fonts.get("/" + m[1].decode(), ("?", None))
        elif m[2]:
            ref = xobjects.get("/" + m[2].decode())
            if ref and depth < 5 and resolve(ref).get("/Subtype") == "/Form":
                flush()
                walk(stream(ref), resolve(ref).get("/Resources", resources), page, out, depth + 1)
        # Q restores the font set before the matching q: a face switched on
        # inside q...Q sets nothing after it
        elif m[5] == b"q":
            saved.append((face, cmap))
        elif m[5] == b"Q":
            flush()
            face, cmap = saved.pop() if saved else (face, cmap)
        elif m[5] == b"ET":
            flush()
        elif m[3] is not None:
            text += decode(literal(m[3]), cmap)
        elif m[4] is not None:
            text += decode(hexstring(m[4]), cmap) if cmap else "#"
    flush()


out = []
for n, entry in enumerate(doc["pages"], 1):
    page = resolve(entry["object"])
    # Resources may be inherited from the page tree
    node = page
    while "/Resources" not in node and "/Parent" in node:
        node = resolve(node["/Parent"])
    contents = page.get("/Contents", [])
    contents = contents if isinstance(contents, list) else [contents]
    walk(b"\n".join(stream(c) for c in contents), node.get("/Resources", {}), n, out)

runs, samples = defaultdict(int), defaultdict(dict)
for face, page, text in out:
    runs[face] += 1
    # Words make recognisable samples; a bare glyph only stands in until one turns up
    has_word = re.search(r"[A-Za-z0-9]", text)
    if len(samples[face]) < per_face and (has_word or not samples[face]):
        samples[face].setdefault(text[:70], page)

for face in sorted(runs, key=runs.get, reverse=True):
    print(f"{face}  -> weight {weight(face)}  ({runs[face]} runs)")
    for text, page in samples[face].items():
        print(f"    p.{page}  {text}")
    print()
