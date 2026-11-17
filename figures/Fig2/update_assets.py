"""Update the adopted Fig. 3 PowerPoint's assets without rebuilding its layout.

Flow is native editable DrawingML, projected from recorded per-step labels in
the saved orthographic view. All other slide objects and all existing text are
preserved. Run this after render_assets.py, then run build_fig2.py to export.
Use --icons-v28 to replace only the five robot icons and two noise patches;
the default illustration update preserves those seven replacements.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np

ROOT = Path(__file__).resolve().parent
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)
EMU_PER_PAPER_PT = 15240000 / 495
TARGET, STATIC = "C0263A", "6E6E6E"
HORIZONS = (0, 3, 7)
# Same sampled matplotlib turbo LUT as Fig. 1(a) and figures/paradigms.
TURBO = (
    '4666dd','4669e0','466be3','476ee6','4771e9','4773eb','4776ee','4778f0','477bf2','467df4',
    '4680f6','4682f8','4685fa','4687fb','458afc','458cfd','448ffe','4391fe','4294ff','4196ff',
    '4099ff','3e9bfe','3d9efe','3ba0fd','3aa3fc','38a5fb','37a8fa','35abf8','33adf7','31aff5',
    '2fb2f4','2eb4f2','2cb7f0','2ab9ee','28bceb','27bee9','25c0e7','23c3e4','22c5e2','20c7df',
    '1fc9dd','1ecbda','1ccdd8','1bd0d5','1ad2d2','1ad4d0','19d5cd','18d7ca','18d9c8','18dbc5',
    '18ddc2','18dec0','18e0bd','19e2bb','19e3b9','1ae4b6','1ce6b4','1de7b2','1fe9af','20eaac',
    '22ebaa','25eca7','27eea4','2aefa1','2cf09e','2ff19b','32f298','35f394','38f491','3cf58e',
    '3ff68a','43f787','46f884','4af880','4ef97d','52fa7a','55fa76','59fb73','5dfc6f','61fc6c',
    '65fd69','69fd66','6dfe62','71fe5f','75fe5c','79fe59','7dff56','80ff53','84ff51','88ff4e',
    '8bff4b','8fff49','92ff47','96fe44','99fe42','9cfe40','9ffd3f','a1fd3d','a4fc3c','a7fc3a',
    'a9fb39','acfb38','affa37','b1f936','b4f836','b7f735','b9f635','bcf534','bef434','c1f334',
    'c3f134','c6f034','c8ef34','cbed34','cdec34','d0ea34','d2e935','d4e735','d7e535','d9e436',
    'dbe236','dde037','dfdf37','e1dd37','e3db38','e5d938','e7d739','e9d539','ebd339','ecd13a',
    'eecf3a','efcd3a','f1cb3a','f2c93a','f4c73a','f5c53a','f6c33a','f7c13a','f8be39',
)


def q(name):
    prefix, local = name.split(":")
    return f"{{{NS[prefix]}}}{local}"


def add(parent, tag, **attrs):
    return ET.SubElement(parent, q(tag), {k: str(v) for k, v in attrs.items()})


def color(parent, value, opacity=1):
    fill = add(parent, "a:solidFill")
    rgb = add(fill, "a:srgbClr", val=value.upper())
    if opacity != 1:
        add(rgb, "a:alpha", val=round(opacity * 100000))


def name(shape):
    return shape.find(".//p:cNvPr", NS).get("name")


def xy(shape):
    transform = shape.find("./p:spPr/a:xfrm", NS)
    offset, extent = transform.find("a:off", NS), transform.find("a:ext", NS)
    return np.array([int(offset.get("x")), int(offset.get("y"))]), np.array([int(extent.get("cx")), int(extent.get("cy"))])


class Drawing:
    def __init__(self, tree):
        self.next_id = max(int(n.get("id")) for n in tree.findall(".//p:cNvPr", NS)) + 1

    def shape(self, parent, label, low, size):
        shape = add(parent, "p:sp")
        nv = add(shape, "p:nvSpPr")
        add(nv, "p:cNvPr", id=self.next_id, name=label)
        self.next_id += 1
        add(nv, "p:cNvSpPr")
        add(nv, "p:nvPr")
        props = add(shape, "p:spPr")
        transform = add(props, "a:xfrm")
        add(transform, "a:off", x=round(low[0]), y=round(low[1]))
        add(transform, "a:ext", cx=max(1, round(size[0])), cy=max(1, round(size[1])))
        return shape, props

    def poly(self, parent, label, points, fill=None, stroke=None, width=0, opacity=1):
        points = np.round(points).astype(int)
        low = points.min(axis=0)
        size = np.maximum(points.max(axis=0) - low, 1)
        shape, props = self.shape(parent, label, low, size)
        geometry = add(props, "a:custGeom")
        for tag in ("avLst", "gdLst", "ahLst", "cxnLst"):
            add(geometry, "a:" + tag)
        add(geometry, "a:rect", l="l", t="t", r="r", b="b")
        path = add(add(geometry, "a:pathLst"), "a:path", w=size[0], h=size[1],
                   fill="norm" if fill else "none", stroke=int(bool(stroke)))
        for i, point in enumerate(points - low):
            add(add(path, "a:moveTo" if i == 0 else "a:lnTo"), "a:pt", x=point[0], y=point[1])
        if fill:
            add(path, "a:close")
            color(props, fill, opacity)
        else:
            add(props, "a:noFill")
        line = add(props, "a:ln", w=round(width), cap="rnd")
        color(line, stroke, opacity) if stroke else add(line, "a:noFill")
        add(line, "a:round")
        return shape

    def dot(self, parent, label, point, radius, stroke, width):
        shape, props = self.shape(parent, label, np.asarray(point) - radius, [2 * radius] * 2)
        add(add(props, "a:prstGeom", prst="ellipse"), "a:avLst")
        color(props, "FFFFFF")
        color(add(props, "a:ln", w=round(width)), stroke)
        return shape

    def text(self, parent, label, value, x, y, w, h, size):
        shape, props = self.shape(parent, label, [x, y], [w, h])
        add(add(props, "a:prstGeom", prst="rect"), "a:avLst")
        add(props, "a:noFill")
        add(add(props, "a:ln"), "a:noFill")
        body = add(shape, "p:txBody")
        add(body, "a:bodyPr", wrap="none", lIns=0, tIns=0, rIns=0, bIns=0, anchor="ctr")
        add(body, "a:lstStyle")
        paragraph = add(body, "a:p")
        add(paragraph, "a:pPr", algn="ctr")
        run = add(paragraph, "a:r")
        props = add(run, "a:rPr", lang="en-US", sz=round(size * EMU_PER_PAPER_PT / 127))
        color(props, "31455C")
        add(props, "a:latin", typeface="Arial")
        add(run, "a:t").text = value

    def arrow(self, parent, label, points, unit, times):
        lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
        if lengths[-1] < 1e-6:
            return
        head = min(1.9 * unit, 0.5 * sum(lengths))
        direction = (points[-1] - points[-2]) / lengths[-1]
        neck = points[-1] - head * direction
        normal = np.array([-direction[1], direction[0]]) * head * .46
        triangle = [points[-1], neck + normal, neck - normal]
        stop = sum(lengths) - .85 * head
        shaft, stamps, distance = [points[0]], [times[0]], 0
        for k, length in enumerate(lengths):
            if distance + length >= stop:
                t = (stop - distance) / max(length, 1e-9)
                shaft.append(points[k] + t * (points[k + 1] - points[k]))
                stamps.append(times[k] + t * (times[k + 1] - times[k]))
                break
            distance += length
            shaft.append(points[k + 1])
            stamps.append(times[k + 1])
        # PowerPoint scales group geometry, but not DrawingML line widths.
        stroke_unit = EMU_PER_PAPER_PT
        # Match every scene-flow illustration: coloured shafts and heads, no outline.
        for a, b, ta, tb in zip(shaft[:-1], shaft[1:], stamps[:-1], stamps[1:]):
            for k in range(3):
                t = ta + (tb - ta) * (k + .5) / 3
                self.poly(parent, label + " gradient", [a + (b - a) * k / 3, a + (b - a) * (k + 1) / 3],
                          stroke=TURBO[int((.12 + .54 * t) * 256) - 30], width=.62 * stroke_unit)
        self.poly(parent, label + " head", triangle, fill=TURBO[int((.12 + .54 * times[-1]) * 256) - 30])


def update_flow(group, drawing, labels, context, horizon):
    picture = group.find("p:pic", NS)
    for child in list(group)[2:]:
        if child is not picture:
            group.remove(child)
    origin, size = xy(picture)
    transform = group.find("p:grpSpPr/a:xfrm", NS)
    unit = EMU_PER_PAPER_PT * int(transform.find("a:chExt", NS).get("cx")) / int(transform.find("a:ext", NS).get("cx"))
    right, up = np.array(context["right"]), np.array(context["up"])
    center, scale = np.array(context["projection_center"]), context["paper_scale"]

    def project(points):
        uv = np.stack([points @ right, -points @ up], axis=-1)
        return ((uv - center) * scale + [82.5, 44]) / [165, 88] * size + origin

    patch, flow = labels["patch_xyz_world"], labels["flow_xyz_world"]
    starts = project(patch)
    tracks = np.stack([project(patch + 3 * flow[:, k]) for k in range(8)], axis=1)
    valid = labels["patch_keep"] & np.all(labels["flow_valid"][:, :horizon + 1], axis=1)
    moving = np.max(np.linalg.norm(flow[:, :horizon + 1], axis=-1), axis=1) > .002
    for k in np.flatnonzero(valid & ~moving):
        drawing.dot(group, f"Static patch {k}", starts[k], .25 * unit, STATIC, .12 * EMU_PER_PAPER_PT)
    for k in np.flatnonzero(valid & moving):
        points = np.vstack([starts[k], tracks[k, :horizon + 1]])
        drawing.arrow(group, f"Recorded flow patch {k}", points, unit, np.arange(horizon + 2) / 8)
        drawing.dot(group, f"Moving patch {k} origin", starts[k], .32 * unit, TURBO[0], .15 * EMU_PER_PAPER_PT)
    return {"horizon_ms": 50 * (horizon + 1), "moving": int(np.sum(valid & moving)),
            "static": int(np.sum(valid & ~moving)), "tracks": tracks.tolist(), "starts": starts.tolist()}


def update_target(group, drawing):
    # Preserve the original orange mesh colors, face shading and temporal fading.
    for shape in list(group)[2:]:
        label = name(shape)
        if label.startswith("Asset update "):
            group.remove(shape)
    trajectory = next(s for s in list(group)[2:] if name(s) == "Recorded target origin trajectory")
    origin, _ = xy(trajectory)
    path = trajectory.find(".//a:path", NS)
    points = np.array([[int(p.get("x")), int(p.get("y"))] for p in path.findall(".//a:pt", NS)]) + origin
    forecast = "future" in name(group)
    if forecast:
        # Keep the approved dashed line and 50-ms ticks, without a white casing.
        for k, point in enumerate(points):
            dot = drawing.dot(group, f"Asset update +{k * 50} ms tick", point,
                              .5 * EMU_PER_PAPER_PT, TARGET, .22 * EMU_PER_PAPER_PT)
            # Keep intermediate ticks beneath the target bodies and pose axes.
            group.remove(dot); group.insert(list(group).index(trajectory) + 1, dot)
    for shape in list(group)[2:]:
        if name(shape).endswith(" ms X"):
            offset, _ = xy(shape)
            first = shape.find(".//a:path/a:moveTo/a:pt", NS)
            point = offset + [int(first.get("x")), int(first.get("y"))]
            drawing.dot(group, "Asset update " + name(shape)[:-2] + " origin", point,
                        .7 * EMU_PER_PAPER_PT, TARGET, .28 * EMU_PER_PAPER_PT)


ICON_POSES = {"robot-state": "p2", "action-chunk-1": "p1",
              "action-chunk-2": "p2", "action-chunk-3": "p3",
              "inference-action-chunk": "p2"}
NOISE_PATCHES = {22622: "noisy_actions_A", 13097: "inference_noise"}


def update_icons_v28():
    """Replace only the five icon groups and the two 32x32 noise grids.

    SVG primitives become native DrawingML shapes, with the SVG aspect ratio,
    the old group's height and center, and a common base line for all poses.
    Re-running is safe: existing v28 groups/images are replaced in place.
    """
    source = ROOT / "fig2_se3wam.pptx"
    assets = ROOT / "assets/icons_v28"
    with ZipFile(source) as deck:
        entries = [(info, deck.read(info.filename)) for info in deck.infolist()]
    parts = {info.filename: data for info, data in entries}
    slide = ET.fromstring(parts["ppt/slides/slide1.xml"])
    tree = slide.find("p:cSld/p:spTree", NS)
    drawing = Drawing(tree)
    groups = {name(group): group for group in tree.findall("p:grpSp", NS)}
    # The adopted v27 source uses zero-based action-chunk names.
    if "action-chunk-0" in groups:
        for i in reversed(range(3)):
            groups[f"action-chunk-{i}"].find("p:nvGrpSpPr/p:cNvPr", NS).set(
                "name", f"action-chunk-{i + 1}")
        groups = {name(group): group for group in tree.findall("p:grpSp", NS)}
    svg_ns = "{http://www.w3.org/2000/svg}"
    for label, pose in ICON_POSES.items():
        group = groups[label]
        transform = group.find("p:grpSpPr/a:xfrm", NS)
        off, ext = transform.find("a:off", NS), transform.find("a:ext", NS)
        old_x, y = int(off.get("x")), int(off.get("y"))
        old_w, height = int(ext.get("cx")), int(ext.get("cy"))
        svg = ET.parse(assets / f"robot_arm_{pose}.svg").getroot()
        vx, vy, vw, vh = map(float, svg.get("viewBox").split())
        scale = height / vh
        width = round(vw * scale)
        x = round(old_x + (old_w - width) / 2)
        for tag, attrs in (("a:off", {"x": x, "y": y}),
                           ("a:ext", {"cx": width, "cy": height}),
                           ("a:chOff", {"x": x, "y": y}),
                           ("a:chExt", {"cx": width, "cy": height})):
            transform.find(tag, NS).attrib.update({k: str(v) for k, v in attrs.items()})
        group.find("p:nvGrpSpPr/p:cNvPr", NS).set(
            "descr", f"icons_v28/robot_arm_{pose}.svg; native vector shapes")
        for child in list(group)[2:]:
            group.remove(child)

        def point(px, py):
            return np.array([x + (px - vx) * scale, y + (py - vy) * scale])

        for i, element in enumerate(svg):
            kind = element.tag.removeprefix(svg_ns)
            if kind in ("title", "metadata"):
                continue
            attrs = element.attrib
            fill = attrs.get("fill", "none").removeprefix("#")
            stroke = attrs.get("stroke", "none").removeprefix("#")
            fill, stroke = (None if v == "none" else v for v in (fill, stroke))
            pen = float(attrs.get("stroke-width", 0)) * scale
            child_name = f"{label} v28 {pose} {kind} {i}"
            if kind == "polygon":
                points = [point(*map(float, pair.split(","))) for pair in attrs["points"].split()]
                drawing.poly(group, child_name, points, fill=fill, stroke=stroke, width=pen)
            elif kind == "line":
                points = [point(float(attrs[f"x{k}"]), float(attrs[f"y{k}"])) for k in (1, 2)]
                drawing.poly(group, child_name, points, stroke=stroke, width=pen)
            elif kind in ("circle", "rect"):
                if kind == "circle":
                    radius = float(attrs["r"])
                    low = point(float(attrs["cx"]) - radius, float(attrs["cy"]) - radius)
                    size = np.array([2 * radius, 2 * radius]) * scale
                    preset = "ellipse"
                else:
                    low = point(float(attrs["x"]), float(attrs["y"]))
                    size = np.array([float(attrs["width"]), float(attrs["height"])]) * scale
                    preset = "roundRect" if float(attrs.get("rx", 0)) else "rect"
                _, props = drawing.shape(group, child_name, low, size)
                adjustments = add(add(props, "a:prstGeom", prst=preset), "a:avLst")
                if preset == "roundRect":
                    adjustment = round(float(attrs["rx"]) * scale / min(size) * 100000)
                    add(adjustments, "a:gd", name="adj", fmla=f"val {adjustment}")
                color(props, fill) if fill else add(props, "a:noFill")
                line = add(props, "a:ln", w=round(pen), cap="rnd")
                color(line, stroke) if stroke else add(line, "a:noFill")
                add(line, "a:round")
            else:
                raise ValueError(f"Unsupported SVG element: {kind}")

    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    relationships = ET.fromstring(parts["ppt/slides/_rels/slide1.xml.rels"])
    media = {}
    removed = 0
    for cell_size, label in NOISE_PATCHES.items():
        container = groups["action-noise" if label == "noisy_actions_A" else "inference-noise"]
        cells = []
        for shape in container.findall("p:sp", NS):
            if name(shape).startswith("Noise "):
                low, size = xy(shape)
                if tuple(size) == (cell_size, cell_size):
                    cells.append(shape)
        existing = next((pic for pic in container.findall("p:pic", NS) if name(pic) == label), None)
        if cells:
            assert len(cells) == 1024, (label, len(cells))
            bounds = [xy(shape) for shape in cells]
            low = np.min([pos for pos, _ in bounds], axis=0)
            size = np.max([pos + extent for pos, extent in bounds], axis=0) - low
            index = list(container).index(cells[0])
            for shape in cells:
                container.remove(shape)
            removed += len(cells)
        else:
            assert existing is not None, f"Missing noise grid: {label}"
            low, size = xy(existing)
            index = list(container).index(existing)
            container.remove(existing)
        # Keep the existing native border and the unrelated dashed group frames.
        borders = [shape for shape in container.findall("p:sp", NS)
                   if name(shape).startswith("Noise ") and
                   all(np.array_equal(a, b) for a, b in zip(xy(shape), (low, size)))]
        assert len(borders) == 1, f"Expected original border for {label}"
        target = f"../media/{label}_v28.png"
        relationship = next((rel for rel in relationships if rel.get("Target") == target), None)
        if relationship is None:
            next_rid = 1 + max(int(rel.get("Id")[3:]) for rel in relationships)
            relationship = ET.SubElement(relationships, f"{{{rel_ns}}}Relationship", {
                "Id": f"rId{next_rid}", "Type": NS["r"] + "/image", "Target": target})
        pic = ET.Element(q("p:pic"))
        nv = add(pic, "p:nvPicPr")
        add(nv, "p:cNvPr", id=drawing.next_id, name=label,
            descr="icons_v28; 32x32 Gaussian noise, nearest-neighbor 640px PNG")
        drawing.next_id += 1
        add(add(nv, "p:cNvPicPr"), "a:picLocks", noChangeAspect=1)
        add(nv, "p:nvPr")
        blip_fill = add(pic, "p:blipFill")
        blip = add(blip_fill, "a:blip", cstate="none")
        blip.set(q("r:embed"), relationship.get("Id"))
        add(add(blip_fill, "a:stretch"), "a:fillRect")
        props = add(pic, "p:spPr")
        transform = add(props, "a:xfrm")
        add(transform, "a:off", x=low[0], y=low[1])
        add(transform, "a:ext", cx=size[0], cy=size[1])
        add(add(props, "a:prstGeom", prst="rect"), "a:avLst")
        container.insert(index, pic)
        media[f"ppt/media/{label}_v28.png"] = (assets / f"{label}.png").read_bytes()
    assert removed in (0, 2048), removed
    presentation = ET.fromstring(parts["ppt/presentation.xml"])
    presentation.set("autoCompressPictures", "0")
    changed = {
        "ppt/slides/slide1.xml": ET.tostring(slide, encoding="utf-8", xml_declaration=True),
        "ppt/slides/_rels/slide1.xml.rels": ET.tostring(relationships, encoding="utf-8", xml_declaration=True),
        "ppt/presentation.xml": ET.tostring(presentation, encoding="utf-8", xml_declaration=True),
        **media,
    }
    temporary = source.with_suffix(".updated.pptx")
    with ZipFile(temporary, "w") as deck:
        for info, data in entries:
            deck.writestr(info, changed.pop(info.filename, data))
        for filename, data in changed.items():
            deck.writestr(filename, data)
    temporary.replace(source)
    print(json.dumps({"robot_groups": ICON_POSES, "noise_cells_removed": removed,
                      "noise_images": list(NOISE_PATCHES.values())}))


def update_illustrations():
    source = ROOT / "fig2_se3wam.pptx"
    with ZipFile(source) as deck:
        entries = [(info, deck.read(info.filename)) for info in deck.infolist()]
    parts = {i.filename: b for i, b in entries}
    slide_size = ET.fromstring(parts["ppt/presentation.xml"]).find("p:sldSz", NS)
    assert (int(slide_size.get("cx")), int(slide_size.get("cy"))) == (15240000, 9048750)
    slide = ET.fromstring(parts["ppt/slides/slide1.xml"])
    tree = slide.find("p:cSld/p:spTree", NS)
    drawing = Drawing(tree)
    labels = np.load(ROOT / "assets/geometry_labels.npz")
    original = np.load(ROOT.parent / "Fig1/data/labels.npz")
    camera = np.linalg.inv(original["world_from_camera_cv"])
    intrinsics = original["camera_intrinsics"]
    world_tracks = labels["patch_xyz_world"][:, None] + labels["flow_xyz_world"]
    camera_tracks = world_tracks @ camera[:3, :3].T + camera[:3, 3]
    image_tracks = camera_tracks[..., :2] / camera_tracks[..., 2:]
    image_tracks = image_tracks * [intrinsics[0, 0], intrinsics[1, 1]] + intrinsics[:2, 2]
    label_error_px = float(np.max(abs(image_tracks - original["flow_end_px"])) * 640 / 224)
    assert label_error_px < 1e-6, label_error_px
    context = json.loads((ROOT / "assets/blender/source.json").read_text(encoding="utf-8"))
    records = []
    for group in tree.findall("p:grpSp", NS):
        label = name(group)
        if label.startswith("S-supervision-example-"):
            horizon = HORIZONS[int(label.rsplit("-", 1)[1])]
            records.append(update_flow(group, drawing, labels, context, horizon))
        elif label in ("Target history trajectory", "Target SE(3) future trajectory"):
            update_target(group, drawing)
    assert len(records) == 3
    for shape in list(tree):
        text = ''.join(t.text or '' for t in shape.findall(".//a:t", NS))
        if shape.tag == q("p:sp") and name(shape).startswith("Asset update flow legend"):
            tree.remove(shape)
        elif shape.tag == q("p:sp") and text in ("Sparse 3D flow", "Target SE(3) forecast"):
            for rgb in shape.findall(".//a:srgbClr", NS):
                rgb.set("val", "263E74" if text == "Sparse 3D flow" else TARGET)
    unit = EMU_PER_PAPER_PT
    # Fits in the existing white margin below the three context thumbnails.
    drawing.text(tree, "Asset update flow legend zero", "0", 391 * unit, 69.4 * unit, 5 * unit, 6.2 * unit, 5.8)
    legend = np.stack([np.linspace(398, 420, 9), np.full(9, 72.5)], axis=-1) * unit
    drawing.arrow(tree, "Asset update flow legend", legend, unit, np.linspace(0, 1, 9))
    drawing.text(tree, "Asset update flow legend time", "+400 ms", 422 * unit, 69.4 * unit, 27 * unit, 6.2 * unit, 5.8)
    updated = ET.tostring(slide, encoding="utf-8", xml_declaration=True)
    media = {"ppt/media/image1.png": (ROOT / "assets/rgb.png").read_bytes(),
             "ppt/media/image3.png": (ROOT / "assets/blender/flow_context.png").read_bytes()}
    temporary = source.with_suffix(".updated.pptx")
    with ZipFile(temporary, "w") as deck:
        for info, data in entries:
            deck.writestr(info, updated if info.filename == "ppt/slides/slide1.xml" else media.get(info.filename, data))
    temporary.replace(source)
    report = ROOT.parents[1] / "build/fig3-assets-20261116/flow_validation.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"display_scale": 3.0, "turbo": [.12, .66],
                                 "max_label_error_px_at_640": label_error_px,
                                 "panels": records}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"panels": [{k: v for k, v in r.items() if k not in ("tracks", "starts")} for r in records]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--icons-v28", action="store_true",
                        help="replace only the five robot icons and two noise patches")
    args = parser.parse_args()
    update_icons_v28() if args.icons_v28 else update_illustrations()
