#!/usr/bin/env python3
"""Style fingerprints used by the round-1 reviewer, computed on blind texts.

Body = everything before the reference list, tables removed. Reports per-1000-word rates of
semicolons and first-person 'we', and counts of ', not' contrasts, 'never', 'Takeaway',
and other phrases the reviewer flagged.
usage: style_metrics.py file.txt [file2.txt ...]
"""
import re
import sys

FLAGS = ["pending", "Takeaway", "equivalence margin", "crossed bootstrap", "Wilson", "arms",
         "exposure", "unresolved", "native", "program", "never", "exactly", "falsifiable"]


def body(text):
    m = re.search(r"\n(References|REFERENCES|R EFERENCES)\n", text)
    t = text[:m.start()] if m else text
    t = re.sub(r"\[TABLE\].*?\[/TABLE\]", " ", t, flags=re.S)
    return t


def appendix(text):
    """Text after the reference list (supplement), tables removed."""
    m = re.search(r"\n(References|REFERENCES|R EFERENCES)\n", text)
    if not m:
        return ""
    rest = text[m.end():]
    a = re.search(r"\n(A\.? +[A-Z][^\n]{3,80}|Appendix[^\n]{0,80}|APPENDIX[^\n]{0,80})\n", rest)
    t = rest[a.start():] if a else ""
    return re.sub(r"\[TABLE\].*?\[/TABLE\]", " ", t, flags=re.S)


def rates(tag, t):
    words = max(len(t.split()), 1)
    semi = t.count(";")
    we = len(re.findall(r"\b[Ww]e\b", t))
    notx = len(re.findall(r", not\b", t))
    return f"{tag}: words={words} semi/1k={1000 * semi / words:.1f} we/1k={1000 * we / words:.1f} ', not'={notx}"


for path in sys.argv[1:]:
    raw = open(path, encoding="utf-8").read()
    print(path.split('/')[-1], "|", rates("main", body(raw)), "|", rates("appx", appendix(raw)))
    t = body(raw)
    words = len(t.split())
    semi = t.count(";")
    we = len(re.findall(r"\b[Ww]e\b", t))
    notx = len(re.findall(r", not\b", t))
    out = [f"{path.split('/')[-1]}: words={words} semicolons/1k={1000 * semi / words:.1f} we/1k={1000 * we / words:.1f} ', not'={notx}"]
    for f in FLAGS:
        n = len(re.findall(r"\b" + re.escape(f) + r"\w*", raw))
        if n:
            out.append(f"{f}={n}")
    print("  ".join(out))
