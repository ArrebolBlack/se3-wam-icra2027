#!/usr/bin/env python3
"""Convert a paper PDF into a uniform blind-review text.

Same treatment for every paper: figure graphics (and any text drawn inside them) are
removed and only captions remain; running headers, footers, watermarks and margin stamps
are dropped; tables are rebuilt row by row with every numeric cell masked; in prose,
decimals, percentages, multipliers and numbers with physical units are masked, while
plain integers (counts, years, section numbers) are kept.

usage: pdf2blind.py input.pdf output.txt [--debug]
"""
import re
import subprocess
import sys
from xml.etree import ElementTree as ET

import pdfplumber

NS = "{http://www.w3.org/1999/xhtml}"
MASK = "[MASK]"

UNIT = (r"(?:%|×(?!\s?\d)|m/s\b|cm/s\b|mm/s\b|rad/s\b|deg/s\b|°/s\b|"
        r"GPU-hours?\b|TFLOPs?\b|GFLOPs?\b|FLOPs?\b|x\b(?!\s?\d)|mm\b|cm\b|km\b|ms\b|m\b|sec\b|s\b|min\b|"
        r"kHz\b|Hz\b|fps\b|FPS\b|°|degrees?\b|deg\b|rad\b|GiB\b|GB\b|MB\b|TB\b|M\b|B\b|K\b|k\b|G\b|"
        r"hours?\b|hrs?\b|h\b|days?\b|N\b|kg\b|g\b)")
NUM = r"[+\-−±~≈]?\d[\d,]*(?:\.\d+)?"
REF = r"(?<!Sec\. )(?<!Section )(?<!Secs\. )(?<!Eq\. )(?<!Eqs\. )(?<!Fig\. )(?<!Figs\. )(?<!Figure )(?<!Table )(?<!Tab\. )(?<!Appendix )(?<!App\. )(?<!Alg\. )(?<!§)(?<!§ )"
PROSE_PATTERNS = [
    re.compile(rf"{REF}(?<![\w.\[])({NUM})(\s?){UNIT}"),          # number with unit / % / ×
    re.compile(rf"{REF}(?<![\w.\[])([+\-−±]\d+(?:\.\d+)?|\d+\.\d+)\s?(?:points?|pts?|pp|p\.p\.)\b"),
    re.compile(rf"{REF}(?<![\w.\[])[+\-−±~≈]?\d+\.\d+(?![\w.])"),   # any decimal
    re.compile(r"(?<![\w.\[\])])[+\-−±]?\.\d+(?![\w.])"),             # leading-dot decimal (.08)
]
REF_WORDS = {"Sec.", "Secs.", "Section", "Sections", "Table", "Tables", "Tab.", "Fig.", "Figs.", "Figure",
             "Eq.", "Eqs.", "Appendix", "App.", "Alg.", "§"}
TABLE_TOKEN = re.compile(
    r"^[\(\[]?[+\-−±~≈]?(\d[\d,]*(\.\d+)?|\.\d+)(%|×|x|k|K|M|B|pp|ms|s|mm|°)?"
    r"([±/:]\s*[+\-−]?\d[\d,]*(\.\d+)?%?)*[\)\]]?[,;*†‡]*$")


def mask_prose(text):
    text = re.sub(r"π\s?0\.5", "π0\u20275", text)       # protect the model name pi_0.5
    text = re.sub(r"(arXiv:|abs/)\s?(\d{4})\.(\d{4,5})", lambda m: m.group(1) + m.group(2) + "\u2027" + m.group(3), text)
    text = re.sub(r"(doi:\s?)(\S+)", lambda m: m.group(1) + m.group(2).replace(".", "\u2027"), text)
    for pattern in PROSE_PATTERNS:
        text = pattern.sub(MASK, text)
    text = re.sub(r"[+\-−±]?\d+(\.\d+)?(?=\s?[~–\-]\s?\[MASK\])", MASK, text)
    text = text.replace("\u2027", ".")
    text = re.sub(r"(\[MASK\]\s*){2,}", MASK + " ", text)
    return text


def mask_table_token(token):
    core = token.strip()
    if TABLE_TOKEN.match(core):
        return MASK
    # value with uncertainty glued, e.g. 45.6±1.2, 12.3(0.4)
    if re.match(r"^[+\-−]?\d+(\.\d+)?(±|\()\d", core):
        return MASK
    return token


