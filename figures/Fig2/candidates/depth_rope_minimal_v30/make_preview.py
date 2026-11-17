"""Keep RGB-D, the short depth-to-cloud arrow, and unlabelled ordinary anchors."""

import importlib.util
from io import BytesIO
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import fitz
import numpy as np


HERE = Path(__file__).resolve().parent
FIG = HERE.parents[1]
PREVIOUS = HERE.parent / "depth_rope_simple_v29"
BASE = HERE.parent / "depth_rope_v28" / "base_v27"
UNIT = 15240000 / 495
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


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

    def transform(shape):
        return shape.find("p:spPr/a:xfrm", NS)

    def position(shape, x, y, width=None, height=None):
        tr = transform(shape)
        tr.find("a:off", NS).attrib.update(x=str(round(x * UNIT)), y=str(round(y * UNIT)))
        extent = tr.find("a:ext", NS)
        if width is not None:
            extent.set("cx", str(round(width * UNIT)))
        if height is not None:
            extent.set("cy", str(round(height * UNIT)))

    def move(shape, dx, dy):
        offset = transform(shape).find("a:off", NS)
        position(shape, int(offset.get("x")) / UNIT + dx, int(offset.get("y")) / UNIT + dy)

    thumbnails = {"4": (44.5, 34.5, 20, 20), "5": (44.5, 34.5, 20, 20),
                  "6": (66.5, 34.5, 20, 20), "7": (66.5, 34.5, 20, 20)}
    for shape in tree:
        nv = shape.find(".//p:cNvPr", NS)
        if nv is not None and nv.get("id") in thumbnails:
            position(shape, *thumbnails[nv.get("id")])
    group = next(n for n in tree if n.find(".//p:cNvPr", NS) is not None
                 and n.find(".//p:cNvPr", NS).get("name") == "Depth-RoPE preview: input geometry")
    removed = []
    for shape in list(group):
        nv = shape.find(".//p:cNvPr", NS)
        if nv is None:
            continue
        name = nv.get("name")
        if (name in {"RGB thumbnail label", "Depth thumbnail label", "3D anchors label",
                     "Selected depth patch center", "Depth patch index i",
                     "3D anchor x_i", "Selected anchor leader"}
                or name.startswith("Selected 3D patch anchor ")):
            group.remove(shape)
            removed.append(name)
        elif name.startswith(("Recorded context point ", "Recorded patch anchor ")):
            move(shape, -1.0, 2.3)
        elif name == "Depth to recorded anchors head":
            move(shape, -2.4, 2.5)
        elif name == "Depth to recorded anchors":
            position(shape, 88.0, 44.5, width=92.8 - 1.5 * .72 - 88.0)
        if name in {"Depth to recorded anchors", "Depth to recorded anchors head"}:
            for ink in shape.findall(".//a:srgbClr", NS):
                ink.set("val", "6E6E6E")
    assert len(removed) == 8
    rope_label = next(node for node in tree.findall(".//p:sp", NS)
                      if node.find("p:nvSpPr/p:cNvPr", NS).get("name") == "Patch QK-only 3D RoPE")
    paragraph = rope_label.find("p:txBody/a:p", NS)
    runs = paragraph.findall("a:r", NS)
    runs[0].find("a:t", NS).text = "3D RoPE"
    for run in runs[1:]:
        paragraph.remove(run)
    # Keep the original box, font, and rotation; align the short label by its arrow.
    paragraph.find("a:pPr", NS).set("algn", "r")
    for node in tree.findall(".//p:sp", NS):
        name = node.find("p:nvSpPr/p:cNvPr", NS).get("name")
        if name in {"Patch QK-only 3D RoPE", "RoPE selects the visual patch QK",
                    "RoPE selects the visual patch QK head"}:
            for ink in node.findall(".//a:srgbClr", NS):
                ink.set("val", "6E6E6E")
    candidate = HERE / "fig2_se3wam.pptx"
    with ZipFile(candidate, "w") as deck:
        for info, data in entries:
            deck.writestr(info, ET.tostring(slide, encoding="utf-8", xml_declaration=True)
                          if info.filename == "ppt/slides/slide1.xml" else data)

    helper = load_module(PREVIOUS / "make_preview.py", "fig3_previous_preview")
    original_objects = helper.named_children(helper.read_slide(BASE / "fig2_se3wam.pptx"))
    current_objects = helper.named_children(slide)
    changed = [identity for identity, node in original_objects.items()
               if ET.tostring(node) != ET.tostring(current_objects[identity])]
    assert sorted(changed) == ["4", "5", "6", "7"]
    exporter = load_module(BASE / "build_fig2.py", "fig3_native_export")
    exporter.ROOT = HERE
    exporter.build()
    export_report = json.loads((HERE / "export_report.json").read_text())
    export_report["release"] = "v27-depth-rope-minimal-input-preview"
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
    for x0, y0, x1, y1 in [(43, 29, 121, 60), (196, 33, 219, 86)]:
        outside[int(y0 * 2):int(y1 * 2) + 1, int(x0 * 2):int(x1 * 2) + 1] = False
    assert not np.any(difference[outside])
    assert master.read_bytes() == master_before
    assert list(original[0].rect) == list(current[0].rect)
    report = {"status": "local candidate, not adopted", "base": "v27",
              "change_from_v29": "RGB-D moved left and centered; bottom captions, point labels, highlights and leader removed",
              "removed_objects": removed, "changed_original_objects": changed,
              "depth_arrow_color": "#6E6E6E",
              "rope_annotation": "3D RoPE",
              "rope_annotation_and_arrow_color": "#6E6E6E",
              "changed_pixels_outside_input_and_rope_regions": 0,
              "paper_size_pt": [original[0].rect.width, original[0].rect.height],
              "master_unchanged": True,
              "data": {key: value for key, value in json.loads((PREVIOUS / "preview_check.json").read_text())["data"].items()
                       if not key.startswith("selected_")}}
    (HERE / "preview_check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    helper.HERE = HERE
    helper.comparison(previous, current, "Before: previous local preview", "local_before_after")
    helper.comparison(original, current, "Before: original v27", "v27_before_after")
    current[0].get_pixmap(dpi=360, alpha=False, clip=fitz.Rect(8, 24, 160, 64)).save(HERE / "input_detail.png")
    current[0].get_pixmap(dpi=360, alpha=False, clip=fitz.Rect(168, 28, 243, 117)).save(HERE / "qk_rope_detail.png")
    full = fitz.open()
    full.insert_pdf(original)
    full.insert_pdf(current)
    full.save(HERE / "before_after.pdf", garbage=4, deflate=True)
    print(json.dumps(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
