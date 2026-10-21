#!/usr/bin/env python3
"""Re-apply the small-caps heading repair of the Cosmos Policy decoy to a regenerated text.

The repair maps each heading line as extracted (letter-spaced small caps) to its readable form, taken from the
round-1 decoy text, and joins any remaining 'C OSMOS'-style letter splits in short heading lines.
usage: fix_smallcaps.py raw_old.txt fixed_old.txt new_raw.txt out.txt
"""
import difflib
import re
import sys

raw_old, fixed_old, new_raw, out = sys.argv[1:5]
a = open(raw_old, encoding="utf-8").read().split("\n")
b = open(fixed_old, encoding="utf-8").read().split("\n")
mapping = {}
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if tag == "replace" and i2 - i1 == j2 - j1:
        for k in range(i2 - i1):
            mapping[a[i1 + k]] = b[j1 + k]
lines = open(new_raw, encoding="utf-8").read().split("\n")
res = []
for line in lines:
    if line in mapping:
        res.append(mapping[line])
    elif len(line) < 160 and re.search(r"\b[A-Z] [A-Z]{2,}", line):
        res.append(re.sub(r"\b([A-Z]) ([A-Z]{2,})", r"\1\2", line))
    else:
        res.append(line)
open(out, "w", encoding="utf-8").write("\n".join(res))
print("mapped", sum(l in mapping for l in lines), "lines")
