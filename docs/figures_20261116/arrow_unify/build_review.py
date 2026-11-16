"""Build the 1:1 overview and 600 dpi / 3x before-after arrow contact sheet."""
from pathlib import Path
import argparse
import importlib.util
import io
import json
import math
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image
import pymupdf as fitz
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
import motion_arrow as motion


def load_module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def records():
    f4 = load_module("fig4_restyle", "figures/Fig4/restyle_motion_arrows.py")
    data = (ROOT / "figures/Fig4/ontimebench.svg").read_bytes()
    assert f4.restyle(data)[0] == data
    items = f4.restyle(data)[1]
    for a in items:
        a["figure"] = 4
    f6 = load_module("fig6_build", "figures/Fig6/build_figure.py")
    manifest = json.loads((ROOT / "figures/Fig6/outputs/single-column/fig6.json").read_text())
    for i, a in enumerate(manifest["motion_arrows"]):
        points = a["centerline_pt"]
        length = motion.path_length(points)
        items.append({"id": f"F6-{i+1:02d}", "figure": 6, "label": f6.TASKS[a["task"]],
                      "original_centerline_pt": points, "centerline_pt": points,
                      "original_path_length_pt": length, "path_length_pt": length,
                      "head_length_pt": a["head_length_pt"], "head_width_pt": motion.head_width(a["head_length_pt"]),
                      "double_headed": a["double_headed"], "color": motion.MOTION_COLOR,
                      "scaled": a["head_length_pt"] < motion.HEAD_LEN - 1e-8,
                      "tail_extension_pt": 0., "tip_retreat_pt": 0., "head_only": False,
                      "free_end_extension_pt": 0., "relocation_pt": [0., 0.],
                      "head_fraction": a["head_length_pt"] / (length / (2 if a["double_headed"] else 1))})
    assert len(items) == 29
    return items


