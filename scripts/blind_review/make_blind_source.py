#!/usr/bin/env python3
"""Make a blind-review build copy of the manuscript (never written back to the repository).

- camera-ready CVPR style (no line numbers, no review banner), no author line;
- numeric fill-ins become [MASK]; proposed configuration values and expected-outcome
  phrases print as plain text (the reviewer sees what a finished paper would state);
- result cells print their width template (e.g. 00.0), which the converter masks exactly
  like the numeric cells of every other paper;
- figure placeholders become blank space of the same height (captions stay);
- notes addressed to the authors are removed.

usage: make_blind_source.py <repo> <out_dir>
"""
import re
import shutil
import sys
from pathlib import Path

NUMERIC = re.compile(r"^\s*(\$\\pm\$)?\s*(X+(\.X+)?|X\.XX|N|K|XX|\[a, b\]|X(, X)+|values|name|category)\s*$")
EMPTY = {"confirm"}


# Named fill-ins print a plausible name in the blind build only (the repository keeps the placeholder).
NAMES = {
    "name of the strongest baseline": "DynamicWAM",
    "name of the strongest +SE(3) baseline": "DynamicWAM + SE(3)",
    "name of the strongest paused baseline": "DreamVLA",
    "name of the strongest DOMINO baseline": "PUMA",
}


def fillin_replacement(content):
    c = " ".join(content.split())
    if c in EMPTY:
        return ""
    if c in NAMES:
        return NAMES[c]
    if NUMERIC.match(c):
        return "\\textnormal{[MASK]}"
    c = re.sub(r"^e\.g\.,\s*", "", c)
    return c


def rewrite_fillins(text):
    out, i = [], 0
    while True:
        j = text.find("\\fillin{", i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        k = j + len("\\fillin{")
        depth, m = 1, k
        while depth:
            if text[m] == "{":
                depth += 1
            elif text[m] == "}":
                depth -= 1
            m += 1
        out.append(fillin_replacement(text[k:m - 1]))
        i = m
    return "".join(out)


def main(repo, out):
    repo, out = Path(repo), Path(out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(repo, out, ignore=shutil.ignore_patterns(
        "*.aux", "*.log", "*.fls", "*.fdb_latexmk", "*.out", "*.bbl", "*.blg", "*.brf",
        "*.xdv", "*.synctex.gz", "local_private", ".git", "tmp", "zhtest*", "*.pdf.bak"))
    pre = out / "preamble.tex"
    s = pre.read_text(encoding="utf-8")
    s = s.replace("\\usepackage[review]{cvpr}", "\\usepackage[pagenumbers]{cvpr}")
    s = s.replace(
        "\\newcommand{\\resultplaceholder}[1][00.0]{\\textcolor{fillcolor}{%\n  \\ooalign{\\hphantom{#1}\\cr\\hidewidth\\textemdash\\hidewidth\\cr}}}",
        "\\newcommand{\\resultplaceholder}[1][00.0]{#1}")
    s = re.sub(r"\\newcommand\{\\figplaceholder\}\[4\]\[1\.6in\]\{%.*?\\end\{minipage\}\}\}",
               lambda m: "\\newcommand{\\figplaceholder}[4][1.6in]{\\rule{0pt}{#1}}", s, flags=re.S)
    assert "\\rule{0pt}{#1}" in s and "{#1}}" in s, "placeholder macros not rewritten"
    pre.write_text(s, encoding="utf-8")
    for tex in list(out.rglob("*.tex")):
        if tex.parts[-2] == "zh" or "zh" in tex.relative_to(out).parts:
            continue
        t = tex.read_text(encoding="utf-8")
        t2 = rewrite_fillins(t)
        t2 = t2.replace("\\author{Anonymous Authors}", "\\author{}")
        t2 = re.sub(r"Colored dashes and bracketed entries denote values pending the\s*\n?final runs\.",
                    "", t2)
        if t2 != t:
            tex.write_text(t2, encoding="utf-8")
    cfg = out / "paper_config.tex"
    c = cfg.read_text(encoding="utf-8")
    cfg.write_text(c, encoding="utf-8")
    print("blind source written to", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
