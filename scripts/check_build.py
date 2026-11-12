"""Check the compiled manuscripts after scripts/build.ps1.

Usage: python scripts/check_build.py [--strict] [--final]

Blocking: LaTeX/BibTeX errors, undefined or multiply defined labels and citations,
missing glyphs, pending reruns, incorrect disclosure/appendix/bibliography structure, and a
main body that ends after page eight, including a body figure or table that LaTeX
deferred past it. Reported: overfull boxes,
pending result cells (\\resultplaceholder in tables), pending text fill-ins
(\\fillin in prose), and differences between each English source file and its Chinese
mirror: stated numbers, and structure (outcome-switch branches, fill-ins, figure
placeholders, labels, references, citations, table inputs). --strict also blocks on
overfull boxes and EN/ZH differences; --final also blocks on pending result cells and
text fill-ins.
"""
import argparse
from collections import Counter
import re
import sys

from common import REPO, TABLES

DOCUMENTS = ("main", "supplementary", "paper_full", "manuscript_zh")
BODY_PAGE_LIMIT = 8
LOG_PATTERNS = {
    "errors": re.compile(r"^! |LaTeX Error|Emergency stop|Undefined control sequence|"
                         r"Forbidden control sequence|Runaway argument|Fatal error"),
    "undefined": re.compile(r"There were undefined (references|citations)|"
                            r"(Reference|Citation) `[^']*' on page \d+ undefined"),
    "multiply_defined": re.compile(r"multiply[- ]defined"),
    "rerun": re.compile(r"Label\(s\) may have changed|Rerun to get"),
    "overfull": re.compile(r"^Overfull \\[hv]box"),
    "missing_glyphs": re.compile(r"Missing character"),
}
BLOCKING = ("errors", "undefined", "multiply_defined", "rerun", "missing_glyphs")
SECTIONS = ("teaser", "introduction", "related_work", "method", "experiments", "conclusion")
APPENDICES = ("implementation", "benchmark", "results", "real")
_FILLIN = re.compile(r"\\fillin\{")
_COMMENT = re.compile(r"(?<!\\)%.*$", re.MULTILINE)
_NON_PROSE = re.compile(
    r"\\(?:label|ref|appref|mainref|eqref|cite[pt]?|input|include|path|url|begin|end|"
    r"includegraphics|figplaceholder|resizebox|fontsize|setlength|hspace|vspace|addlinespace|"
    r"renewcommand|renewenvironment|newcommand)\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})*")
