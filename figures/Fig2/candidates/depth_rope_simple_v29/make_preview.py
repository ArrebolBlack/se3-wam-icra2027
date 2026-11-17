"""Simplify the v27-derived preview by removing its explicit geometry wiring."""

from io import BytesIO
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import fitz
import numpy as np


HERE = Path(__file__).resolve().parent
FIG = HERE.parents[1]
PREVIOUS = HERE.parent / "depth_rope_v28"
BASE = PREVIOUS / "base_v27"
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
REMOVE = {
    "RGB-only encoder input", "RGB-only encoder input head",
    "Vision feature to sum", "Depth geometry branch", "Anchor geometry branch",
    "Depth and position embeddings", "Visual token additive fusion",
    "Visual token sum horizontal", "Visual token sum vertical",
    "Geometry-aware visual token", "Geometry-aware visual token head",
}


def read_slide(path):
    with ZipFile(path) as deck:
        return ET.fromstring(deck.read("ppt/slides/slide1.xml"))


def named_children(slide):
    return {n.find(".//p:cNvPr", NS).get("id"): n
            for n in slide.find("p:cSld/p:spTree", NS)
            if n.find(".//p:cNvPr", NS) is not None}


def comparison(first, second, title, prefix):
    panels = [(fitz.Rect(8, 17, 160, 66), fitz.Rect(9, 16, 161, 65)),
              (fitz.Rect(195.5, 31, 221, 87), fitz.Rect(177, 13, 202.5, 69))]
    pages = fitz.open()
    for document, label in [(first, title), (second, "After: simplified depth anchors and RoPE")]:
        page = pages.new_page(width=212, height=77)
        page.insert_text((9, 8), label, fontsize=6.5, fontname="hebo", color=(.12, .12, .12))
        page.insert_text((182, 8), "Q/K/V", fontsize=5.5, color=(.35, .35, .35))
        for clip, destination in panels:
            page.show_pdf_page(destination, document, 0, clip=clip)
    pages.save(HERE / f"{prefix}.pdf", garbage=4, deflate=True)
    stacked = fitz.open()
    page = stacked.new_page(width=212, height=158)
    page.show_pdf_page(fitz.Rect(0, 0, 212, 77), pages, 0)
    page.show_pdf_page(fitz.Rect(0, 81, 212, 158), pages, 1)
    page.get_pixmap(dpi=300).save(HERE / f"{prefix}.png")


def main():
    master = FIG / "fig2_se3wam.pptx"
    master_before = master.read_bytes()
    with ZipFile(PREVIOUS / "fig2_se3wam.pptx") as deck:
        entries = [(info, deck.read(info.filename)) for info in deck.infolist()]
    raw = next(data for info, data in entries if info.filename == "ppt/slides/slide1.xml")
    for _, (prefix, uri) in ET.iterparse(BytesIO(raw), events=["start-ns"]):
        if not (prefix.startswith("ns") and prefix[2:].isdigit()):
            ET.register_namespace(prefix, uri)
    slide = ET.fromstring(raw)
    tree = slide.find("p:cSld/p:spTree", NS)
    group = next(n for n in tree if n.find(".//p:cNvPr", NS) is not None
                 and n.find(".//p:cNvPr", NS).get("name") == "Depth-RoPE preview: input geometry")
    removed = []
    for child in list(group):
        nv = child.find(".//p:cNvPr", NS)
        if nv is not None and nv.get("name") in REMOVE:
            removed.append(nv.get("name"))
            group.remove(child)
    assert set(removed) == REMOVE, removed
    changed_original = [identity for identity, node in named_children(read_slide(BASE / "fig2_se3wam.pptx")).items()
                        if ET.tostring(node) != ET.tostring(named_children(slide)[identity])]
    assert sorted(changed_original) == ["4", "5", "6", "7"], changed_original
    modified = ET.tostring(slide, encoding="utf-8", xml_declaration=True)
    with ZipFile(HERE / "fig2_se3wam.pptx", "w") as deck:
        for info, data in entries:
            deck.writestr(info, modified if info.filename == "ppt/slides/slide1.xml" else data)

    spec = importlib.util.spec_from_file_location("fig3_native_export", BASE / "build_fig2.py")
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    exporter.ROOT = HERE
    exporter.build()
    export_report = json.loads((HERE / "export_report.json").read_text())
    export_report["release"] = "v27-depth-rope-simplified-preview"
    (HERE / "export_report.json").write_text(json.dumps(export_report, indent=2) + "\n")

    original = fitz.open(BASE / "fig2_se3wam.pdf")
    previous = fitz.open(PREVIOUS / "fig2_se3wam.pdf")
    current = fitz.open(HERE / "fig2_se3wam.pdf")
    a = original[0].get_pixmap(dpi=144, alpha=False)
    b = current[0].get_pixmap(dpi=144, alpha=False)
    shape = (a.height, a.width, 3)
    difference = np.max(abs(np.frombuffer(a.samples, np.uint8).reshape(shape).astype(int)
                            - np.frombuffer(b.samples, np.uint8).reshape(shape).astype(int)), axis=2)
    outside = np.ones(difference.shape, bool)
    for x0, y0, x1, y1 in [(44, 29, 121, 60), (196, 33, 219, 86)]:
        outside[int(y0 * 2):int(y1 * 2) + 1, int(x0 * 2):int(x1 * 2) + 1] = False
    assert not np.any(difference[outside])
    assert master.read_bytes() == master_before
    assert list(original[0].rect) == list(current[0].rect)
    report = {
        "status": "local candidate, not adopted",
        "base": "v27; simplified from the first Depth/RoPE preview",
        "removed_objects": removed,
        "changed_original_objects": changed_original,
        "retained": ["Depth to recorded 3D patch anchors", "matched patch i and x_i",
                     "Q/K-only RoPE annotation on the blue visual patch token"],
        "changed_pixels_outside_input_and_rope_regions": 0,
        "paper_size_pt": [original[0].rect.width, original[0].rect.height],
        "master_unchanged": True,
        "data": json.loads((PREVIOUS / "preview_check.json").read_text())["data"],
    }
    (HERE / "preview_check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    comparison(previous, current, "Before: first Depth/RoPE preview", "local_before_after")
    comparison(original, current, "Before: original v27", "v27_before_after")
    full = fitz.open()
    full.insert_pdf(original)
    full.insert_pdf(current)
    full.save(HERE / "before_after.pdf", garbage=4, deflate=True)
    print(json.dumps(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
