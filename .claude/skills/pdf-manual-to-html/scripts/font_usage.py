#!/usr/bin/env python3
"""Which embedded face sets which text, and the CSS weight each face maps to.

`pdffonts` only lists the faces; this shows where each one is used, so table
labels, step instructions and run-in heads get the weight the manual gives
them instead of one picked by eye.

Usage: font_usage.py <manual.pdf> [samples per face, default 8]
Needs qpdf. Not pdftohtml: its XML can file text under the wrong face.
Subsets with a custom encoding print glyph codes instead of words; the face
and weight lines still hold.
"""
import base64
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
    rb"|<([0-9A-Fa-f\s]*)>"  # hex string: CID glyph ids, unreadable
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


def literal(b):
    b = re.sub(rb"\\([0-7]{1,3})", lambda m: bytes([int(m[1], 8) & 255]), b)
    b = re.sub(rb"\\(.)", lambda m: {b"n": b" ", b"r": b" ", b"t": b" "}.get(m[1], m[1]), b, flags=re.S)
    return b.decode("cp1252", "replace")


def walk(data, resources, page, out, depth=0):
    resources = resolve(resources) or {}
    fonts = {
        name: resolve(ref).get("/BaseFont", "?").split("+")[-1]
        for name, ref in (resolve(resources.get("/Font", {})) or {}).items()
    }
    xobjects = resolve(resources.get("/XObject", {})) or {}
    face, saved, text = None, [], ""

    def flush():
        nonlocal text
        if face and text.strip():
            out.append((face, page, " ".join(text.split())))
        text = ""

    for m in TOKEN.finditer(data):
        if m[1]:
            flush()
            face = fonts.get("/" + m[1].decode(), "?")
        elif m[2]:
            ref = xobjects.get("/" + m[2].decode())
            if ref and depth < 5 and resolve(ref).get("/Subtype") == "/Form":
                flush()
                walk(stream(ref), resolve(ref).get("/Resources", resources), page, out, depth + 1)
        # Q restores the font set before the matching q: a face switched on
        # inside q...Q sets nothing after it
        elif m[5] == b"q":
            saved.append(face)
        elif m[5] == b"Q":
            flush()
            face = saved.pop() if saved else face
        elif m[5] == b"ET":
            flush()
        elif m[3] is not None:
            text += literal(m[3])
        elif m[4] is not None:
            text += "#"
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