_NUMBER = re.compile(r"(?<![A-Za-z_\\])\d+(?:,\d{3})*(?:\.\d+)?")
_ABSTRACT = re.compile(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", re.DOTALL)
_TITLE = re.compile(r"^\\title\{(.*)\}$", re.MULTILINE)


def log_findings(name):
    log = REPO / f"{name}.log"
    if not log.is_file():
        return None
    text = log.read_text(encoding="utf-8", errors="replace")
    findings = {key: [line for line in text.splitlines() if pattern.search(line)]
                for key, pattern in LOG_PATTERNS.items()}
    pages = re.findall(r"Output written on \S+ \((\d+) pages?", text)
    findings["pages"] = int(pages[-1]) if pages else None
    return findings


def body_end_page():
    aux = REPO / "main.aux"
    if not aux.is_file():
        return None
    match = re.search(r"\\newlabel\{main:body-end\}\{\{[^{}]*\}\{(\d+)\}",
                      aux.read_text(encoding="utf-8", errors="replace"))
    return int(match.group(1)) if match else None


def late_floats():
    """Figures and tables of the main body that LaTeX deferred beyond the page limit.

    The body-end label marks where the text stops, but a deferred float is flushed
    by the \\clearpage before the references and still counts as body content.
    """
    aux = REPO / "main.aux"
    if not aux.is_file():
        return []
    labels = re.findall(r"\\newlabel\{((?:fig|tab):[^}]+)\}\{\{[^{}]*\}\{(\d+)\}",
                        aux.read_text(encoding="utf-8", errors="replace"))
    return sorted((name, int(page)) for name, page in labels if int(page) > BODY_PAGE_LIMIT)


def pending_cells():
    """Count pending result cells per table, split by where each table is used."""
    counts = {path.stem: path.read_text(encoding="utf-8").count(r"\resultplaceholder")
              for path in sorted(TABLES.glob("*.tex"))}
    used = {}
    for scope, files in (("main", [REPO / "sections" / f"{s}.tex" for s in SECTIONS]),
                         ("supplement", [REPO / "appendix" / f"{a}.tex" for a in APPENDICES])):
        names = set()
        for path in files:
            names |= set(re.findall(r"\\input\{tables/([^}]+)\}", path.read_text(encoding="utf-8")))
        used[scope] = {name: counts[name] for name in sorted(names) if counts.get(name)}
    return used


def pending_fillins():
    """Count \\fillin{...} placeholders in the prose, split into main text and supplement."""
    main = [REPO / "main.tex"] + [REPO / "sections" / f"{name}.tex"
                                for name in SECTIONS + ("llm_usage",)]
    main += sorted((REPO / "figures").glob("Fig*/figure.tex"))
    supplement = [REPO / "appendix" / f"{name}.tex" for name in APPENDICES]
    counts = {}
    for scope, files in (("main", main), ("supplement", supplement)):
        found = {}
        for path in files:
            if path.is_file():
                hits = len(_FILLIN.findall(_COMMENT.sub("", path.read_text(encoding="utf-8"))))
                if hits:
                    found[path.relative_to(REPO).as_posix()] = hits
        counts[scope] = found
    return counts


def numbers(text):
    """Numbers stated in prose, ignoring labels, citations, layout and small counts."""
    text = _NON_PROSE.sub(" ", _COMMENT.sub("", text))
    values = (match.replace(",", "") for match in _NUMBER.findall(text))
    return Counter(value for value in values if "." in value or int(value) > 20)


def mirrored_pairs():
    main = (REPO / "main.tex").read_text(encoding="utf-8")
    zh = (REPO / "manuscript_zh.tex").read_text(encoding="utf-8")
    pairs = [(name, pattern.search(main).group(1), pattern.search(zh).group(1))
             for name, pattern in (("title", _TITLE), ("abstract", _ABSTRACT))]
    for folder, names in (("sections", SECTIONS + ("llm_usage",)),
                          ("appendix", APPENDICES)):
        for name in names:
            english, chinese = REPO / folder / f"{name}.tex", REPO / "zh" / folder / f"{name}.tex"
            pairs.append((f"{folder}/{name}", english.read_text(encoding="utf-8"),
                          chinese.read_text(encoding="utf-8")))
    for english in sorted((REPO / "figures").glob("Fig*/figure.tex")):
        chinese = english.with_name("figure_zh.tex")
        pairs.append((english.parent.relative_to(REPO).as_posix(),
                      english.read_text(encoding="utf-8"), chinese.read_text(encoding="utf-8")))
    return pairs


def number_differences():
    report = []
    for name, english, chinese in mirrored_pairs():
        en, zh = numbers(english), numbers(chinese)
        only_en, only_zh = en - zh, zh - en
        if only_en or only_zh:
            report.append((name, sorted(only_en.elements()), sorted(only_zh.elements())))
    return report


_STRUCTURE = {
    "switch branches": re.compile(r"\\(?:Qtwo|Qthree|Bbone)\{\d\}|\\(?:QtwoSel|QthreeSel|BboneSel)\b"),
    "fill-ins": re.compile(r"\\fillin\{"),
    "figure placeholders": re.compile(r"\\figplaceholder\b"),
    "labels": re.compile(r"\\label\{[^}]+\}"),
    "tables": re.compile(r"\\input\{tables/[^}]+\}"),
}
_REFERENCE = re.compile(r"\\(?:ref|eqref|appref|mainref)\{([^}]+)\}")
_CITATION = re.compile(r"\\cite[pt]?\{([^}]+)\}")


def structure_differences():
    """Markup that must correspond between each English file and its Chinese mirror.

    Switch branches, fill-ins, figure placeholders, labels and table inputs must match one
    to one; the sets of cross-references and citation keys must be equal (wording may refer
    to the same item more than once).
    """
    report = []
    for name, english, chinese in mirrored_pairs():
        en, zh = _COMMENT.sub("", english), _COMMENT.sub("", chinese)
        for kind, pattern in _STRUCTURE.items():
            a, b = Counter(pattern.findall(en)), Counter(pattern.findall(zh))
            if a != b:
                report.append((name, kind, sorted((a - b).elements()), sorted((b - a).elements())))
        for kind, pattern in (("references", _REFERENCE), ("citations", _CITATION)):
            a = {key.strip() for match in pattern.findall(en) for key in match.split(",")}
            b = {key.strip() for match in pattern.findall(zh) for key in match.split(",")}
            if a != b:
                report.append((name, kind, sorted(a - b), sorted(b - a)))
    return report


def submission_findings():
    """Check disclosure placement, compiled appendices, and bibliography coverage."""
    failures = []
    for document, statement in (("main", "sections/llm_usage"),
                                ("manuscript_zh", "zh/sections/llm_usage")):
        source = _COMMENT.sub("", (REPO / f"{document}.tex").read_text(encoding="utf-8"))
        end = source.find(r"\input{" + ("sections/" if document == "main" else "zh/sections/")
                          + "conclusion}")
        disclosure = source.find(r"\input{" + statement + "}")
        bibliography = source.find(r"\bibliography{")
        if not (0 <= end < disclosure < bibliography):
            failures.append(f"{document}: LLM statement must follow the body and precede references")
        text = (REPO / f"{statement}.tex").read_text(encoding="utf-8")
        if "LLM Usage Statement" not in text:
            failures.append(f"{document}: missing LLM Usage Statement heading")

    aux_texts = {}
    for document in DOCUMENTS:
        path = REPO / f"{document}.aux"
        if not path.is_file():
            failures.append(f"{document}: missing aux for appendix/citation checks")
            continue
        aux_texts[document] = path.read_text(encoding="utf-8")
        if not (REPO / f"{document}.pdf").is_file():
            failures.append(f"{document}: missing PDF")
        cited = {key.strip() for group in re.findall(r"\\citation\{([^}]+)\}", aux_texts[document])
                 for key in group.split(",")}
        rendered = set(re.findall(r"\\bibcite\{([^}]+)\}", aux_texts[document]))
        if cited != rendered:
            failures.append(f"{document}: citation/bibliography mismatch "
                            f"(missing {sorted(cited - rendered)}, unused {sorted(rendered - cited)})")
        blg = REPO / f"{document}.blg"
        if not blg.is_file():
            failures.append(f"{document}: missing BibTeX log")
        elif re.search(r"Warning--|Repeated entry|I couldn't open|error message",
                       blg.read_text(encoding="utf-8")):
            failures.append(f"{document}: BibTeX reported a warning or error")

    for document in ("main", "paper_full", "manuscript_zh"):
        if document in aux_texts and r"\newlabel{sec:llm_usage}" not in aux_texts[document]:
            failures.append(f"{document}: LLM statement absent from compiled labels")
    if re.search(r"\\newlabel\{app:", aux_texts.get("main", "")):
        failures.append("main: appendix content must be submitted separately")
    for document in ("supplementary", "paper_full", "manuscript_zh"):
        if document not in aux_texts:
            continue
        for name, letter in zip(APPENDICES, "ABCD", strict=True):
            found = re.search(r"\\newlabel\{app:" + name + r"\}\{\{([^}]+)\}",
                              aux_texts[document])
            if not found or found.group(1) != letter:
                failures.append(f"{document}: appendix {letter} ({name}) missing or misnumbered")
    if "paper_full" in aux_texts and "manuscript_zh" in aux_texts:
        en = set(re.findall(r"\\bibcite\{([^}]+)\}", aux_texts["paper_full"]))
        zh = set(re.findall(r"\\bibcite\{([^}]+)\}", aux_texts["manuscript_zh"]))
        if en != zh:
            failures.append(f"EN/ZH bibliography differs (only EN {sorted(en - zh)}, "
                            f"only ZH {sorted(zh - en)})")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    failures = []

    for name in DOCUMENTS:
        findings = log_findings(name)
        if findings is None:
            print(f"{name}: no log; build it first")
            failures.append(f"{name}: not built")
            continue
        counts = {key: len(findings[key]) for key in LOG_PATTERNS}
        print(f"{name}: {findings['pages']} pages; " +
              ", ".join(f"{key} {value}" for key, value in counts.items()))
        for key in BLOCKING + (("overfull",) if args.strict else ()):
            if counts[key]:
                failures.append(f"{name}: {counts[key]} {key}")
                for line in findings[key][:5]:
                    print(f"    {line.strip()}")

    page = body_end_page()
    print(f"main body ends on page {page} (limit {BODY_PAGE_LIMIT})")
    if page is None or page > BODY_PAGE_LIMIT:
        failures.append("main body exceeds the page limit or its end label is missing")
    late = late_floats()
    if late:
        print("    floats placed after the page limit: " +
              ", ".join(f"{name} (p. {where})" for name, where in late))
        failures.append(f"{len(late)} main-body float(s) after page {BODY_PAGE_LIMIT}")

    submission = submission_findings()
    print(f"LLM statement, appendices A-D, and bibliography: {len(submission)} issue(s)")
    for finding in submission:
        print(f"    {finding}")
    failures.extend(submission)

    for scope, tables in pending_cells().items():
        total = sum(tables.values())
        print(f"pending result cells in {scope}: {total}" +
              ("" if not tables else " (" + ", ".join(f"{k} {v}" for k, v in tables.items()) + ")"))
        if args.final and total:
            failures.append(f"{scope}: {total} pending result cells")

    for scope, files in pending_fillins().items():
        total = sum(files.values())
        print(f"pending text fill-ins in {scope}: {total}" +
              ("" if not files else " (" + ", ".join(f"{k} {v}" for k, v in files.items()) + ")"))
        if args.final and total:
            failures.append(f"{scope}: {total} pending text fill-ins")

    differences = number_differences()
    print(f"EN/ZH number differences: {len(differences)} file pair(s)")
    for name, only_en, only_zh in differences:
        print(f"    {name}: only EN {only_en[:12]}; only ZH {only_zh[:12]}")
    if args.strict and differences:
        failures.append("EN/ZH numbers differ")

    structure = structure_differences()
    print(f"EN/ZH structure differences: {len(structure)}")
    for name, kind, only_en, only_zh in structure:
        print(f"    {name} {kind}: only EN {only_en[:8]}; only ZH {only_zh[:8]}")
    if args.strict and structure:
        failures.append("EN/ZH structure differs")

    if failures:
        print("FAILED: " + "; ".join(failures))
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
