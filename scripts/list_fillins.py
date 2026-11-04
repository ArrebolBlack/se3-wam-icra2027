"""List every placeholder the authors still have to fill in the v2 manuscript.

Usage: python scripts/list_fillins.py [--zh] [--markdown PATH]

Reports, in reading order, each \\fillin{...} in the abstract, main sections, and
supplement (file, line, the bracketed hint, the words just before it, and the outcome
switch branch it belongs to, if any), each figure placeholder, and the number of pending
table cells (\\resultplaceholder) per table. Fill-ins inside a branch that the current
paper_config.tex does not select do not appear in the PDF; fill them before switching.
With --zh the Chinese mirror (zh/) is scanned instead. The same placeholders are counted
by scripts/check_build.py, which fails on them in --final mode.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from check_build import APPENDICES, SECTIONS
from common import REPO

FILLIN = re.compile(r"\\fillin\{((?:[^{}]|\{[^{}]*\})*)\}")
FIGURE = re.compile(r"\\figplaceholder(?:\[[^\]]*\])?\{[^{}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}")
TABLE = re.compile(r"\\input\{tables/([^}]+)\}")
COMMENT = re.compile(r"(?<!\\)%.*$", re.MULTILINE)
# Outcome switches: \Qtwo{n}{...} and \QtwoSel{case 1}{case 2}{case 3}; likewise Qthree, Bbone.
SWITCH = re.compile(r"\\(Qtwo|Qthree|Bbone)(Sel)?(?![A-Za-z])")
SWITCH_NAMES = {"Qtwo": "Q2", "Qthree": "Q3", "Bbone": "BB"}
SELECT_ARITY = {"Qtwo": 3, "Qthree": 3, "Bbone": 2}
CONTEXT_MACROS = {r"\ours": "FoveaWAM", r"\bench": "OnTimeBench", r"\se": "SE(3)", r"\so": "SO(3)"}


def sources(chinese: bool) -> list[Path]:
    base = REPO / "zh" if chinese else REPO
    files = [REPO / ("manuscript_zh.tex" if chinese else "main.tex")]
    files += [base / "sections" / f"{name}.tex" for name in SECTIONS + ("llm_usage",)]
    files += [base / "appendix" / f"{name}.tex" for name in APPENDICES]
    ordered = []
    for path in files:
        if not path.is_file():
            continue
        ordered.append(path)
        # Figure projects follow the section that includes them; archives are not scanned.
        body = COMMENT.sub("", path.read_text(encoding="utf-8"))
        for source in re.findall(r"\\input\{(figures/Fig\d+/figure(?:_zh)?)\}", body):
            ordered.append(REPO / f"{source}.tex")
    return ordered


def group_end(text: str, start: int) -> int:
    """Index just past the brace group that opens at text[start] == '{'."""
    depth, i = 0, start
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def branches(text: str) -> list[tuple[int, int, str]]:
    """(start, end, label) for every outcome-switch branch, e.g. (120, 380, 'Q3=2')."""
    spans = []
    for match in SWITCH.finditer(text):
        name, select = SWITCH_NAMES[match.group(1)], match.group(2)
        i = match.end()
        if select:
            for case in range(1, SELECT_ARITY[match.group(1)] + 1):
                while i < len(text) and text[i].isspace():
                    i += 1
                if i >= len(text) or text[i] != "{":
                    break
                end = group_end(text, i)
                spans.append((i, end, f"{name}={case}"))
                i = end
        else:
            number = re.match(r"\{(\d)\}", text[i:])
            if number:
                i += number.end()
                if i < len(text) and text[i] == "{":
                    spans.append((i, group_end(text, i), f"{name}={number.group(1)}"))
    return spans


def context(text: str, position: int, width: int = 64) -> str:
    """The words just before a fill-in, with LaTeX markup reduced to plain text."""
    before = text[max(0, position - 4 * width):position]
    before = FILLIN.sub(lambda m: f"[{m.group(1)}]", before)
    for macro, word in CONTEXT_MACROS.items():
        before = re.sub(re.escape(macro) + r"(?![A-Za-z])", word, before)
    before = re.sub(r"\\(?:cite[pt]?|label|ref|eqref|appref|mainref)\{[^}]*\}", "", before)
    before = re.sub(r"\\[A-Za-z]+\*?", " ", before)
    before = re.sub(r"[{}~$\\]", " ", before)
    before = " ".join(before.split())
    return ("…" + before[-width:]) if len(before) > width else before


def scan(chinese: bool):
    fillins, figures, tables = [], [], []
    for path in sources(chinese):
        text = COMMENT.sub("", path.read_text(encoding="utf-8"))
        name = path.relative_to(REPO).as_posix()
        spans = branches(text)
        for match in FILLIN.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            labels = sorted({label for start, end, label in spans if start < match.start() < end})
            hint = " ".join(match.group(1).split())
            fillins.append((name, line, hint, context(text, match.start()), ", ".join(labels) or "all"))
        for match in FIGURE.finditer(text):
            figures.append((name, text.count("\n", 0, match.start()) + 1, match.group(1)))
        for match in TABLE.finditer(text):
            table = REPO / "tables" / f"{match.group(1)}.tex"
            if table.is_file():
                body = table.read_text(encoding="utf-8")
                cells = body.count(r"\resultplaceholder")
                hints = len(FILLIN.findall(body))
                if cells or hints:
                    tables.append((match.group(1), name, cells, hints))
    return fillins, figures, tables


def render(fillins, figures, tables) -> str:
    out = ["# Placeholders to fill", ""]
    out.append(f"Text fill-ins: {len(fillins)}; figure placeholders: {len(figures)}; "
               f"tables with pending cells: {len(tables)} "
               f"({sum(t[2] for t in tables)} cells).")
    out.append("")
    out.append("Branch `all` appears in every version; `Q3=2` etc. only when paper_config.tex "
               "selects that outcome.")
    out += ["", "## Text fill-ins", "", "| File | Line | Hint | Preceding text | Branch |",
            "|---|---:|---|---|---|"]
    out += [f"| {f} | {n} | `{h}` | {c.replace('|', '/')} | {b} |" for f, n, h, c, b in fillins]
    out += ["", "## Figure placeholders", "", "| File | Line | Figure |", "|---|---:|---|"]
    out += [f"| {f} | {n} | {h} |" for f, n, h in figures]
    out += ["", "## Tables", "", "| Table | Used in | Pending cells | Fill-ins |",
            "|---|---|---:|---:|"]
    out += [f"| tables/{t}.tex | {u} | {c} | {h} |" for t, u, c, h in tables]
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zh", action="store_true", help="scan the Chinese mirror instead")
    parser.add_argument("--markdown", type=Path, help="also write the report to this file")
    args = parser.parse_args()
    report = render(*scan(args.zh))
    print(report)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
