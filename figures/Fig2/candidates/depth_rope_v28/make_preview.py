"""Local v27 copy: depth anchors and patch-Q/K RoPE; all other objects stay intact."""

from copy import deepcopy
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
PAPER = FIG.parents[1]
BASE = HERE / "base_v27"
UNIT = 15240000 / 495
BLUE = "2859A3"
GRAY = "6E6E6E"
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def main():
    source = BASE / "fig2_se3wam.pptx"
    master_before = source.read_bytes()
    with ZipFile(source) as deck:
        entries = [(info, deck.read(info.filename)) for info in deck.infolist()]
    parts = {info.filename: data for info, data in entries}
    raw = parts["ppt/slides/slide1.xml"]
    for _, (prefix, uri) in ET.iterparse(BytesIO(raw), events=["start-ns"]):
        if not (prefix.startswith("ns") and prefix[2:].isdigit()):
            ET.register_namespace(prefix, uri)
    slide = ET.fromstring(raw)
    tree = slide.find("p:cSld/p:spTree", NS)
    original = {n.find(".//p:cNvPr", NS).get("id"): deepcopy(n)
                for n in tree if n.find(".//p:cNvPr", NS) is not None}
    draw_module = module(BASE / "update_assets.py", "fig3_native_primitives")
    drawing = draw_module.Drawing(tree)
    add = draw_module.add
    color = draw_module.color

    def group(name):
        g = add(tree, "p:grpSp")
        nv = add(g, "p:nvGrpSpPr")
        add(nv, "p:cNvPr", id=drawing.next_id, name=name)
        drawing.next_id += 1
        add(nv, "p:cNvGrpSpPr")
        add(nv, "p:nvPr")
        transform = add(add(g, "p:grpSpPr"), "a:xfrm")
        for tag, attrs in [("a:off", {"x": 0, "y": 0}),
                           ("a:ext", {"cx": 15240000, "cy": 9048750}),
                           ("a:chOff", {"x": 0, "y": 0}),
                           ("a:chExt", {"cx": 15240000, "cy": 9048750})]:
            add(transform, tag, **attrs)
        return g

    local = group("Depth-RoPE preview: input geometry")
    attention = group("Depth-RoPE preview: patch QK annotation")

    def line(parent, name, points, stroke=BLUE, width=.45, head=0):
        p = np.asarray(points, float)
        if head:
            direction = p[-1] - p[-2]
            direction /= np.linalg.norm(direction)
            normal = np.array([-direction[1], direction[0]])
            tip = p[-1].copy()
            p[-1] = tip - direction * head * .72
            drawing.poly(parent, name + " head",
                         np.array([tip, tip - direction * head + normal * head * .42,
                                   tip - direction * head - normal * head * .42]) * UNIT,
                         fill=stroke)
        drawing.poly(parent, name, p * UNIT, stroke=stroke, width=width * UNIT)

    def dot(parent, name, xy, radius, fill, stroke=None, width=0):
        shape, props = drawing.shape(parent, name,
                                     (np.asarray(xy) - radius) * UNIT,
                                     np.array([2 * radius, 2 * radius]) * UNIT)
        add(add(props, "a:prstGeom", prst="ellipse"), "a:avLst")
        color(props, fill)
        outline = add(props, "a:ln", w=round(width * UNIT))
        color(outline, stroke) if stroke else add(outline, "a:noFill")
        return shape

    def text(parent, name, words, box, size=6, ink=BLUE, rotation=0, white=False):
        x, y, w, h = box
        shape, props = drawing.shape(parent, name, np.array([x, y]) * UNIT,
                                     np.array([w, h]) * UNIT)
        if rotation:
            props.find("a:xfrm", NS).set("rot", str(rotation * 60000))
        add(add(props, "a:prstGeom", prst="rect"), "a:avLst")
        color(props, "FFFFFF") if white else add(props, "a:noFill")
        add(add(props, "a:ln"), "a:noFill")
        body = add(shape, "p:txBody")
        body_props = add(body, "a:bodyPr", wrap="none", lIns=0, tIns=0, rIns=0,
                         bIns=0, anchor="ctr")
        add(body_props, "a:noAutofit")
        add(body, "a:lstStyle")
        paragraph = add(body, "a:p")
        add(paragraph, "a:pPr", algn="ctr")
        for value, subscript, italic in words:
            run = add(paragraph, "a:r")
            attrs = {"lang": "en-US", "sz": round(size * UNIT / 127 * (.75 if subscript else 1)),
                     "i": int(italic)}
            if subscript:
                attrs["baseline"] = -23000
            rp = add(run, "a:rPr", **attrs)
            color(rp, ink)
            add(rp, "a:latin", typeface="Arial")
            add(run, "a:t").text = value
        return shape

    def plain(parent, name, value, box, **kwargs):
        return text(parent, name, [(value, False, False)], box, **kwargs)

    # Only the four existing thumbnail/border objects are repositioned.
    replacements = {"4": (46.5, 33.25, 18.0, 18.0), "5": (46.5, 33.25, 18.0, 18.0),
                    "6": (70.5, 33.25, 18.0, 18.0), "7": (70.5, 33.25, 18.0, 18.0)}
    for element in tree:
        nv = element.find(".//p:cNvPr", NS)
        if nv is not None and nv.get("id") in replacements:
            x, y, w, h = replacements[nv.get("id")]
            transform = element.find("p:spPr/a:xfrm", NS)
            transform.find("a:off", NS).attrib.update(x=str(round(x * UNIT)), y=str(round(y * UNIT)))
            transform.find("a:ext", NS).attrib.update(cx=str(round(w * UNIT)), cy=str(round(h * UNIT)))

    labels = np.load(FIG / "assets/geometry_labels.npz")
    recorded = np.load(PAPER / "figures/Fig1/data/labels.npz")
    depth = np.load(PAPER / "figures/Fig1/data/frame_tau_depth_m.npy")
    camera = json.loads((FIG / "assets/blender/source.json").read_text(encoding="utf-8"))
    right, up = np.array(camera["right"]), np.array(camera["up"])
    cloud = labels["cloud_xyz_world"]
    patch = labels["patch_xyz_world"]
    keep = labels["patch_keep"]
    uv = np.stack([cloud @ right, -cloud @ up], axis=1)
    low, high = uv.min(0), uv.max(0)
    center = (low + high) / 2
    scale = min(22.3 / (high[0] - low[0]), 20.0 / (high[1] - low[1]))
    destination = np.array([107.1, 42.2])

    def project(xyz):
        return (np.stack([xyz @ right, -xyz @ up], axis=-1) - center) * scale + destination

    # The faint surface is context; only the recorded patch centers are blue anchors.
    cloud_uv = project(cloud)
    for index in np.argsort(cloud @ np.array(camera["view"]))[::2]:
        rgb = np.asarray(labels["cloud_rgb"][index], float)
        if rgb.max() <= 1:
            rgb *= 255
        rgb = np.round(.50 * rgb + .50 * 255).astype(int)
        dot(local, f"Recorded context point {index}", cloud_uv[index], .14,
            "".join(f"{v:02X}" for v in rgb))
    patch_uv = project(patch)
    for index in np.flatnonzero(keep):
        dot(local, f"Recorded patch anchor {index}", patch_uv[index], .22,
            "FFFFFF", BLUE, .12)

    # Choose one visible front-surface anchor, and identify its exact depth pixel.
    wanted = np.array([111.2, 47.3])
    valid_indices = np.flatnonzero(keep)
    selected = int(valid_indices[np.argmin(np.linalg.norm(patch_uv[keep] - wanted, axis=1))])
    xy = recorded["source_px_xy"][selected].astype(int)
    depth_point = np.array([70.5, 33.25]) + (xy + .5) / 224 * 18.0
    dot(local, "Selected depth patch center", depth_point, .60, "FFFFFF", BLUE, .28)
    plain(local, "Depth patch index i", "i", [depth_point[0] - 2.0, depth_point[1] - 6.0, 4, 5.5],
          size=5.8)
    anchor = patch_uv[selected]
    dot(local, f"Selected 3D patch anchor {selected}", anchor, .65, BLUE, "FFFFFF", .25)
    label_box = [112.1, 32.1, 6.6, 6.4]
    text(local, "3D anchor x_i", [("x", False, True), ("i", True, True)], label_box, size=6.4)
    line(local, "Selected anchor leader", [[114.6, 38.0], [114.6, 40.0], anchor], width=.35)

    plain(local, "RGB thumbnail label", "RGB", [46.0, 52.3, 19.0, 6.5], size=5.8, ink=GRAY)
    plain(local, "Depth thumbnail label", "Depth", [70.0, 52.3, 19.0, 6.5], size=5.8, ink=GRAY)
    line(local, "Depth to recorded anchors", [[89.3, 42.0], [95.2, 42.0]], head=1.5)

    # RGB goes to the unchanged vision encoder. Geometry joins its output.
    line(local, "RGB-only encoder input", [[55.75, 32.2], [55.75, 20.6], [131.7, 20.6],
                                           [131.7, 30.1]], head=1.6)
    token_y = 26.5689625984252 + 2 * 9.28125 + 8.04375 / 2
    join = np.array([146.4, token_y])
    line(local, "Vision feature to sum", [[143.55, token_y], [145.1, token_y]])
    line(local, "Depth geometry branch", [[88.5, 48.7], [89.7, 48.7], [89.7, 62.0],
                                          [146.4, 62.0], [146.4, token_y + 1.3]])
    line(local, "Anchor geometry branch", [[119.0, 47.8], [119.0, 62.0]], width=.35)
    plain(local, "3D anchors label", "3D anchors", [90.7, 52.3, 29.2, 6.5],
          size=5.7, white=True)
    # The label masks its own short connector, as in the adopted figure's flow-time label.
    text(local, "Depth and position embeddings",
         [("Embed(", False, False), ("d\u0304", False, True), ("i", True, True),
          (", ", False, False), ("x", False, True), ("i", True, True), (")", False, False)],
         [101.0, 58.8, 35, 6.4], size=6, white=True)
    dot(local, "Visual token additive fusion", join, 1.3, "FFFFFF", BLUE, .35)
    line(local, "Visual token sum horizontal", [join + [-.75, 0], join + [.75, 0]], width=.28)
    line(local, "Visual token sum vertical", [join + [0, -.75], join + [0, .75]], width=.28)
    line(local, "Geometry-aware visual token", [[147.8, token_y], [149.4, token_y]], head=1.1)

    # The original Q/K/V column and all representative tokens remain in place.
    # A short leader selects only the blue visual-patch representative.
    text(attention, "Patch QK-only 3D RoPE",
         [("3D RoPE(", False, False), ("x", False, True), ("i", True, True),
          (") · Q,K", False, False)],
         [188.5, 56.8, 51.0, 7.0], size=6.0, rotation=270)
    line(attention, "RoPE selects the visual patch QK", [[210.0, 45.37], [207.65, 45.37]],
         width=.4, head=1.15)

    changed = []
    for element in tree:
        nv = element.find(".//p:cNvPr", NS)
        if nv is not None and nv.get("id") in original:
            identity = nv.get("id")
            if ET.tostring(element) != ET.tostring(original[identity]):
                changed.append(identity)
    assert sorted(changed) == ["4", "5", "6", "7"], changed
    modified = ET.tostring(slide, encoding="utf-8", xml_declaration=True)
    with ZipFile(HERE / "fig2_se3wam.pptx", "w") as deck:
        for info, data in entries:
            deck.writestr(info, modified if info.filename == "ppt/slides/slide1.xml" else data)

    px = recorded["source_px_xy"].astype(int)
    rays = np.linalg.solve(recorded["camera_intrinsics"],
                           np.column_stack([px, np.ones(len(px))]).T).T
    z = depth[px[:, 1], px[:, 0]]
    transform = recorded["world_from_camera_cv"]
    derived = (rays * z[:, None]) @ transform[:3, :3].T + transform[:3, 3]
    error = float(np.max(abs(derived - patch)))
    assert error < 1e-9
    report = {"status": "local candidate, not adopted", "base": "v27 with centered LN labels",
              "changed_existing_object_ids": changed,
              "unchanged_existing_objects": len(original) - len(changed),
              "data": {"patch_points": len(patch), "displayed_anchors": int(keep.sum()),
                       "selected_patch_index": selected, "selected_source_pixel_xy": xy.tolist(),
                       "max_backprojection_difference_m": error},
              "scope": "Current RGB-D thumbnails, input geometry branch, blue patch Q/K RoPE annotation",
              "master_modified": False}
    (HERE / "preview_check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    exporter = module(BASE / "build_fig2.py", "fig3_powerpoint_export")
    exporter.ROOT = HERE
    exporter.build()
    export_report = json.loads((HERE / "export_report.json").read_text())
    export_report["release"] = "v27-depth-rope-local-preview"
    (HERE / "export_report.json").write_text(json.dumps(export_report, indent=2) + "\n")

    # Before/after uses the same PDF renderer and physical scale.
    before = fitz.open(BASE / "fig2_se3wam.pdf")
    after = fitz.open(HERE / "fig2_se3wam.pdf")
    before_pixels = before[0].get_pixmap(dpi=144, alpha=False)
    after_pixels = after[0].get_pixmap(dpi=144, alpha=False)
    pixel_shape = (before_pixels.height, before_pixels.width, 3)
    a = np.frombuffer(before_pixels.samples, np.uint8).reshape(pixel_shape)
    b = np.frombuffer(after_pixels.samples, np.uint8).reshape(pixel_shape)
    difference = np.max(abs(a.astype(int) - b.astype(int)), axis=2)
    outside = np.ones(difference.shape, bool)
    for x0, y0, x1, y1 in [(44, 18, 160, 66), (196, 33, 219, 86)]:
        outside[int(y0 * 2):int(y1 * 2) + 1, int(x0 * 2):int(x1 * 2) + 1] = False
    report["render_check"] = {
        "paper_size_unchanged": list(before[0].rect) == list(after[0].rect),
        "changed_pixels_outside_allowed_regions": int(np.sum((difference > 0) & outside)),
        "master_unchanged": source.read_bytes() == master_before,
    }
    assert report["render_check"]["paper_size_unchanged"]
    assert report["render_check"]["changed_pixels_outside_allowed_regions"] == 0
    assert report["render_check"]["master_unchanged"]
    (HERE / "preview_check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    comparison = fitz.open()
    panels = [(fitz.Rect(8, 17, 160, 66), fitz.Rect(9, 16, 161, 65)),
              (fitz.Rect(195.5, 31.0, 221, 87), fitz.Rect(177, 13, 202.5, 69))]
    for index, (document, title) in enumerate([(before, "Before: v27"),
                                               (after, "After: depth anchors and patch Q/K RoPE")]):
        page = comparison.new_page(width=212, height=77)
        page.insert_text((9, 8), title, fontsize=6.5, fontname="hebo", color=(.12, .12, .12))
        page.insert_text((182, 8), "Q/K/V", fontsize=5.5, fontname="helv", color=(.35, .35, .35))
        for clip, destination in panels:
            page.show_pdf_page(destination, document, 0, clip=clip)
        page.get_pixmap(dpi=300).save(HERE / ("local_before.png" if index == 0 else "local_after.png"))
    comparison.save(HERE / "local_before_after.pdf", garbage=4, deflate=True)
    stacked = fitz.open()
    page = stacked.new_page(width=212, height=158)
    page.show_pdf_page(fitz.Rect(0, 0, 212, 77), comparison, 0)
    page.show_pdf_page(fitz.Rect(0, 81, 212, 158), comparison, 1)
    page.get_pixmap(dpi=300).save(HERE / "local_before_after.png")
    full = fitz.open()
    full.insert_pdf(before)
    full.insert_pdf(after)
    full.save(HERE / "before_after.pdf", garbage=4, deflate=True)
    print(json.dumps(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
