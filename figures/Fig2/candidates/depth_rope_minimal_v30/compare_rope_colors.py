"""Render matched blue/gray RoPE crops without changing the current candidate."""

import importlib.util
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import fitz


HERE = Path(__file__).resolve().parent
FIG = HERE.parents[1]
BASE = HERE.parent / "depth_rope_v28" / "base_v27"
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
TARGETS = {"Patch QK-only 3D RoPE", "RoPE selects the visual patch QK",
           "RoPE selects the visual patch QK head"}


def main():
    current_pptx = HERE / "fig2_se3wam.pptx"
    current_pdf = HERE / "fig2_se3wam.pdf"
    source_before, pdf_before = current_pptx.read_bytes(), current_pdf.read_bytes()
    with ZipFile(current_pptx) as deck:
        entries = [(info, deck.read(info.filename)) for info in deck.infolist()]
    raw = next(data for info, data in entries if info.filename == "ppt/slides/slide1.xml")
    for _, (prefix, uri) in ET.iterparse(BytesIO(raw), events=["start-ns"]):
        if not (prefix.startswith("ns") and prefix[2:].isdigit()):
            ET.register_namespace(prefix, uri)
    slide = ET.fromstring(raw)
    selected = []
    for shape in slide.findall(".//p:sp", NS):
        name = shape.find("p:nvSpPr/p:cNvPr", NS).get("name")
        if name in TARGETS:
            for color in shape.findall(".//a:srgbClr", NS):
                assert color.get("val") == "6E6E6E"
                color.set("val", "2859A3")
            selected.append(name)
    assert set(selected) == TARGETS

    with TemporaryDirectory(prefix=".rope_color_compare_", dir=HERE) as directory:
        staging = Path(directory)
        assert staging.resolve().parent == HERE.resolve()
        with ZipFile(staging / "fig2_se3wam.pptx", "w") as deck:
            for info, data in entries:
                deck.writestr(info, ET.tostring(slide, encoding="utf-8", xml_declaration=True)
                              if info.filename == "ppt/slides/slide1.xml" else data)
        spec = importlib.util.spec_from_file_location("fig3_color_export", BASE / "build_fig2.py")
        exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exporter)
        exporter.ROOT = staging
        exporter.build()
        with fitz.open(staging / "fig2_se3wam.pdf") as blue, fitz.open(current_pdf) as gray:
            assert blue[0].rect == gray[0].rect
            comparison = fitz.open()
            clip = fitz.Rect(171, 28, 243, 117)
            page = comparison.new_page(width=162, height=110)
            for document, x, title, color in [(blue, 5, "Before: blue", "#2859A3"),
                                               (gray, 85, "After: dark gray", "#6E6E6E")]:
                page.insert_text((x, 7), title, fontsize=6.5, fontname="hebo", color=(.12, .12, .12))
                page.insert_text((x, 13), color, fontsize=5.7, color=(.35, .35, .35))
                page.show_pdf_page(fitz.Rect(x, 16, x + 72, 105), document, 0, clip=clip)
            comparison.save(HERE / "qk_rope_color_compare.pdf", garbage=4, deflate=True)
            page.get_pixmap(dpi=360, alpha=False).save(HERE / "qk_rope_color_compare.png")
            comparison.close()
    assert current_pptx.read_bytes() == source_before
    assert current_pdf.read_bytes() == pdf_before
    print(json.dumps({"comparison": "blue vs dark gray; identical crop and scale",
                      "only_difference": "RoPE text and arrow color", "candidate_unchanged": True}))


if __name__ == "__main__":
    main()
