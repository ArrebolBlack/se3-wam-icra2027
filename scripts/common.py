"""Shared paths, task labels, validation, and figure rendering for the paper scripts.

Exporters resolve Research through research_root(). SVG figures are printed to PDF
by svg_to_pdf(), always inside the script that draws them, so every figure PDF has
exactly one producer and the LaTeX build never rewrites it.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIGURES = REPO / "figures"
TABLES = REPO / "tables"
REVIEW = REPO / "tmp" / "figure-review"

RESEARCH_ENV = "SE3WAM_RESEARCH"
DEFAULT_RESEARCH = Path("C:/workspace/se3-wam-research")
CHROMIUM_ENV = "SE3WAM_CHROMIUM"
# Accepted P15 DEV84 report archive and its acceptance record, relative to Research.
P15_ARCHIVE = Path("local_private/future0-aux-20261012/"
                   "P15-archive-aux-p15-reports-a36-low-priority-4g-a1-a1/"
                   "reports-downloaded-20261013T110014343027Z.tar")
P15_ACCEPTANCE = ("docs/experiments/FUTURE0/results/auxiliary_supervision/"
                  "P15_complete_report_archive_20261013.json")

TASKS = ("grasp", "t1_belt", "t1_occ", "t1_so3", "t1_xyz", "t2_se3", "t2_trans",
         "t3_full", "t3_phase", "t4_can", "t4_slider", "t4_sphere",
         "t4_sphere_tabletop", "t5_replan")
# Row labels shared by the per-task tables; grouped tables shorten some of them.
TASK_LABELS = {
    "grasp": ("Grasp", "抓取"),
    "t1_belt": ("Belt", "传送带"),
    "t1_occ": ("Occlusion", "遮挡"),
    "t1_so3": ("SO(3)", "SO(3)"),
    "t1_xyz": ("XYZ", "XYZ"),
    "t2_se3": ("SE(3) placement", "SE(3) 放置"),
    "t2_trans": ("Trans. placement", "平移放置"),
    "t3_full": ("Full passage", "完整穿越"),
    "t3_phase": ("Phase passage", "相位穿越"),
    "t4_can": ("Can", "罐体"),
    "t4_slider": ("Slider", "滑块"),
    "t4_sphere": ("Sphere", "球体"),
    "t4_sphere_tabletop": ("Tabletop sphere", "桌面球体"),
    "t5_replan": ("Replan", "重规划"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tablelang(english, chinese):
    """Return the shared-table language switch, or plain text when both agree."""
    return english if english == chinese else rf"\tablelang{{{english}}}{{{chinese}}}"


def task_label(task):
    return tablelang(*TASK_LABELS[task])


def research_root(value=None):
    """Resolve Research from --research-root, then $SE3WAM_RESEARCH, then the default checkout."""
    root = Path(value) if value else Path(os.environ.get(RESEARCH_ENV) or DEFAULT_RESEARCH)
    if not (root / "docs" / "experiments").is_dir():
        raise FileNotFoundError(
            f"No Research checkout at {root}; pass --research-root or set {RESEARCH_ENV}")
    return root


def add_research_argument(parser):
    parser.add_argument(
        "--research-root", "--research", dest="research_root", type=Path, default=None,
        help=f"Research checkout (default: ${RESEARCH_ENV}, else {DEFAULT_RESEARCH})")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


_LOCAL_IMAGE = re.compile(
    r'(?P<attr>(?:xlink:)?href)="(?P<path>[^"#]+\.(?:png|jpe?g|webp))"', re.IGNORECASE)
_VIEWBOX = re.compile(
    rb'viewBox="\s*0\s+0\s+(?P<width>[0-9.]+)\s+(?P<height>[0-9.]+)\s*"')
_PDF_TIMESTAMP = re.compile(rb"/(?P<key>CreationDate|ModDate) \(D:\d{14}[+-]\d{2}'\d{2}'\)")
_FIXED_TIMESTAMP = b"D:19700101000000+00'00'"
_CHROMIUM_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)


def inline_local_images(svg_path):
    """Embed relative raster references, which a data-URI SVG page cannot resolve."""
    svg_path = Path(svg_path)

    def replace(match):
        relative = match.group("path")
        if relative.startswith(("data:", "http://", "https://")):
            return match.group(0)
        image = (svg_path.parent / relative).resolve()
        mime = mimetypes.guess_type(image.name)[0] or "application/octet-stream"
        payload = base64.b64encode(image.read_bytes()).decode("ascii")
        return f'{match.group("attr")}="data:{mime};base64,{payload}"'

    return _LOCAL_IMAGE.sub(replace, svg_path.read_text(encoding="utf-8")).encode("utf-8")


def normalize_pdf_metadata(path):
    """Replace converter wall-clock timestamps so unchanged figures stay byte-stable."""
    path = Path(path)
    payload = path.read_bytes()
    normalized = _PDF_TIMESTAMP.sub(
        lambda match: b"/" + match.group("key") + b" (" + _FIXED_TIMESTAMP + b")", payload)
    if normalized != payload:
        path.write_bytes(normalized)


def find_chromium():
    override = os.environ.get(CHROMIUM_ENV)
    candidates = [override] if override else []
    candidates += list(_CHROMIUM_PATHS[:2])
    candidates += [shutil.which(name) for name in ("chrome", "msedge", "chromium")]
    candidates += list(_CHROMIUM_PATHS[2:])
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise RuntimeError(f"No Chromium browser found; set {CHROMIUM_ENV} to chrome.exe or msedge.exe")


def svg_to_pdf(svg_path, pdf_path=None, *, preview_dir=None):
    """Print an SVG to a PDF page of its viewBox size; optionally save 3x and 1x PNG previews."""
    svg_path = Path(svg_path).resolve()
    pdf_path = Path(pdf_path).resolve() if pdf_path else svg_path.with_suffix(".pdf")
    svg = inline_local_images(svg_path)
    match = _VIEWBOX.search(svg)
    require(match is not None, f"{svg_path} needs a viewBox of the form '0 0 width height'")
    width, height = (round(float(match.group(key))) for key in ("width", "height"))
    payload = base64.b64encode(svg).decode("ascii")
    html = (f'<!doctype html><meta charset="utf-8"><style>@page{{size:{width}px {height}px;margin:0}}'
            f'html,body{{width:{width}px;height:{height}px;margin:0;overflow:hidden}}'
            f'img{{display:block;width:{width}px;height:{height}px}}</style>'
            f'<img src="data:image/svg+xml;base64,{payload}">')
    browser = find_chromium()
    with tempfile.TemporaryDirectory(prefix="se3wam-figure-") as temporary:
        temporary = Path(temporary)
        page = temporary / "figure.html"
        page.write_text(html, encoding="utf-8")
        common = [str(browser), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                  f"--user-data-dir={temporary / 'profile'}"]
        commands = [common + [f"--print-to-pdf={pdf_path}", page.as_uri()]]
        previews = []
        if preview_dir is not None:
            preview_dir = Path(preview_dir).resolve()
            preview_dir.mkdir(parents=True, exist_ok=True)
            for suffix, scale in (("", 3), ("_actual_size", 1)):
                preview = preview_dir / f"{svg_path.stem}{suffix}.png"
                previews.append(preview)
                commands.append(common + [f"--force-device-scale-factor={scale}",
                                          f"--window-size={width},{height}",
                                          f"--screenshot={preview}", page.as_uri()])
        pdf_path.unlink(missing_ok=True)
        for command in commands:
            completed = subprocess.run(command, capture_output=True, text=True,
                                       encoding="utf-8", errors="replace")
            require(completed.returncode == 0,
                    f"Chromium failed for {svg_path.name}: {completed.stderr.strip()}")
    for output in [pdf_path, *previews]:
        require(output.is_file() and output.stat().st_size > 0, f"missing render output {output}")
    normalize_pdf_metadata(pdf_path)
    return pdf_path


def figure_parser(description, *, extract=False):
    """Argument parser shared by the figure scripts."""
    parser = argparse.ArgumentParser(description=description)
    add_research_argument(parser)
    if extract:
        parser.add_argument("--extract", action="store_true",
                            help="re-read Research before plotting; otherwise use the adjacent data")
    return parser
