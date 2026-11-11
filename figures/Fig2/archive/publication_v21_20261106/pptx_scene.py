"""Translate this figure's SVG into native slide geometry; no raster fallback.

Used by build_fig2_pptx.mjs. Only the two existing modality images stay images.
The DrawingML pass preserves SVG groups, exact dash lengths and rounded joins.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def tag(element):
    return element.tag.rsplit("}", 1)[-1]


def matmul(first, second):
    a, b, c, d, e, f = first
    g, h, i, j, k, l = second
    return (a*g+c*h, b*g+d*h, a*i+c*j, b*i+d*j,
            a*k+c*l+e, b*k+d*l+f)


def transform(value):
    result = (1, 0, 0, 1, 0, 0)
    for kind, arguments in re.findall(r"(\w+)\(([^)]+)\)", value or ""):
        args = [float(v) for v in re.split(r"[,\s]+", arguments.strip())]
        if kind == "matrix":
            current = tuple(args)
        elif kind == "rotate":
            angle = math.radians(args[0])
            current = (math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), 0, 0)
            if len(args) == 3:
                x, y = args[1:]
                current = matmul(matmul((1, 0, 0, 1, x, y), current), (1, 0, 0, 1, -x, -y))
        else:
            raise ValueError(f"Unsupported SVG transform: {kind}")
        result = matmul(result, current)
    return result


def point(matrix, x, y):
    a, b, c, d, e, f = matrix
    return [a*x+c*y+e, b*x+d*y+f]


def bounds(points):
    xs, ys = zip(*points)
    return [min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)]


def segment_clip(p, q, clip):
    x, y, w, h = clip
    dx, dy = q[0]-p[0], q[1]-p[1]
    lo, hi = 0.0, 1.0
    for coefficient, distance in [(-dx, p[0]-x), (dx, x+w-p[0]),
                                   (-dy, p[1]-y), (dy, y+h-p[1])]:
        if abs(coefficient) < 1e-12:
            if distance < 0:
                return None
        else:
            ratio = distance/coefficient
            if coefficient < 0:
                lo = max(lo, ratio)
            else:
                hi = min(hi, ratio)
            if lo > hi:
                return None
    return [[p[0]+lo*dx, p[1]+lo*dy], [p[0]+hi*dx, p[1]+hi*dy]]


def polygon_clip(points, clip):
    x, y, w, h = clip
    for axis, boundary, sign in [(0, x, 1), (0, x+w, -1), (1, y, 1), (1, y+h, -1)]:
        output = []
        if not points:
            return []
        previous = points[-1]
        previous_in = sign*(previous[axis]-boundary) >= -1e-8
        for current in points:
            current_in = sign*(current[axis]-boundary) >= -1e-8
            if current_in != previous_in:
                ratio = (boundary-previous[axis])/(current[axis]-previous[axis])
                output.append([previous[j]+ratio*(current[j]-previous[j]) for j in [0, 1]])
            if current_in:
                output.append(current)
            previous, previous_in = current, current_in
        points = output
    return points


def font_metrics(filename):
    data = Path(filename).read_bytes()
    count = struct.unpack_from(">H", data, 4)[0]
    tables = {}
    for index in range(count):
        name, _, offset, size = struct.unpack_from(">4sIII", data, 12+16*index)
        tables[name] = (offset, size)
    units = struct.unpack_from(">H", data, tables[b"head"][0]+18)[0]
    asc, desc, gap = struct.unpack_from(">hhh", data, tables[b"hhea"][0]+4)
    return asc/units, -desc/units, gap/units


def prepare(svg_path, scene_path):
    fonts = {}
    font_dir = Path("C:/Windows/Fonts")
    for name, filename in [("Arial", "arial.ttf"), ("Arial-Bold", "arialbd.ttf"),
                           ("Arial-Italic", "ariali.ttf")]:
        pdfmetrics.registerFont(TTFont(name, str(font_dir/filename)))
        fonts[name] = font_metrics(font_dir/filename)
    root = ET.parse(svg_path).getroot()
    viewbox = list(map(float, root.get("viewBox").split()))
    assert viewbox == [0, 0, 1600, 950], viewbox
    objects, clips = [], {}
    for element in root.iter():
        if tag(element) == "clipPath":
            rectangle = next(iter(element))
            assert tag(rectangle) == "rect"
            clips[element.get("id")] = [float(rectangle.get(k, 0)) for k in ("x", "y", "width", "height")]
    tree = {"group": "figure", "children": []}
    skipped = []

    def walk(element, matrix, style, clip, node, path):
        kind = tag(element)
        if kind in ("defs", "title", "desc"):
            return
        matrix = matmul(matrix, transform(element.get("transform")))
        current = style | dict(element.attrib)
        if element.get("clip-path"):
            local = clips[re.fullmatch(r"url\(#(.*)\)", element.get("clip-path"))[1]]
            x, y, w, h = local
            clip = bounds([point(matrix, px, py) for px, py in [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]])
        if kind in ("svg", "g"):
            if kind == "g" and element.get("id"):
                group = {"group": element.get("id"), "children": []}
                node["children"].append(group)
                node, path = group, path+[element.get("id")]
            for child in element:
                walk(child, matrix, current, clip, node, path)
            return
        scale = math.hypot(matrix[0], matrix[1])
        assert abs(scale-math.hypot(matrix[2], matrix[3])) < 1e-6
        obj = dict(kind=kind, group="/".join(path), fill=current.get("fill", "#000000"),
                   stroke=current.get("stroke", "none"), sw=float(current.get("stroke-width", 1))*scale,
                   dash=[float(v)*scale for v in current.get("stroke-dasharray", "").split()])
        number = lambda key, default=0: float(element.get(key, default))
        if kind == "rect":
            x, y, w, h = [number(k) for k in ("x", "y", "width", "height")]
            obj["box"] = bounds([point(matrix, px, py) for px, py in [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]])
            obj["radius"] = number("rx")*scale
            if not path and obj["box"] == viewbox and obj["fill"] == "#FFFFFF":
                return
        elif kind == "circle":
            cx, cy = point(matrix, number("cx"), number("cy"))
            r = number("r")*scale
            obj["box"] = [cx-r, cy-r, 2*r, 2*r]
        elif kind in ("polyline", "polygon"):
            points = [point(matrix, *map(float, item.split(","))) for item in element.get("points").split()]
            if clip:
                if kind == "polygon":
                    points = polygon_clip(points, clip)
                else:
                    pieces = [segment_clip(a, b, clip) for a, b in zip(points, points[1:])]
                    points = []
                    for piece in pieces:
                        if piece:
                            if not points or math.dist(points[-1], piece[0]) > 1e-6:
                                points.append(piece[0])
                            points.append(piece[1])
            if len(points) < 2 or (kind == "polygon" and len(points) < 3):
                skipped.append(kind)
                return
            obj["points"] = points
            obj["box"] = bounds(points)
        elif kind == "text":
            value = "".join(element.itertext())
            bold = current.get("font-weight") == "700"
            italic = current.get("font-style") == "italic"
            font = "Arial-Bold" if bold else "Arial-Italic" if italic else "Arial"
            size = float(current["font-size"])*scale
            advance = pdfmetrics.stringWidth(value, font, size)
            anchor = current.get("text-anchor", "start")
            dx = {"start": 0, "middle": -advance/2, "end": -advance}[anchor]
            ascent, descent, _ = fonts[font]
            # Native text boxes rotate about their centers. Preserve the SVG baseline.
            width, height = advance+4, size*(ascent+descent)
            baseline = point(matrix, number("x"), number("y"))
            angle = math.degrees(math.atan2(matrix[1], matrix[0]))
            theta = math.radians(angle)
            # PowerPoint's Arial cell baseline sits 0.071289 em below hhea.
            # Calibrated against this slide's native PowerPoint PDF export.
            native_ascent = ascent+0.0712890625
            local_center = [dx+width/2, -native_ascent*size+height/2]
            center = [baseline[0]+math.cos(theta)*local_center[0]-math.sin(theta)*local_center[1],
                      baseline[1]+math.sin(theta)*local_center[0]+math.cos(theta)*local_center[1]]
            obj.update(text=value, size=size, bold=bold, italic=italic, rotation=angle,
                       box=[center[0]-width/2, center[1]-height/2, width, height],
                       baseline=baseline, advance=advance, anchor=anchor, font="Arial")
        elif kind == "image":
            x, y, w, h = [number(k) for k in ("x", "y", "width", "height")]
            obj["box"] = bounds([point(matrix, x, y), point(matrix, x+w, y+h)])
            obj["data"] = element.get("href")
            assert obj["data"].startswith("data:image/png;base64,")
        else:
            raise ValueError(f"Unsupported SVG primitive: {kind}")
        if clip and kind in ("rect", "circle"):
            x, y, w, h = obj["box"]
            cx, cy, cw, ch = clip
            assert x >= cx-1e-6 and y >= cy-1e-6 and x+w <= cx+cw+1e-6 and y+h <= cy+ch+1e-6, obj
        obj["id"] = f"fig2-{len(objects)+1:05d}"
        objects.append(obj)
        node["children"].append({"object": obj["id"]})

    walk(root, (1, 0, 0, 1, 0, 0), {}, None, tree, [])
    scene = dict(width=1600, height=950, objects=objects, tree=tree,
                 source=str(svg_path), clipped_primitives=len(skipped))
    scene_path.write_text(json.dumps(scene, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    from collections import Counter
    print(json.dumps(dict(objects=len(objects), kinds=dict(Counter(o["kind"] for o in objects)), clipped=len(skipped))))


def q(prefix, name):
    return f"{{{NS[prefix]}}}{name}"


def arrow_pair(first, second):
    return (first["kind"] == "polyline" and second["kind"] == "polygon" and
            len(second["points"]) == 3 and
            math.dist(first["points"][-1], second["points"][0]) < .01 and
            first["stroke"] == second["fill"] and second["stroke"] == "none")


def arrow_pairs(node, objects):
    pairs = []
    children = node["children"]
    for child in children:
        if "children" in child:
            pairs.extend(arrow_pairs(child, objects))
    for first, second in zip(children, children[1:]):
        if "object" in first and "object" in second and arrow_pair(objects[first["object"]], objects[second["object"]]):
            pairs.append((first["object"], second["object"]))
    return pairs


def refine(scene_path, candidate, output):
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    objects = {obj["id"]: obj for obj in scene["objects"]}
    with ZipFile(candidate) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    root = ET.fromstring(entries["ppt/slides/slide1.xml"])
    tree = root.find("p:cSld/p:spTree", NS)
    elements = {}
    for child in list(tree):
        identifier = child.find(".//p:cNvPr", NS)
        if tag(child) == "pic":
            # The image facade does not export its `name` option. Match the
            # original image by its exact placement, then assign its SVG id.
            offset = child.find("p:spPr/a:xfrm/a:off", NS)
            matches = [obj for obj in objects.values() if obj["kind"] == "image" and
                       abs(int(offset.get("x"))-round(obj["box"][0]*9525)) <= 1 and
                       abs(int(offset.get("y"))-round(obj["box"][1]*9525)) <= 1]
            assert len(matches) == 1
            identifier.set("name", matches[0]["id"])
        if identifier is not None and identifier.get("name") in objects:
            name = identifier.get("name")
            elements[name] = child
            tree.remove(child)
    assert set(elements) == set(objects), (len(elements), len(objects))
    for name, child in elements.items():
        obj = objects[name]
        properties = child.find("p:spPr", NS)
        if properties is not None:
            line = properties.find("a:ln", NS)
            if line is not None and obj["stroke"] != "none":
                line.set("cap", "rnd")
                for join in list(line):
                    if tag(join) in ("round", "miter", "bevel", "prstDash", "custDash"):
                        line.remove(join)
                if obj["dash"]:
                    custom = ET.SubElement(line, q("a", "custDash"))
                    pairs = obj["dash"] if len(obj["dash"]) % 2 == 0 else obj["dash"]*2
                    for dash, space in zip(pairs[::2], pairs[1::2]):
                        ET.SubElement(custom, q("a", "ds"), d=str(round(100000*dash/obj["sw"])), sp=str(round(100000*space/obj["sw"])))
                ET.SubElement(line, q("a", "round"))
        if obj["kind"] == "text":
            xfrm = properties.find("a:xfrm", NS)
            x, y, w, h = obj["box"]
            xfrm.find("a:off", NS).attrib.update(x=str(round(x*9525)), y=str(round(y*9525)))
            xfrm.find("a:ext", NS).attrib.update(cx=str(round(w*9525)), cy=str(round(h*9525)))
            body = child.find("p:txBody/a:bodyPr", NS)
            body.set("wrap", "none")
            body.set("anchor", "t")
            body.set("lIns", "0"); body.set("rIns", "0")
            body.set("tIns", "0"); body.set("bIns", "0")
            for autofit in list(body):
                if tag(autofit) in ("normAutofit", "spAutoFit", "noAutofit"):
                    body.remove(autofit)
            ET.SubElement(body, q("a", "noAutofit"))

    next_id = max(int(e.get("id")) for container in [root, *elements.values()]
                  for e in container.iter(q("p", "cNvPr")))+1
    merged_arrows = set()

    def merge_arrow(first_id, second_id):
        first, second = objects[first_id], objects[second_id]
        child = elements[first_id]
        properties = child.find("p:spPr", NS)
        x, y, w, h = bounds(first["points"]+second["points"])
        width, height = max(1, round(w*9525)), max(1, round(h*9525))
        xfrm = properties.find("a:xfrm", NS)
        xfrm.find("a:off", NS).attrib.update(x=str(round(x*9525)), y=str(round(y*9525)))
        xfrm.find("a:ext", NS).attrib.update(cx=str(width), cy=str(height))
        for old in list(properties):
            if tag(old) in ("custGeom", "prstGeom", "noFill", "solidFill", "gradFill", "pattFill"):
                properties.remove(old)
        geometry = ET.Element(q("a", "custGeom"))
        for kind in ("avLst", "gdLst", "ahLst", "cxnLst"):
            ET.SubElement(geometry, q("a", kind))
        ET.SubElement(geometry, q("a", "rect"), l="0", t="0", r="w", b="h")
        paths = ET.SubElement(geometry, q("a", "pathLst"))
        for points, fill, stroke, closed in [(first["points"], "none", "1", False),
                                             (second["points"], "norm", "0", True)]:
            drawing = ET.SubElement(paths, q("a", "path"), w=str(width), h=str(height), fill=fill, stroke=stroke)
            for index, (px, py) in enumerate(points):
                command = ET.SubElement(drawing, q("a", "moveTo" if index == 0 else "lnTo"))
                ET.SubElement(command, q("a", "pt"), x=str(round((px-x)*9525)), y=str(round((py-y)*9525)))
            if closed:
                ET.SubElement(drawing, q("a", "close"))
        properties.insert(1, geometry)
        fill = ET.Element(q("a", "solidFill"))
        ET.SubElement(fill, q("a", "srgbClr"), val=second["fill"].lstrip("#"))
        properties.insert(2, fill)
        first["box"] = [x, y, w, h]
        merged_arrows.add(first_id)

    def node_bounds(node):
        if "object" in node:
            obj = objects[node["object"]]
            x, y, w, h = obj["box"]
            angle = math.radians(obj.get("rotation", 0))
            cx, cy = x+w/2, y+h/2
            points = [[cx+math.cos(angle)*dx-math.sin(angle)*dy,
                       cy+math.sin(angle)*dx+math.cos(angle)*dy]
                      for dx, dy in [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]]
            return bounds(points)
        rectangles = [node_bounds(child) for child in node["children"]]
        return bounds([[x, y] for x, y, w, h in rectangles]+
                      [[x+w, y+h] for x, y, w, h in rectangles]) if rectangles else [0, 0, 1, 1]

    def organize_arrows(node):
        children, organized, index = node["children"], [], 0
        while index < len(children):
            child = children[index]
            if "children" in child:
                organize_arrows(child)
            if index+1 < len(children) and "object" in child and "object" in children[index+1]:
                first, second = objects[child["object"]], objects[children[index+1]["object"]]
                if arrow_pair(first, second):
                    merge_arrow(child["object"], children[index+1]["object"])
                    organized.append(child)
                    index += 2
                    continue
            organized.append(child)
            index += 1
        node["children"] = organized

    organize_arrows(scene["tree"])

    def build_group(node):
        nonlocal next_id
        group = ET.Element(q("p", "grpSp"))
        nv = ET.SubElement(group, q("p", "nvGrpSpPr"))
        ET.SubElement(nv, q("p", "cNvPr"), id=str(next_id), name=node["group"])
        next_id += 1
        ET.SubElement(nv, q("p", "cNvGrpSpPr"))
        ET.SubElement(nv, q("p", "nvPr"))
        properties = ET.SubElement(group, q("p", "grpSpPr"))
        xfrm = ET.SubElement(properties, q("a", "xfrm"))
        x, y, w, h = node_bounds(node)
        offset = {"x": str(round(x*9525)), "y": str(round(y*9525))}
        extent = {"cx": str(max(1, round(w*9525))), "cy": str(max(1, round(h*9525)))}
        for kind in ["off", "ext", "chOff", "chExt"]:
            coords = offset if kind.endswith("Off") or kind == "off" else extent
            ET.SubElement(xfrm, q("a", kind), coords)
        for child in node["children"]:
            if "object" in child:
                group.append(elements[child["object"]])
            else:
                nested = build_group(child)
                if len(nested) > 2:
                    group.append(nested)
        return group

    # Preserve meaningful SVG subgroups while leaving top-level a/b/c independent.
    for node in scene["tree"]["children"]:
        tree.append(elements[node["object"]] if "object" in node else build_group(node))
    for name, child in elements.items():
        obj = objects[name]
        identifier = child.find(".//p:cNvPr", NS)
        identifier.set("name", obj["text"] if obj["kind"] == "text" else
                       "arrow | "+name if name in merged_arrows else
                       f'{obj["group"].rsplit("/", 1)[-1] or "figure"} | {obj["kind"]} | {name}')
    # Keep every native object; remove optional, redundant per-object metadata.
    # This also lets the user regroup the independently editable shapes.
    for element in root.iter(q("p", "cNvPr")):
        extension = element.find(q("a", "extLst"))
        if extension is not None:
            element.remove(extension)
        name = element.get("name", "")
        if " | circle | " in name:
            element.set("name", "Point " + element.get("id"))
        elif "noise" in name and " | rect | " in name:
            element.set("name", "Noise " + element.get("id"))
    for element in root.iter(q("p", "cNvSpPr")):
        locks = element.find(q("a", "spLocks"))
        if locks is not None and locks.attrib == {"noGrp": "1"}:
            element.remove(locks)
    for element in root.iter(q("a", "prstGeom")):
        adjustments = element.find(q("a", "avLst"))
        if adjustments is not None and not len(adjustments) and not adjustments.attrib:
            element.remove(adjustments)
    for element in root.iter(q("a", "ln")):
        dash = element.find(q("a", "prstDash"))
        if dash is not None and dash.get("val") == "solid":
            element.remove(dash)
    entries["ppt/slides/slide1.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    print(json.dumps(dict(source_objects=len(elements), single_object_arrows=len(merged_arrows), output=str(output))))


def verify(scene_path, presentation):
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    pairs = arrow_pairs(scene["tree"], {obj["id"]: obj for obj in scene["objects"]})
    with ZipFile(presentation) as archive:
        root = ET.fromstring(archive.read("ppt/slides/slide1.xml"))
        deck = ET.fromstring(archive.read("ppt/presentation.xml"))
        slide_count = len(deck.findall("p:sldIdLst/p:sldId", NS))
        pictures = root.findall(".//p:pic", NS)
        shapes = root.findall(".//p:sp", NS)
        text = ["".join(t.itertext()) for t in root.findall(".//a:t", NS)]
        expected = [o["text"] for o in scene["objects"] if o["kind"] == "text"]
        assert text == expected, (text, expected)
        assert slide_count == 1
        assert len(pictures) == 5
        assert len(shapes)+len(pictures) == len(scene["objects"])-len(pairs)
        identifiers = [element.get("id") for element in root.iter(q("p", "cNvPr"))]
        assert len(identifiers) == len(set(identifiers)), "Duplicate native shape ids"
        media = [n for n in archive.namelist() if n.startswith("ppt/media/")]
        assert 3 <= len(media) <= 5, media
        picture_sizes = []
        for picture in pictures:
            extent = picture.find("p:spPr/a:xfrm/a:ext", NS)
            picture_sizes.append([int(extent.get("cx")), int(extent.get("cy"))])
            assert picture_sizes[-1][0] <= 165*9525+1 and picture_sizes[-1][1] <= 88*9525+1, picture_sizes
        report = dict(slides=slide_count, native_shapes=len(shapes),
                      editable_text_boxes=len(expected), native_groups=len(root.findall(".//p:grpSp", NS)),
                      embedded_images=len(pictures), image_size_emu=picture_sizes,
                      single_object_arrows=len(pairs),
                      full_figure_image=False, all_svg_objects_accounted_for=True,
                      text_preserved_exactly=True)
        print(json.dumps(report))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "refine", "verify"])
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    {"prepare": prepare, "refine": refine, "verify": verify}[args.mode](*args.paths)
