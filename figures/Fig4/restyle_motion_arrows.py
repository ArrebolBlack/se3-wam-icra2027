"""Restyle the 21 blue and two striker arrows without reserializing the SVG.

All other bytes, including embedded scene images and text, are preserved.
Reruns rebuild marked groups from their print-point data-centerline attributes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from xml.parsers import expat

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import motion_arrow as motion

SVG = motion.SVG
NAMES = {
    "advancing": "(a) World advances / 18 cm",
    "grasp": "(c) Grasp / Harmonic",
    "t1_belt": "(c) Grasp / Conveyor", "t1_xyz": "(c) Grasp / Translating",
    "t1_so3": "(c) Grasp / Rotating", "t1_occ": "(c) Grasp / Occluded",
    "t2_trans": "(c) Place / Translating", "t2_se3": "(c) Place / Rotating",
    "t3_phase": "(c) Pass / Passage", "t3_full": "(c) Pass / Full passage",
    "t5_replan": "(c) Impact / Post-impact", "t4_sphere": "(c) Capture / Ball",
    "t4_sphere_tabletop": "(c) Capture / Tabletop ball", "t4_slider": "(c) Capture / Slider",
    "t4_can": "(c) Capture / Can",
}
# Figure-specific clearance adjustments are in print pt, never geometry defaults.
# Values are applied only to the original centerlines, then stored in the SVG.
TIP_RETREAT = {}
FORCE_MIN_HEAD = {"F4-22"}  # legend icon follows the surrounding text height


def path_points(d):
    assert set(re.findall("[A-Za-z]", d)) <= {"M", "L", "Z"}, d
    return np.array([float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]).reshape(-1, 2)


def unit(v):
    return v / np.linalg.norm(v)


def transform_matrix(value):
    matrix = np.eye(3)
    for name, args in re.findall(r"([a-zA-Z]+)\(([^)]+)\)", value or ""):
        values = [float(v) for v in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", args)]
        t = np.eye(3)
        if name == "translate":
            t[:2, 2] = values if len(values) == 2 else [values[0], 0]
        elif name == "scale":
            t[0, 0], t[1, 1] = values if len(values) == 2 else values * 2
        elif name == "matrix":
            a, b, c, d, e, f = values
            t = np.array([[a, c, e], [b, d, f], [0, 0, 1]])
        else:
            raise ValueError(f"Unsupported source transform: {name}")
        matrix = matrix @ t
    return matrix


def transformed(points, matrix):
    return (np.column_stack([points, np.ones(len(points))]) @ matrix.T)[:, :2]


def element_spans(data):
    """Map ET preorder indices to exact XML byte spans, including empty tags."""
    parser = expat.ParserCreate()
    spans, stack = [], []
    def start(name, attrs):
        begin = parser.CurrentByteIndex
        tag_end = data.index(b">", begin) + 1
        index = len(spans)
        spans.append([begin, None])
        stack.append((index, data[begin:tag_end].rstrip().endswith(b"/>")))
    def end(name):
        index, empty = stack.pop()
        position = parser.CurrentByteIndex
        spans[index][1] = position if empty else data.index(b">", position) + 1
    parser.StartElementHandler, parser.EndElementHandler = start, end
    parser.Parse(data, True)
    return spans


def erase_spans(data, spans):
    for begin, end in sorted(spans, reverse=True):
        data = data[:begin] + data[end:]
    return data


def verify_unchanged(source, result, removed_spans):
    """Stronger than the reference canonical comparison: literal byte equality."""
    root = ET.fromstring(result)
    result_spans = element_spans(result)
    inserted = [result_spans[i] for i, n in enumerate(root.iter())
                if n.get("data-motion-arrow") == motion.STYLE]
    assert len(inserted) == 23
    assert erase_spans(source, removed_spans) == erase_spans(result, inserted), "Non-arrow SVG bytes changed"


def identify(data):
    root = ET.fromstring(data)
    nodes = list(root.iter())
    spans = element_spans(data)
    assert len(nodes) == len(spans)
    span_of = dict(zip(nodes, spans))
    parents = {n: p for p in nodes for n in p}
    marked = [n for n in nodes if n.get("data-motion-arrow") == motion.STYLE]
    if marked:
        assert len(marked) == 23
        return [{"node": n, "old": [n], "record": json.loads(n.get("data-review")),
                 "points": np.array(json.loads(n.get("data-centerline"))),
                 "double": n.get("data-double") == "true", "color": n.get("data-color"),
                 "transform": n.get("transform"),
                 "head_len": motion.HEAD_MIN if n.get("id") in FORCE_MIN_HEAD else None}
                for n in marked], span_of
    records = []
    for parent in nodes:
        children = list(parent)
        for i, n in enumerate(children):
            color = n.get("stroke")
            if n.tag != SVG + "path" or color not in (motion.MOTION_COLOR, motion.STRIKER_COLOR) or n.get("fill") != "none":
                continue
            d = n.get("d")
            if d.endswith("Z"):
                continue  # closed entry-location circles are not motion arrows
            old, heads = [n], []
            if i and children[i - 1].get("d") == d and children[i - 1].get("stroke", "").upper() == "#FFFFFF":
                old.insert(0, children[i - 1])
            for candidate in children[i + 1:]:
                if candidate.tag == SVG + "path" and candidate.get("fill") == color and candidate.get("d", "").endswith("Z"):
                    heads.append(candidate)
                    old.append(candidate)
                else:
                    break
            chain, a = [], parent
            while a is not None:
                chain.insert(0, a)
                a = parents.get(a)
            parent_matrix = np.eye(3)
            for a in chain:
                parent_matrix = parent_matrix @ transform_matrix(a.get("transform"))
            matrix = parent_matrix @ transform_matrix(n.get("transform"))
            owner = next((a.get("id")[6:] for a in reversed(chain) if a.get("id", "").startswith("panel-")), "advancing")
            label = NAMES[owner]
            original_points = None
            if heads:
                points = path_points(d)
                hp = path_points(heads[0].get("d"))
                assert np.linalg.norm(hp[0] - points[-1]) < .002
                direction = unit(hp[0] - hp[2])
                if len(heads) == 2:
                    assert np.linalg.norm(path_points(heads[1].get("d"))[0] - points[0]) < .002
                label += " / " + ("striker" if color == motion.STRIKER_COLOR else
                                    "double" if len(heads) == 2 else
                                    "rotation" if "local-motion" in parent.get("id", "") else "translation")
            elif d.startswith("M 116.784"):
                points = path_points(d.split(" M ")[0])
                direction = unit(points[-1] - points[0])
            elif d.startswith("M 439.5"):
                y = 223.3 if color == motion.STRIKER_COLOR else 199.3
                points = np.array([[439.5, y], [446., y]])
                direction = np.array([1., 0.])
                label = "Legend / " + ("Striker" if color == motion.STRIKER_COLOR else "Translation")
            elif d.startswith("M 440 212."):
                control = np.array([[440., 212.6], [442.4, 207.3], [445.6, 212.]])
                original_points = np.array([(1-t)**2*control[0] + 2*(1-t)*t*control[1] + t*t*control[2]
                                            for t in np.linspace(0, 1, 65)])
                # 270-degree open circle, near the 7 pt legend text's cap height.
                angles = np.linspace(np.deg2rad(45), np.deg2rad(315), 97)
                points = np.column_stack([442.1 + 2.25 * np.cos(angles), 211.1 + 2.25 * np.sin(angles)])
                direction = unit(points[-1] - points[-2])
                label = "Legend / Rotation"
            else:
                raise ValueError(f"Unrecognized motion arrow: {d[:90]}")
            points = transformed(points, matrix)
            direction = unit(matrix[:2, :2] @ direction)
            original = transformed(original_points, matrix) if original_points is not None else points.copy()
            double = len(heads) == 2
            arrow_id = f"F4-{len(records) + 1:02d}"
            original_length = motion.path_length(original)
            retreat = TIP_RETREAT.get(arrow_id, 0.)
            if retreat:
                assert 0 < retreat <= 1.0
                points = motion.trim_path(points, end=original_length - retreat)
            # Extend only as far as necessary to respect BOTH the 3 pt minimum
            # and the 40% cap (7.5 pt single / 15 pt double). Review scene clearance.
            needed = motion.HEAD_MIN / motion.HEAD_FRACTION * (2 if double else 1)
            extension = max(0., needed - motion.path_length(points))
            end_extension, relocation = 0., [0., 0.]
            if arrow_id == "F4-03":
                # User approved extending the free lower-right end; the upper
                # end cannot be extended without crossing the opaque gripper.
                end_extension, extension = extension, 0.
                points = np.vstack([points, points[-1] + direction * end_extension])
            elif extension:
                points = np.vstack([points[0] - direction * extension, points])
            if arrow_id == "F4-07":
                # User-approved relocation below the ghost trail: the original
                # head intersects the current target even after 1 pt retreat.
                relocation = (np.array([397.2, 62.1]) - points[-1]).tolist()
                points += relocation
            elif arrow_id == "F4-16":
                # Move parallel to the striker direction, clear of its body.
                relocation = (np.array([direction[1], -direction[0]]) * 3.2).tolist()
                points += relocation
            head_len = motion.head_length(points, double_headed=double,
                                          head_len=motion.HEAD_MIN if arrow_id in FORCE_MIN_HEAD else None)
            inverse = np.linalg.inv(parent_matrix)
            transform = "matrix(" + " ".join(f"{v:.12g}" for v in
                        [inverse[0, 0], inverse[1, 0], inverse[0, 1], inverse[1, 1], inverse[0, 2], inverse[1, 2]]) + ")"
            record = {"id": arrow_id, "label": label, "original_centerline_pt": original.tolist(),
                      "original_path_length_pt": original_length, "tail_extension_pt": extension,
                      "tip_retreat_pt": retreat, "free_end_extension_pt": end_extension,
                      "relocation_pt": relocation, "head_only": False}
            records.append({"node": n, "old": old, "record": record, "points": points,
                            "double": double, "color": color, "transform": transform, "head_len": head_len})
    assert sum(a["color"] == motion.MOTION_COLOR for a in records) == 21
    assert len(records) == 23  # includes the two black striker arrows, per user correction
    return records, span_of


def restyle(source):
    arrows, spans = identify(source)
    edits, removed, report = [], [], []
    for arrow in arrows:
        points, double, record = arrow["points"], arrow["double"], arrow["record"]
        length = motion.head_length(points, double_headed=double, head_len=arrow["head_len"])
        record.update({"centerline_pt": points.tolist(), "path_length_pt": motion.path_length(points),
                       "head_length_pt": length, "head_width_pt": motion.head_width(length),
                       "scaled": length < motion.HEAD_LEN - 1e-8, "double_headed": double,
                       "color": arrow["color"], "head_fraction": length / (motion.path_length(points) / (2 if double else 1))})
        group = motion.svg_group(points, double_headed=double, head_len=length, color=arrow["color"], attributes={
            "id": record["id"], "transform": arrow["transform"], "data-head-length": repr(length),
            "data-review": json.dumps(record, separators=(",", ":")),
        })
        replacement = ET.tostring(group, encoding="utf-8")
        for i, node in enumerate(arrow["old"]):
            begin, end = spans[node]
            removed.append((begin, end))
            edits.append((begin, end, replacement if i == 0 else b""))
        report.append(record)
    result = source
    for begin, end, replacement in sorted(edits, reverse=True):
        result = result[:begin] + replacement + result[end:]
    verify_unchanged(source, result, removed)
    return result, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", type=Path, default=Path(__file__).with_name("ontimebench.svg"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result, records = restyle(args.svg.read_bytes())
    assert restyle(result)[0] == result, "Restyling is not byte-idempotent"
    args.svg.write_bytes(result)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Restyled {len(records)} arrows; non-arrow bytes unchanged; rerun is byte-identical.")
