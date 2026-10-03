#!/usr/bin/env python3
"""Find page text that the source PDFs don't contain.

Usage: check_copy.py <pedal-dir>/index.html <manual.pdf> [<other.pdf> …]

Every sentence of every paragraph, list item, heading, caption and table cell
in <main> is looked up in the PDFs' text. A miss is either a logged departure
(copy-changes.md) or a conversion error: a typo introduced, a value changed,
a heading or caption invented. Matching ignores case, spacing, punctuation
and line-end hyphenation, so wrapped and re-flowed text still matches. A table
cell also passes when its words come in order within a few words of each
other, so a dropped word in a cell can slip through.

What it cannot see: order, which row a cell sits in, formatting, and text
under 4 letters (counted, not checked) — those stay with the reviewer.
"""
import re
import subprocess
import sys
import unicodedata
from html.parser import HTMLParser

if len(sys.argv) < 3:
    sys.exit(__doc__.strip())

BLOCKS = {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
          "figcaption", "caption", "dt", "dd"}
SKIP = {"nav", "script", "style"}


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[^0-9a-z]", "", s)


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = 0
        self.skip = 0
        self.skip_tag = None
        self.stack = []
        self.section = "-"
        self.out = []

    def handle_starttag(self, tag, attrs):
        # a <br> separates lines the PDF may set apart, e.g. a stacked header
        if tag == "br" and self.stack:
            self.stack[-1][1].append("\0")
        if tag == "main":
            self.in_main += 1
        if self.skip and tag == self.skip_tag:
            self.skip += 1
        elif not self.skip and (tag in SKIP or dict(attrs).get("id") == "toc-mobile"):
            self.skip, self.skip_tag = 1, tag
        if tag in BLOCKS:
            if tag[0] == "h" and dict(attrs).get("id"):
                self.section = dict(attrs)["id"]
            self.stack.append((tag, []))

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main -= 1
        if self.skip and tag == self.skip_tag:
            self.skip -= 1
        # an implicitly closed <p> or <td> is closed by its parent's end tag
        while tag in BLOCKS and any(name == tag for name, _ in self.stack):
            name, parts = self.stack.pop()
            if self.in_main and not self.skip:
                for line in "".join(parts).split("\0"):
                    text = " ".join(line.split())
                    if text:
                        self.out.append((self.section, name, text))
            if name == tag:
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1][1].append(data)


page = sys.argv[1]
parser = Blocks()
parser.feed(open(page, encoding="utf-8").read())

# both reading orders: plain keeps a wrapped sentence together, -layout keeps
# a table row together
raw = ""
for pdf in sys.argv[2:]:
    for mode in ([], ["-layout"]):
        raw += subprocess.run(["pdftotext", *mode, pdf, "-"], capture_output=True,
                              text=True, check=True).stdout
source = norm(raw)
words = [norm(w) for w in raw.split()]
where = {}
for i, w in enumerate(words):
    where.setdefault(w, []).append(i)


def in_order(sentence):
    """Words in order within a tight window. Only for table cells, which wrap
    and get interleaved with their neighbours' lines in both reading orders;
    in prose it would pass a dropped word."""
    ws = [norm(w) for w in sentence.split() if norm(w)]
    limit = len(ws) + 8
    for start in where.get(ws[0], []):
        i = start
        for w in ws[1:]:
            i = next((j for j in where.get(w, []) if i < j <= start + limit), None)
            if i is None:
                break
        else:
            return True
    return False


misses, short = [], 0
for section, tag, text in parser.out:
    for sentence in re.split(r"(?<=[.!?:])\s+", text):
        key = norm(sentence)
        if len(key) < 4:
            short += bool(key)
        elif key not in source and not (tag in ("td", "th") and in_order(sentence)):
            misses.append(f"{section} <{tag}>: {sentence[:120]}")

print("\n".join(misses))
print(f"{len(misses)} not in the PDFs; {short} fragments under 4 letters not checked")
sys.exit(1 if misses else 0)