def parse_bbox_layout(pdf):
    xml = subprocess.run(["pdftotext", "-bbox-layout", pdf, "-"], capture_output=True,
                         text=True, check=True).stdout
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml)
    xml = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xml)
    xml = re.sub(r"&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", xml)
    root = ET.fromstring(xml)
    pages = []
    for page in root.iter(NS + "page"):
        blocks = []
        for flow in page.iter(NS + "flow"):
            for block in flow.iter(NS + "block"):
                lines = []
                for line in block.iter(NS + "line"):
                    words = [(w.text or "", float(w.get("xMin")), float(w.get("yMin")),
                              float(w.get("xMax")), float(w.get("yMax"))) for w in line.iter(NS + "word")]
                    if words:
                        lines.append(words)
                if lines:
                    xs0 = min(w[1] for l in lines for w in l); ys0 = min(w[2] for l in lines for w in l)
                    xs1 = max(w[3] for l in lines for w in l); ys1 = max(w[4] for l in lines for w in l)
                    blocks.append({"bbox": (xs0, ys0, xs1, ys1), "lines": lines})
        pages.append({"w": float(page.get("width")), "h": float(page.get("height")), "blocks": blocks})
    return pages


def union_find_clusters(boxes, pad):
    parent = list(range(len(boxes)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    order = sorted(range(len(boxes)), key=lambda i: boxes[i][0])
    for a_idx, a in enumerate(order):
        ax0, ay0, ax1, ay1 = boxes[a][:4]
        for b in order[a_idx + 1:]:
            bx0, by0, bx1, by1 = boxes[b][:4]
            if bx0 - pad > ax1 + pad:
                break
            if by0 - pad <= ay1 + pad and ay0 - pad <= by1 + pad:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra
    groups = {}
    for i in range(len(boxes)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def graphics_regions(page, blocks=()):
    """Return (figure_regions, table_regions) in page coordinates (x0, top, x1, bottom)."""
    rules, objs = [], []
    W = float(page.width)
    for im in page.images:
        objs.append((im["x0"], im["top"], im["x1"], im["bottom"], "img"))
    for c in page.curves:
        objs.append((c["x0"], c["top"], c["x1"], c["bottom"], "curve"))
    for r in page.rects:
        w, h = r["x1"] - r["x0"], r["bottom"] - r["top"]
        if h < 1.6 and w > 80:
            rules.append((r["x0"], r["top"], r["x1"], r["bottom"], h))
        elif h < 1.6 and w > 15:
            continue                      # math bars, cmidrules: neither table frame nor figure
        elif w < 1.6 and h > 6:
            objs.append((r["x0"], r["top"], r["x1"], r["bottom"], "vrule"))
        else:
            objs.append((r["x0"], r["top"], r["x1"], r["bottom"], "rect"))
    for l in page.lines:
        if abs(l["bottom"] - l["top"]) < 1.0 and (l["x1"] - l["x0"]) > 80:
            rules.append((l["x0"], l["top"], l["x1"], l["bottom"], float(l.get("linewidth") or 0.0)))
        elif abs(l["bottom"] - l["top"]) < 1.0 and (l["x1"] - l["x0"]) > 15:
            continue
        else:
            objs.append((l["x0"], l["top"], l["x1"], l["bottom"], "line"))
    # tables: groups of horizontal rules sharing an x-range
    tables = []
    rules.sort(key=lambda r: r[1])
    used = [False] * len(rules)

    def overlap(a, b):
        return min(a[2], b[2]) - max(a[0], b[0])
    # a booktabs table (heavy top rule) stays open across a tall body until its next heavy rule,
    # unless a table or figure caption lies in between
    cap_y = [((bb["bbox"][0] + bb["bbox"][2]) / 2, (bb["bbox"][1] + bb["bbox"][3]) / 2) for bb in blocks
             if re.match(r"^(Table|TABLE|Tab\.|Figure|FIGURE|Fig\.)\s*(S?\d+|[IVXLC]+)[.:]",
                         join_lines(bb["lines"]).strip())]

    def caption_between(x0, x1, y0, y1):
        return any(x0 - 2 <= cx <= x1 + 2 and y0 < cy < y1 for cx, cy in cap_y)
    for i, r in enumerate(rules):
        if used[i]:
            continue
        group = [r]; used[i] = True
        for j in range(i + 1, len(rules)):
            if used[j]:
                continue
            s = rules[j]
            ov = min(r[2], s[2]) - max(r[0], s[0])
            if ov <= 0.85 * max(r[2] - r[0], s[2] - s[0]):
                continue
            gap = s[1] - group[-1][3]
            still_open = group[0][4] >= 0.75 and sum(g[4] >= 0.75 for g in group) % 2 == 1
            if caption_between(r[0], r[2], group[-1][3], s[1]):
                continue                  # a caption separates two tables
            if gap < 260 or (gap < 700 and still_open and s[4] >= 0.75):
                group.append(s); used[j] = True
        if len(group) >= 2 and group[-1][3] - group[0][1] > 12:
            tables.append((min(g[0] for g in group) - 2, group[0][1] - 1,
                           max(g[2] for g in group) + 2, group[-1][3] + 1))
    # figures: clusters of graphic objects
    figures, clusters = [], []
    if objs:
        for members in union_find_clusters(objs, 3.0):
            box = (min(objs[i][0] for i in members), min(objs[i][1] for i in members),
                   max(objs[i][2] for i in members), max(objs[i][3] for i in members))
            kinds = [objs[i][4] for i in members]
            clusters.append(box)
            area = (box[2] - box[0]) * (box[3] - box[1])
            has_img = "img" in kinds
            n_draw = sum(k in ("curve", "line", "rect") for k in kinds)
            if has_img and area > 400:
                figures.append(box)
            elif n_draw >= 4 and area > 2500:
                # a tinted table (row colors) inside a rule-bounded table is not a figure
                inside_table = any(box[0] >= t[0] - 4 and box[2] <= t[2] + 4 and box[1] >= t[1] - 30
                                   and box[3] <= t[3] + 4 for t in tables)
                if not inside_table:
                    figures.append(box)
    return figures, tables, clusters


CAPTION = re.compile(r"^(Figure|Fig\.)\s*S?\d+[.:]")


def caption_regions(blocks, clusters):
    """The area between a figure's graphics and its caption, spanning the caption's width."""
    regions = []
    for b in blocks:
        text = join_lines(b["lines"])
        if not CAPTION.match(text):
            continue
        cx0, cy0, cx1, _ = b["bbox"]
        top, x0, x1 = cy0, cx0, cx1
        found = False
        for c in sorted(clusters, key=lambda c: -c[3]):
            ov = min(c[2], cx1) - max(c[0], cx0)
            if ov <= 0.3 * (c[2] - c[0]) or c[3] > cy0 + 3:
                continue
            if c[3] >= top - 40:
                top = min(top, c[1]); x0 = min(x0, c[0]); x1 = max(x1, c[2]); found = True
        if found:
            regions.append((x0, top, x1, cy0 - 0.5))
    return regions


def inside(cx, cy, box, pad=2.0):
    return box[0] - pad <= cx <= box[2] + pad and box[1] - pad <= cy <= box[3] + pad


def table_text(page, box):
    words = page.extract_words(x_tolerance=1.5, y_tolerance=2.0)
    sel = [w for w in words if inside((w["x0"] + w["x1"]) / 2, (w["top"] + w["bottom"]) / 2, box, 0.5)]
    sel.sort(key=lambda w: (round(w["top"] / 2.5), w["x0"]))
    rows, cur, cur_top = [], [], None
    for w in sorted(sel, key=lambda w: w["top"]):
        if cur_top is None or abs(w["top"] - cur_top) <= 2.5:
            cur.append(w); cur_top = w["top"] if cur_top is None else cur_top
        else:
            rows.append(cur); cur = [w]; cur_top = w["top"]
    if cur:
        rows.append(cur)
    out = []
    for row in rows:
        row.sort(key=lambda w: w["x0"])
        cells, last_x1, protect = [], None, False
        for w in row:
            # numbers that follow "Sec.", "Table", "Appendix", ... are references, not results
            tok = w["text"] if protect else mask_table_token(w["text"])
            protect = (w["text"] in REF_WORDS) or (protect and w["text"].endswith(","))
            if last_x1 is not None and w["x0"] - last_x1 > 6:
                cells.append(" | ")
            elif last_x1 is not None:
                cells.append(" ")
            cells.append(tok)
            last_x1 = w["x1"]
        line = "".join(cells)
        line = re.sub(r"(\[MASK\] ?){2,}", lambda m: " ".join([MASK] * m.group(0).count(MASK)), line)
        out.append(line)
    return "\n".join(out)


WATERMARK = re.compile(r"(This CVPR paper is the Open Access version|Except for this watermark|"
                       r"final published version of the proceedings|Published as a conference paper at|"
                       r"Robotics: Science and Systems 20\d\d|arXiv:\d{4}\.\d{4,5}|Anonymous CVPR submission|"
                       r"CONFIDENTIAL REVIEW COPY)")


def join_lines(lines):
    texts = [" ".join(w[0] for w in line) for line in lines]
    out = ""
    for t in texts:
        if not out:
            out = t
        elif out.endswith("-") and t[:1].isalpha():
            out = out + "\u2063" + t
        elif out.endswith("-") and t[:1].isdigit():
            out = out + t
        else:
            out = out + " " + t
    return out


LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st"}


def order_blocks(blocks, W):
    mid = W / 2

    def col(b):
        x0, _, x1, _ = b["bbox"]
        if x1 <= mid + 10:
            return 0
        if x0 >= mid - 10:
            return 1
        return 2
    out, band = [], []

    def flush():
        out.extend(sorted([b for b in band if col(b) == 0], key=lambda b: b["bbox"][1]))
        out.extend(sorted([b for b in band if col(b) == 1], key=lambda b: b["bbox"][1]))
        band.clear()
    for b in sorted(blocks, key=lambda b: b["bbox"][1]):
        if col(b) == 2:
            flush()
            out.append(b)
        else:
            band.append(b)
    flush()
    return out


def resolve_hyphens(text, vocab):
    def fix(m):
        a, b = m.group(1), m.group(2)
        if (a + b).lower() in vocab and (a + "-" + b).lower() not in vocab:
            return a + b
        return a + "-" + b
    return re.sub(r"(\w+)-\u2063(\w+)", fix, text)


ABSTRACT = re.compile(r"^(Abstract|A BSTRACT|ABSTRACT|Abstract\.|Abstract—)")
FOOTNOTE = re.compile(r"^([∗*†‡§¶]|\d\s*[A-Z][a-z]+ (University|Institute)|Equal contribution|Corresponding|Correspondence|"
                      r"Project lead|Joint (first|supervision|project)|Contact:|Work done)")
HEADING_AFTER_ACK = re.compile(r"^(\d+\.?\s*)?(References|R EFERENCES|REFERENCES|Appendix|A PPENDIX|APPENDIX|"
                               r"Supplementary|[A-Z]\.?\s+[A-Z][a-z]+)")


def clean_front_and_back(chunks):
    out = list(chunks)
    # front matter: keep the title, drop author and affiliation blocks before the abstract
    first_page = [i for i, (p, _) in enumerate(out) if p == 0]
    abs_idx = next((i for i, (p, c) in enumerate(out) if p <= 1 and ABSTRACT.match(c.strip())), None)
    if first_page and abs_idx is not None:
        keep = []
        for i, (p, c) in enumerate(out):
            if 0 < i < abs_idx and not CAPTION.match(c) and not c.startswith("[figure"):
                continue
            keep.append((p, c))
        out = keep
    out = [(p, c) for (p, c) in out if not (p == 0 and FOOTNOTE.match(c.strip()) and len(c.split()) < 60)]
    ORG = re.compile(r"(University|Institute|Robotics|Lab\b|Laboratory|Inc\.?|Research|Academy|College|NVIDIA|Google|"
                     r"Meta\b|Microsoft|DeepMind|Horizon|Galbot|ShengShu|Tsinghua|Stanford|MIT\b|Princeton)")
    out = [(p, c) for (p, c) in out if not (p == 0 and len(c.split()) <= 6 and
                                            (re.fullmatch(r"[\d\s,∗*†‡]+", c.strip()) or ORG.search(c)))]
    # running heads of single-column templates (e.g. "K. Zhou et al.")
    out = [(p, c) for (p, c) in out if not re.fullmatch(r"\s*[A-Z]\. [A-Z][\w-]+ et al\.\s*", c)]
    # acknowledgments
    res, skipping = [], False
    for p, c in out:
        head = c.strip()
        if re.match(r"^(\d+\.?\s*)?(Acknowledg(e)?ments?|A CKNOWLEDG|ACKNOWLEDG)", head):
            skipping = True
            continue
        if skipping and HEADING_AFTER_ACK.match(head):
            skipping = False
        if not skipping:
            res.append((p, c))
    return res


def convert(pdf, debug=False):
    layout = parse_bbox_layout(pdf)
    chunks = []
    with pdfplumber.open(pdf) as doc:
        for pno, (page, lay) in enumerate(zip(doc.pages, layout)):
            figs, tabs, clusters = graphics_regions(page, lay["blocks"])
            caps = caption_regions(lay["blocks"], clusters)
            figs = figs + caps
            W, H = lay["w"], lay["h"]
            emitted_fig, emitted_tab = set(), set()
            for block in order_blocks(lay["blocks"], lay["w"]):
                x0, y0, x1, y1 = block["bbox"]
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                nwords = sum(len(l) for l in block["lines"])
                text = join_lines(block["lines"])
                if WATERMARK.search(text) and nwords < 40:
                    continue
                if (y1 < 0.075 * H or y0 > 0.945 * H) and nwords <= 15:
                    continue                      # running header / footer / page number
                if re.fullmatch(r"\s*\d{1,3}\s*", text) and (y0 > 0.85 * H or y1 < 0.15 * H):
                    continue                      # bare page number
                if (x1 - x0) < 25 and (y1 - y0) > 120:
                    continue                      # vertical margin stamp
                ti = next((k for k, t in enumerate(tabs) if inside(cx, cy, t)), None)
                if ti is not None:
                    if ti not in emitted_tab:
                        emitted_tab.add(ti)
                        chunks.append((pno, "[TABLE]\n" + table_text(page, tabs[ti]) + "\n[/TABLE]"))
                    continue
                fi = None
                if nwords <= 35 and not CAPTION.match(text):
                    fi = next((k for k, f in enumerate(figs) if inside(cx, cy, f, 3.0)), None)
                if fi is None and nwords <= 12 and not CAPTION.match(text):
                    fi = next((k for k, f in enumerate(caps) if f[0] - 3 <= cx <= f[2] + 3
                               and f[1] - 16 <= cy <= f[1]), None)
                    fi = None if fi is None else len(figs) - len(caps) + fi
                if fi is not None:
                    if fi not in emitted_fig:
                        emitted_fig.add(fi)
                        chunks.append((pno, "[figure graphics omitted]"))
                    continue
                chunks.append((pno, mask_prose(text)))
            if debug:
                sys.stderr.write(f"page {pno + 1}: figures={len(figs)} tables={len(tabs)}\n")
    chunks = clean_front_and_back(chunks)
    marked = []
    for p_, c in chunks:
        if CAPTION.match(c.strip()) and not (marked and marked[-1][1].startswith("[figure graphics omitted]")):
            marked.append((p_, "[figure graphics omitted]"))
        marked.append((p_, c))
    chunks = marked
    text = "\n\n".join(c for _, c in chunks)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\b[\w.-]+\.github\.io\S*", "", text)
    text = re.sub(r"\S+@\S+\.\w+", "", text)
    # link labels left behind by removed URLs, only when they form a whole line ("Project Page", "Code:")
    text = re.sub(r"(?m)^[ \t]*(Project|Code|Website|Videos?)([ \t]+(Page|page|available at|and code))?[ \t]*:?[ \t]*$", "", text)
    # ... and at the end of a line when they carry a colon ("... robotic tasks. Project Page:")
    text = re.sub(r"(Project|Code|Website|Videos?)([ \t]+(Page|page|available at|and code))?[ \t]*:[ \t]*(?=\n|$)", "", text)
    for k, v in LIGATURES.items():
        text = text.replace(k, v)
    vocab = set(w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-]+", text.replace("\u2063", " ")))
    text = resolve_hyphens(text, vocab)
    text = text.replace("\u2063", "")
    text = re.sub(r"(\[figure graphics omitted\]\s*){2,}", "[figure graphics omitted]\n\n", text)
    text = re.sub(r"\n[ \t]*\n([ \t]*\n)+", "\n\n", text)
    return text


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    out = convert(src, debug="--debug" in sys.argv)
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(out + "\n")
    print(f"{src} -> {dst}: {len(out.split())} words")