def run(base):
    tmp = ROOT / "tmp/arrow_unify"
    before = tmp / "before"
    before.mkdir(parents=True, exist_ok=True)
    sources = {4: ROOT / "figures/Fig4/ontimebench.pdf",
               6: ROOT / "figures/Fig6/outputs/single-column/fig6.pdf"}
    images = {}
    for fig, path in sources.items():
        previous = before / f"Fig{fig}.pdf"
        previous.write_bytes(subprocess.check_output(["git", "show", f"{base}:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT))
        for stage, pdf in [("before", previous), ("after", path)]:
            prefix = tmp / f"{stage}{fig}_600"
            subprocess.run([shutil.which("pdftoppm"), "-f", "1", "-singlefile", "-r", "600", "-png",
                            str(pdf), str(prefix)], check=True, capture_output=True)
            images[fig, stage] = Image.open(prefix.with_suffix(".png")).convert("RGB")
    pdfmetrics.registerFont(TTFont("Review", "C:/Windows/Fonts/arial.ttf"))
    pdfmetrics.registerFont(TTFont("ReviewBold", "C:/Windows/Fonts/arialbd.ttf"))
    sheet = canvas.Canvas(str(OUT / "arrow_contact_sheet.pdf"), pagesize=(792, 420), invariant=True)
    sheet.setTitle("Fig. 4 / Fig. 6 unified motion arrows")
    def text(x, y, value, size=10, bold=False):
        sheet.setFont("ReviewBold" if bold else "Review", size)
        sheet.setFillColorRGB(.1, .13, .18)
        sheet.drawString(x, y, value)
    text(20, 390, "Unified motion arrows / final print size 1:1", 17, True)
    text(20, 369, "Print at 100%. Fig. 4: 495 x 236 pt; Fig. 6: 236.25 x 202.2265625 pt.", 10)
    text(20, 347, "Fig. 4", 12, True)
    text(535, 347, "Fig. 6", 12, True)
    sheet.drawImage(ImageReader(images[4, "after"]), 20, 100, width=495, height=236)
    sheet.drawImage(ImageReader(images[6, "after"]), 535, 336-202.2265625, width=236.25, height=202.2265625)
    text(20, 70, f"Shaft {motion.SHAFT:.2f} pt; head {motion.HEAD_LEN:.1f} x {motion.HEAD_W:.1f} pt; rim {motion.RIM:.2f} pt per side.")
    text(20, 52, "23 Fig. 4 arrows (21 blue + 2 black) and 6 Fig. 6 arrows. Before: main at " + base + ".", 9)
    text(20, 34, "All details: 600 dpi source raster, shown at exactly 3x the printed size. Dimensions below are print pt.", 9)
    sheet.showPage()
    items = records()
    for i, a in enumerate(items):
        slot = i % 4
        if slot == 0:
            sheet.setPageSize((792, 740))
            text(20, 709, "Arrow details / before and after", 16, True)
        top = 675 - slot * 158
        outline = motion.arrow_outline(a["centerline_pt"], double_headed=a["double_headed"], head_len=a["head_length_pt"])
        pts = np.vstack([outline, a["original_centerline_pt"]])
        low, high = pts.min(axis=0) - 5, pts.max(axis=0) + 5
        if high[1] - low[1] < 22:
            mid = (low[1] + high[1]) / 2
            low[1], high[1] = mid - 11, mid + 11
        rect = fitz.Rect(*low, *high) & fitz.open(sources[a["figure"]])[0].rect
        # Integer source pixels determine the displayed physical dimensions.
        box = (math.floor(rect.x0*600/72), math.floor(rect.y0*600/72),
               math.ceil(rect.x1*600/72), math.ceil(rect.y1*600/72))
        a["crop_pt"] = [v * 72 / 600 for v in box]
        text(20, top, f"{a['id']}   {a['label']}", 11, True)
        text(20, top-16, f"Head {a['head_length_pt']:.3f} x {a['head_width_pt']:.3f} pt; path {a['path_length_pt']:.3f} pt; head share {100*a['head_fraction']:.1f}%" + (" of half path" if a['double_headed'] else ""), 9)
        flags = (f"shrink: {'yes' if a['scaled'] else 'no'}; tail extension: {a['tail_extension_pt']:.3f} pt; "
                 f"tip retreat: {a['tip_retreat_pt']:.3f} pt; head only: {'yes' if a['head_only'] else 'no'}")
        if a["free_end_extension_pt"]:
            flags += f"; free end +{a['free_end_extension_pt']:.3f}"
        if any(a["relocation_pt"]):
            flags += "; move (" + ", ".join(f"{v:+.3f}" for v in a["relocation_pt"]) + ")"
        text(20, top-30, flags, 8)
        for stage, x in [("before", 40), ("after", 420)]:
            text(x, top-46, stage.capitalize(), 9, True)
            crop = images[a["figure"], stage].crop(box)
            w, h = crop.width * 72 / 600 * 3, crop.height * 72 / 600 * 3
            sheet.drawImage(ImageReader(crop), x, top-54-h, width=w, height=h)
            crop.save(tmp / f"{a['id']}_{stage}.png")
        if slot == 3 or i == len(items)-1:
            text(20, 15, f"600 dpi crops, 3x print size | {i//4 + 2}", 8)
            sheet.showPage()
    sheet.save()
    (OUT / "measurements.json").write_text(json.dumps({"baseline": base, "style": motion.style_manifest(), "arrows": items}, indent=2) + "\n", encoding="utf-8")
    pdf = fitz.open(OUT / "arrow_contact_sheet.pdf")
    for i, page in enumerate(pdf):
        page.get_pixmap(dpi=120).save(tmp / f"contact-{i+1:02d}.png")
    print(json.dumps({"arrows": len(items), "pages": len(pdf), "contact_sheet": str(OUT / "arrow_contact_sheet.pdf")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="438c4e4", help="Main before this task")
    run(parser.parse_args().base)
