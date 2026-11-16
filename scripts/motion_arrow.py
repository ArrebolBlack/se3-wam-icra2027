"""The ONLY source of motion-arrow geometry for Fig. 4 and Fig. 6.

All dimensions are absolute points at the final printed figure size. Callers
must transform source coordinates to print points before calling this module.
Bezier curves must be sampled at 64 or more intervals before use.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import numpy as np

SHAFT = 1.00
HEAD_LEN = 3.8
HEAD_W = 3.6
NECK = 0.65  # tip-to-neck / head length; rear indentation is 0.35 L
RIM = 0.17  # each side; stroke the silhouette at 2 * RIM, then fill it
HEAD_MIN = 3.0
HEAD_MIN_W = 2.85
HEAD_FRACTION = 0.40
MOTION_COLOR = "#2859A3"
STRIKER_COLOR = "#1A1A1A"
SVG = "{http://www.w3.org/2000/svg}"
STYLE = "unified-20261116"
ET.register_namespace("", SVG[1:-1])


def polyline(points):
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or not np.isfinite(points).all():
        raise ValueError("Expected finite N x 2 print-point coordinates")
    points = points[np.r_[True, np.linalg.norm(np.diff(points, axis=0), axis=1) > 1e-10]]
    if len(points) < 2:
        raise ValueError("An arrow needs a nonzero centerline")
    return points


def path_length(points):
    return float(np.linalg.norm(np.diff(polyline(points), axis=0), axis=1).sum())


def point_at(points, distance):
    points = polyline(points)
    lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
    cumulative = np.r_[0., np.cumsum(lengths)]
    distance = np.clip(distance, 0, cumulative[-1])
    index = min(len(lengths) - 1, np.searchsorted(cumulative, distance, side="right") - 1)
    return points[index] + (distance - cumulative[index]) / lengths[index] * (points[index + 1] - points[index])


def trim_path(points, start=0., end=None):
    points = polyline(points)
    cumulative = np.r_[0., np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    end = cumulative[-1] if end is None else end
    if not 0 <= start < end <= cumulative[-1] + 1e-9:
        raise ValueError("Invalid centerline trim")
    return polyline([point_at(points, start), *points[(cumulative > start) & (cumulative < end)], point_at(points, end)])


def head_length(points, *, double_headed=False, head_len=None):
    requested = HEAD_LEN if head_len is None else float(head_len)
    if not np.isfinite(requested) or requested < HEAD_MIN:
        raise ValueError("Head length must be at least HEAD_MIN")
    available = path_length(points) / (2 if double_headed else 1)
    # The minimum wins if the path is too short. The figure-specific caller
    # must extend it safely or explicitly report the exceptional head-only case.
    return max(HEAD_MIN, min(requested, HEAD_FRACTION * available))


def head_width(length):
    return max(HEAD_MIN_W, HEAD_W * length / HEAD_LEN)


def head_vertices(points, length, *, at_start=False):
    points = polyline(points)
    if at_start:
        points = points[::-1]
    tip = points[-1]
    # Chord of the LAST HEAD LENGTH, never the final segment's tangent.
    chord = tip - point_at(points, max(0, path_length(points) - length))
    direction = chord / np.linalg.norm(chord)
    normal = np.array([-direction[1], direction[0]])
    back = tip - length * direction
    return np.array([back + head_width(length) / 2 * normal, tip,
                     back - head_width(length) / 2 * normal]), direction


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _crosses(outline):
    for i, (a, b) in enumerate(zip(outline[:-1], outline[1:])):
        for j in range(i + 2, len(outline) - 1):
            if i == 0 and j == len(outline) - 2:
                continue
            c, d = outline[j:j + 2]
            if (_cross(b-a, c-a) * _cross(b-a, d-a) < -1e-12
                    and _cross(d-c, a-c) * _cross(d-c, b-c) < -1e-12):
                return True
    return False


def _silhouette_union(polygons):
    """Trace the outer boundary of overlapping shaft/head pieces.

    Tight arcs can place a rear wing inside the earlier curved shaft. Splitting
    the piece edges at their intersections and keeping only the union boundary
    avoids white seams, without moving the head, changing its chord, or adding
    a polygon library. Enclosed overlap pinholes are filled: the arrow is one
    solid silhouette, with a white stroke only on its exterior boundary.
    """
    segments = [(a, b) for polygon in polygons for a, b in
                zip(polygon, np.roll(polygon, -1, axis=0)) if np.linalg.norm(b-a) > 1e-10]
    cuts = [{0., 1.} for _ in segments]
    for i, (a, b) in enumerate(segments):
        u = b-a
        for j in range(i+1, len(segments)):
            c, d = segments[j]
            v, delta = d-c, c-a
            determinant = _cross(u, v)
            if abs(determinant) > 1e-10:
                t, s = _cross(delta, v)/determinant, _cross(delta, u)/determinant
                if -1e-9 <= t <= 1+1e-9 and -1e-9 <= s <= 1+1e-9:
                    cuts[i].add(float(np.clip(t, 0, 1)))
                    cuts[j].add(float(np.clip(s, 0, 1)))
            elif abs(_cross(delta, u)) < 1e-10:
                for point in [c, d]:
                    t = float(np.dot(point-a, u)/np.dot(u, u))
                    if 0 < t < 1:
                        cuts[i].add(t)
                for point in [a, b]:
                    s = float(np.dot(point-c, v)/np.dot(v, v))
                    if 0 < s < 1:
                        cuts[j].add(s)

    def inside(point):
        x, y = point
        for polygon in polygons:
            odd = False
            for a, b in zip(polygon, np.roll(polygon, -1, axis=0)):
                if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
                    odd = not odd
            if odd:
                return True
        return False

    edges, coordinates = {}, {}
    for (a, b), split in zip(segments, cuts):
        split = sorted(split)
        normal = np.array([-(b-a)[1], (b-a)[0]]) / np.linalg.norm(b-a) * 1e-6
        for lo, hi in zip(split[:-1], split[1:]):
            if hi-lo < 1e-9:
                continue
            start, end = a+(b-a)*lo, a+(b-a)*hi
            midpoint = (start+end)/2
            left, right = inside(midpoint+normal), inside(midpoint-normal)
            if left == right:
                continue  # internal overlap, including the shared neck edge
            if not left:
                start, end = end, start
            key, value = tuple(np.round(start, 8)), tuple(np.round(end, 8))
            if key == value:
                continue
            coordinates[key], coordinates[value] = start, end
            if key in edges and edges[key] != value:
                raise ValueError(f"Ambiguous arrow silhouette boundary at {key}: {edges[key]} / {value}")
            edges[key] = value
    outer = []
    while edges:
        first = min(edges)
        loop, key = [], first
        while True:
            loop.append(coordinates[key])
            key = edges.pop(key)
            if key == first:
                break
        area = sum(_cross(a, b) for a, b in zip(loop, loop[1:] + loop[:1])) / 2
        if area > 1e-10:  # interior-on-left traversal: holes have negative area
            outer.append(loop)
    if len(outer) != 1:
        raise ValueError("Arrow silhouette has disconnected components")
    return np.vstack([outer[0], outer[0][0]])


def arrow_outline(points_pt, *, double_headed=False, head_len=None):
    """Return a closed polygon: filled shaft and concave-backed Stealth head(s)."""
    points = polyline(points_pt)
    length = head_length(points, double_headed=double_headed, head_len=head_len)
    total = path_length(points)
    neck = NECK * length
    last_head, last_direction = head_vertices(points, length)
    if total <= length * (2 if double_headed else 1):
        if double_headed:
            raise ValueError("Double-headed centerline cannot accommodate both heads")
        result = np.vstack([last_head, points[-1] - neck * last_direction])
        return np.vstack([result, result[0]])
    # Keep the curved shaft only up to the beginning of the head chord. Samples
    # nearer the tip would backtrack after connecting to its aligned neck.
    center = trim_path(points, length if double_headed else 0., total - length)
    center = np.vstack([center, points[-1] - neck * last_direction])
    first_head = None
    if double_headed:
        first_head, first_direction = head_vertices(points, length, at_start=True)
        center = np.vstack([points[0] - neck * first_direction, center])
    center = polyline(center)
    directions = np.diff(center, axis=0)
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    tangents = np.vstack([directions[0], directions[:-1] + directions[1:], directions[-1]])
    tangents[-1] = last_direction
    if double_headed:
        tangents[0] = -first_direction
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]
    normals = np.column_stack([-tangents[:, 1], tangents[:, 0]])
    left, right = center + SHAFT / 2 * normals, center - SHAFT / 2 * normals
    result = np.vstack([left, last_head, right[::-1]])
    if first_head is not None:
        result = np.vstack([result, first_head])
    result = np.vstack([result, result[0]])
    if _crosses(result):
        # Segment rectangles plus bevel join triangles give a true constant-
        # width shaft even where a tight turn would fold its offset boundary.
        n = np.column_stack([-directions[:, 1], directions[:, 0]]) * SHAFT / 2
        pieces = [np.array([a+n[i], b+n[i], b-n[i], a-n[i]])
                  for i, (a, b) in enumerate(zip(center[:-1], center[1:]))]
        for i in range(1, len(center)-1):
            pieces.extend([np.array([center[i], center[i]+n[i-1], center[i]+n[i]]),
                           np.array([center[i], center[i]-n[i-1], center[i]-n[i]])])
        pieces.append(np.vstack([left[-1], last_head, right[-1]]))
        if first_head is not None:
            pieces.append(np.vstack([right[0], first_head, left[0]]))
        result = _silhouette_union(pieces)
    return result


def svg_group(points_pt, *, double_headed=False, head_len=None, color=MOTION_COLOR,
              attributes=None):
    points = polyline(points_pt)
    outline = arrow_outline(points, double_headed=double_headed, head_len=head_len)
    group = ET.Element(SVG + "g", {
        "data-motion-arrow": STYLE,
        "data-centerline": json.dumps(points.tolist(), separators=(",", ":")),
        "data-double": str(bool(double_headed)).lower(), "data-color": color,
        **(attributes or {}),
    })
    d = "M " + " L ".join(f"{x:.8f} {y:.8f}" for x, y in outline) + " Z"
    ET.SubElement(group, SVG + "path", {"d": d, "fill": "#FFFFFF", "stroke": "#FFFFFF",
                  "stroke-width": str(2 * RIM), "stroke-linejoin": "round"})
    ET.SubElement(group, SVG + "path", {"d": d, "fill": color})
    return group


def style_manifest():
    return {"source": "scripts/motion_arrow.py", "shaft_pt": SHAFT,
            "white_rim_per_side_pt": RIM, "outer_to_core_ratio": (SHAFT + 2 * RIM) / SHAFT,
            "head": "closed silhouette, concave rear", "head_length_pt": HEAD_LEN,
            "head_width_pt": HEAD_W, "neck_fraction": NECK, "head_min_pt": HEAD_MIN,
            "head_min_width_pt": HEAD_MIN_W, "max_head_fraction": HEAD_FRACTION,
            "direction": "chord over final head length"}
