"""Validate the actual arrow artifacts and unchanged manuscript pagination."""
from pathlib import Path
import ast
import importlib.util
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import motion_arrow as m


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def baseline(path, revision="438c4e4"):
    return subprocess.check_output(["git", "show", revision + ":" + path], cwd=ROOT)


def path_coordinates(d):
    return np.array([float(v) for v in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)]).reshape(-1, 2)


def constant(source, name):
    return next(ast.literal_eval(n.value) for n in ast.parse(source).body
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


def assert_simple_polygon(points):
    # Check actual non-adjacent edges independently of the author's union code.
    def side(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    for i in range(len(points)-1):
        for j in range(i+2, len(points)-1):
            if i == 0 and j == len(points)-2:
                continue
            a, b, c, d = points[i], points[i+1], points[j], points[j+1]
            assert not (side(a,b,c)*side(a,b,d) < -1e-10 and side(c,d,a)*side(c,d,b) < -1e-10)


def type3_glyphs(document):
    fonts = {font[0] for p in document for font in p.get_fonts() if font[2] == "Type3"}
    result = []
    for ref in fonts:
        kind, value = document.xref_get_key(ref, "CharProcs")
        if kind == "xref":
            value = document.xref_object(int(value.split()[0]))
        result.append(sorted(document.xref_stream(int(n)) for n in re.findall(r"\s(\d+) 0 R", value)))
    return sorted(result)


def run():
    data = json.loads(Path(__file__).with_name("measurements.json").read_text())
    assert data["style"] == m.style_manifest()
    arrows = data["arrows"]
    assert len(arrows) == 27
    for a in arrows:
        p = np.array(a["centerline_pt"])
        outline = m.arrow_outline(p, double_headed=a["double_headed"], head_len=a["head_length_pt"])
        assert np.isfinite(outline).all() and np.array_equal(outline[0], outline[-1]), a["id"]
        assert_simple_polygon(outline)
        assert a["head_length_pt"] >= m.HEAD_MIN
        assert a["head_fraction"] <= m.HEAD_FRACTION + 1e-9, a["id"]
        assert abs(m.path_length(p) - a["path_length_pt"]) < 1e-8
        for reverse in [False, True] if a["double_headed"] else [False]:
            q = p[::-1] if reverse else p
            head, direction = m.head_vertices(q, a["head_length_pt"])
            chord = q[-1] - m.point_at(q, m.path_length(q) - a["head_length_pt"])
            assert np.allclose(direction, chord / np.linalg.norm(chord))
            assert np.allclose(head[1], q[-1])
            assert np.min(np.linalg.norm(outline-q[-1], axis=1)) < 1e-7
            assert np.isclose(np.linalg.norm(head[0] - head[2]), a["head_width_pt"])
    restyle = module("restyle", "figures/Fig4/restyle_motion_arrows.py")
    f4 = ROOT / "figures/Fig4/ontimebench.svg"
    current = f4.read_bytes()
    # Use Git's checkout filter so this literal-byte check also works in the
    # Windows main checkout (core.autocrlf=true), without normalizing the SVG.
    source = subprocess.check_output(["git", "cat-file", "--filters", "438c4e4:figures/Fig4/ontimebench.svg"], cwd=ROOT)
    generated, _ = restyle.restyle(source)
    assert generated == current  # includes exact non-arrow byte comparison
    assert restyle.restyle(current)[0] == current
    # The follow-up changes only the two redundant arrow groups. Every retained
    # arrow group and every other SVG byte must match the pre-simplification main.
    previous = subprocess.check_output(["git", "cat-file", "--filters",
        data["baseline"] + ":figures/Fig4/ontimebench.svg"], cwd=ROOT)
    old_nodes = list(ET.fromstring(previous).iter())
    old_spans = restyle.element_spans(previous)
    deleted = [old_spans[i] for i, n in enumerate(old_nodes) if n.get("id") in restyle.OMITTED_IDS]
    assert len(deleted) == 2 and restyle.erase_spans(previous, deleted) == current
    for panel, expected in [("panel-grasp", {"F4-02"}), ("panel-t1_so3", {"F4-06", "F4-08"})]:
        node = next(n for n in ET.fromstring(current).iter() if n.get("id") == panel)
        assert {n.get("id") for n in node.iter() if n.get("data-motion-arrow") == m.STYLE} == expected
    # Metadata must not become a second source of global geometry settings.
    original = m.HEAD_LEN, m.HEAD_W
    try:
        m.HEAD_LEN, m.HEAD_W = 4.2, 4.0
        updated, changes = restyle.restyle(current)
        assert changes[0]["head_length_pt"] == 4.2
        assert restyle.restyle(updated)[0] == updated
    finally:
        m.HEAD_LEN, m.HEAD_W = original
    paths = [f4, ROOT / "figures/Fig6/outputs/single-column/fig6.svg"]
    groups = []
    for path in paths:
        groups.extend(n for n in ET.parse(path).getroot().iter() if n.get("data-motion-arrow") == m.STYLE)
    assert len(groups) == 27
    for a, group in zip(arrows, groups):
        p = json.loads(group.get("data-centerline"))
        expected = m.arrow_outline(p, double_headed=a["double_headed"], head_len=a["head_length_pt"])
        rim, core = list(group)
        assert rim.get("d") == core.get("d")
        assert np.allclose(path_coordinates(core.get("d")), expected, atol=1e-7, rtol=0)
        assert rim.get("stroke") == "#FFFFFF" and float(rim.get("stroke-width")) == 2*m.RIM
        assert rim.get("stroke-linejoin") == "round" and rim.get("opacity") is None
        assert core.get("fill") == a["color"] and core.get("stroke") is None
    f6_source = ROOT / "figures/Fig6/build_figure.py"
    assert constant(baseline("figures/Fig6/build_figure.py"), "MOTION_PATHS") == constant(f6_source.read_bytes(), "MOTION_PATHS")
    f6 = ROOT / "figures/Fig6/outputs/single-column/fig6.pdf"
    drawings = fitz.open(f6)[0].get_drawings()
    assert len(drawings) == 12
    for i, a in enumerate(arrows[21:]):
        expected = m.arrow_outline(a["centerline_pt"], double_headed=a["double_headed"])
        rim, core = drawings[i*2:i*2+2]
        for drawing in [rim, core]:
            actual = np.array([tuple(drawing["items"][0][1])] + [tuple(item[2]) for item in drawing["items"]])
            assert np.allclose(actual, expected, atol=1e-4, rtol=0)
        assert abs(rim["width"]-2*m.RIM) < 1e-7 and rim["lineJoin"] == 1
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
          "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
    with ZipFile(f6.with_name("Fig6-editable.pptx")) as archive:
        root = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
    groups = root.findall(".//p:grpSp", ns)
    assert len(groups) == 6
    for a, group in zip(arrows[21:], groups):
        expected = m.arrow_outline(a["centerline_pt"], double_headed=a["double_headed"])
        shapes = group.findall("p:sp", ns)
        assert len(shapes) == 2
        for i, shape in enumerate(shapes):
            transform = shape.find("p:spPr/a:xfrm", ns)
            offset = np.array([float(transform.find("a:off", ns).get(k)) for k in ["x", "y"]])
            size = np.array([float(transform.find("a:ext", ns).get(k)) for k in ["cx", "cy"]])
            path = shape.find(".//a:path", ns)
            extent = np.array([float(path.get(k)) for k in ["w", "h"]])
            points = np.array([[float(p.get(k)) for k in ["x", "y"]] for p in path.findall(".//a:pt", ns)])
            actual = (offset + points / extent * size) / (12700 * 3)
            assert np.allclose(actual, expected, atol=.0006, rtol=0)
            if i == 0:
                line = shape.find("p:spPr/a:ln", ns)
                assert float(line.get("w"))/(12700*3) == 2*m.RIM
                assert line.find("a:round", ns) is not None
    for fig, size in [(f4.with_suffix(".pdf"), (495, 236)), (f6, (236.25, 202.2265625))]:
        doc = fitz.open(fig)
        assert len(doc) == 1 and np.allclose(doc[0].rect[2:], size)
        assert not any(f[2] == "Type3" for f in doc[0].get_fonts())
    assert all("Arial" in font[3] for font in fitz.open(f4.with_suffix(".pdf"))[0].get_fonts())
    before = fitz.open(stream=baseline("main.pdf", data["baseline"]), filetype="pdf")
    after = fitz.open(ROOT / "main.pdf")
    assert len(before) == len(after)
    for a, b in zip(before, after):
        assert a.rect == b.rect and a.get_text("words") == b.get_text("words")
    assert type3_glyphs(before) == type3_glyphs(after)
    assert len(fitz.open(Path(__file__).with_name("arrow_contact_sheet.pdf"))) == 9
    print(f"PASS: 27 arrows; only F4-03 and F4-07 removed; exact non-arrow bytes; byte-idempotence; global parameter propagation; unchanged MOTION_PATHS; SVG/PDF/PPTX geometry; sizes and Arial; main {len(after)} pages and identical word placement; existing Type 3 glyphs unchanged.")


if __name__ == "__main__":
    run()
