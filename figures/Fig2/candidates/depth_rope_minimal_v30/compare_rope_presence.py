"""Compare full Fig. 3 with/without its RoPE annotation, keeping the model unchanged."""

import importlib.util
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import fitz
import numpy as np


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
    master = FIG / "fig2_se3wam.pptx"
    original_bytes = [path.read_bytes() for path in [current_pptx, current_pdf, master]]
    with ZipFile(current_pptx) as deck:
        entries = [(info, deck.read(info.filename)) for info in deck.infolist()]
    raw = next(data for info, data in entries if info.filename == "ppt/slides/slide1.xml")
    for _, (prefix, uri) in ET.iterparse(BytesIO(raw), events=["start-ns"]):
        if not (prefix.startswith("ns") and prefix[2:].isdigit()):
            ET.register_namespace(prefix, uri)
    slide = ET.fromstring(raw)
    tree = slide.find("p:cSld/p:spTree", NS)
    annotation = next(node for node in tree if node.find(".//p:cNvPr", NS) is not None
                      and node.find(".//p:cNvPr", NS).get("name") == "Depth-RoPE preview: patch QK annotation")
    assert {node.find("p:nvSpPr/p:cNvPr", NS).get("name")
            for node in annotation.findall("p:sp", NS)} == TARGETS
    tree.remove(annotation)

    with TemporaryDirectory(prefix=".rope_presence_compare_", dir=HERE) as directory:
        staging = Path(directory)
        assert staging.resolve().parent == HERE.resolve()
        with ZipFile(staging / "fig2_se3wam.pptx", "w") as deck:
            for info, data in entries:
                deck.writestr(info, ET.tostring(slide, encoding="utf-8", xml_declaration=True)
                              if info.filename == "ppt/slides/slide1.xml" else data)
        spec = importlib.util.spec_from_file_location("fig3_presence_export", BASE / "build_fig2.py")
        exporter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exporter)
        exporter.ROOT = staging
        exporter.build()
        with fitz.open(staging / "fig2_se3wam.pdf") as without, fitz.open(current_pdf) as current:
            assert without[0].rect == current[0].rect
            before = without[0].get_pixmap(dpi=144, alpha=False)
            after = current[0].get_pixmap(dpi=144, alpha=False)
            shape = (before.height, before.width, 3)
            difference = np.max(abs(np.frombuffer(before.samples, np.uint8).reshape(shape).astype(int)
                                    - np.frombuffer(after.samples, np.uint8).reshape(shape).astype(int)), axis=2)
            outside = np.ones(difference.shape, bool)
            outside[33 * 2:63 * 2 + 1, 206 * 2:219 * 2 + 1] = False
            assert not np.any(difference[outside])

            width, height = current[0].rect.width, current[0].rect.height
            comparison = fitz.open()
            for document, title in [(without, "A  Without RoPE annotation"),
                                    (current, "B  With dark-gray RoPE annotation")]:
                page = comparison.new_page(width=width, height=height + 20)
                page.insert_text((10, 12), title, fontsize=8, fontname="hebo", color=(.12, .12, .12))
                page.show_pdf_page(fitz.Rect(0, 20, width, height + 20), document, 0)
            comparison.save(HERE / "fig3_rope_presence_compare.pdf", garbage=4, deflate=True)
            stacked = fitz.open()
            page = stacked.new_page(width=width, height=2 * (height + 20) + 12)
            page.show_pdf_page(fitz.Rect(0, 0, width, height + 20), comparison, 0)
            page.show_pdf_page(fitz.Rect(0, height + 32, width, 2 * (height + 20) + 12), comparison, 1)
            page.get_pixmap(dpi=144, alpha=False).save(HERE / "fig3_rope_presence_compare.png")
            stacked.close()
            comparison.close()
    assert [path.read_bytes() for path in [current_pptx, current_pdf, master]] == original_bytes
    print(json.dumps({"comparison": "full Fig. 3; without vs with dark-gray RoPE annotation",
                      "same_input_region_and_layout": True,
                      "changed_pixels_outside_annotation_region": 0,
                      "current_candidate_and_master_unchanged": True}))


if __name__ == "__main__":
    main()
