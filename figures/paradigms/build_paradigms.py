#!/usr/bin/env python3
"""Build Fig. 2 (label fig:paradigms): forecast precision allocated by role.

One recorded scene (t5_replan, frame 29, agent view) illustrates three ways to predict it.
Every panel pairs the full frame with the same enlarged region around the target and the gripper:
  (a) Full-scene             - a stack of recorded future frames
  (b) Target-centric         - target SE(3) trajectory on the current frame
  (c) Role-aware (FoveaWAM)   - target SE(3) trajectory and sparse 3D flow on the current frame

Rasters are Blender renders of recorded states; flow, poses and silhouettes are the recorded
labels projected by prepare_assets.py. Nothing is a model prediction.

Usage (from this directory):
    python prepare_assets.py             # once, or after the labels change
    python build_paradigms.py            # writes paradigms.svg
    python build_paradigms.py --render   # also prints paradigms.pdf / paradigms.png with Chrome

Design units are points at the final single-column width (234 pt = 3.25 in); the SVG is written
in the 900-unit-wide canvas that scripts/common.svg_to_pdf expects. Needs Pillow.
"""
import argparse
import base64
import io
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"

# ---------------------------------------------------------------- canvas and type
W = 234.0                     # pt, single column
K = 900.0 / W                 # SVG units per pt
FONT = "Arial"
HEAD_PT, TEXT_PT = 8.0, 7.0
COMPARISON_PT = 6.8

# ---------------------------------------------------------------- palette
INK = "#111111"
TARGET = "#C0263A"
FLOW_LABEL = "#263E74"
FLOW_BORDER = "#142039"
STATIC_EDGE = "#6E6E6E"
TIME_LABEL = "#31455C"
AXES = ("#D62728", "#2CA02C", "#1F77B4")   # pose axes x, y, z
CHECK = "#2E8540"
RULE = "#A9AFB5"
# Matplotlib turbo's 256-entry LUT, indices 30..168: floor((0.12 + 0.54*t)*256).
# Keeping the sampled sRGB values here reproduces D2 without a matplotlib dependency.
TURBO_COLORS = (
    '#4666dd', '#4669e0', '#466be3', '#476ee6', '#4771e9', '#4773eb', '#4776ee', '#4778f0', '#477bf2', '#467df4',
    '#4680f6', '#4682f8', '#4685fa', '#4687fb', '#458afc', '#458cfd', '#448ffe', '#4391fe', '#4294ff', '#4196ff',
    '#4099ff', '#3e9bfe', '#3d9efe', '#3ba0fd', '#3aa3fc', '#38a5fb', '#37a8fa', '#35abf8', '#33adf7', '#31aff5',
    '#2fb2f4', '#2eb4f2', '#2cb7f0', '#2ab9ee', '#28bceb', '#27bee9', '#25c0e7', '#23c3e4', '#22c5e2', '#20c7df',
    '#1fc9dd', '#1ecbda', '#1ccdd8', '#1bd0d5', '#1ad2d2', '#1ad4d0', '#19d5cd', '#18d7ca', '#18d9c8', '#18dbc5',
    '#18ddc2', '#18dec0', '#18e0bd', '#19e2bb', '#19e3b9', '#1ae4b6', '#1ce6b4', '#1de7b2', '#1fe9af', '#20eaac',
    '#22ebaa', '#25eca7', '#27eea4', '#2aefa1', '#2cf09e', '#2ff19b', '#32f298', '#35f394', '#38f491', '#3cf58e',
    '#3ff68a', '#43f787', '#46f884', '#4af880', '#4ef97d', '#52fa7a', '#55fa76', '#59fb73', '#5dfc6f', '#61fc6c',
    '#65fd69', '#69fd66', '#6dfe62', '#71fe5f', '#75fe5c', '#79fe59', '#7dff56', '#80ff53', '#84ff51', '#88ff4e',
    '#8bff4b', '#8fff49', '#92ff47', '#96fe44', '#99fe42', '#9cfe40', '#9ffd3f', '#a1fd3d', '#a4fc3c', '#a7fc3a',
    '#a9fb39', '#acfb38', '#affa37', '#b1f936', '#b4f836', '#b7f735', '#b9f635', '#bcf534', '#bef434', '#c1f334',
    '#c3f134', '#c6f034', '#c8ef34', '#cbed34', '#cdec34', '#d0ea34', '#d2e935', '#d4e735', '#d7e535', '#d9e436',
    '#dbe236', '#dde037', '#dfdf37', '#e1dd37', '#e3db38', '#e5d938', '#e7d739', '#e9d539', '#ebd339', '#ecd13a',
    '#eecf3a', '#efcd3a', '#f1cb3a', '#f2c93a', '#f4c73a', '#f5c53a', '#f6c33a', '#f7c13a', '#f8be39',
)

# ---------------------------------------------------------------- layout (pt)
GAP = 6.0
HALF = (W - GAP) / 2
HERO_H = 78.0
PAIR_GAP_HERO, PAIR_GAP_TOP = 3.0, 2.0
ZOOM_ASPECT = (W - PAIR_GAP_HERO - HERO_H) / HERO_H
TOP_H = (HALF - PAIR_GAP_TOP) / (1 + ZOOM_ASPECT)
ZOOM_PX = (130.0, 239.5, 370.0)            # x0, y0, width of the enlarged region (640-px frame)
ZOOM_PX_H = ZOOM_PX[2] / ZOOM_ASPECT


# ---------------------------------------------------------------- rasters
def data_uri(image, quality=93):
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, "JPEG", quality=quality, subsampling=0)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def zoom_crop(frame, upsample):
    x0, y0, w = ZOOM_PX
    box = (x0, y0, x0 + w, y0 + ZOOM_PX_H)
    size = (int(round(w * upsample)), int(round(ZOOM_PX_H * upsample)))
    return frame.resize(size, Image.LANCZOS, box=box)


# ---------------------------------------------------------------- SVG writer
class Svg:
    def __init__(self):
        self.out, self.defs, self._clip = [], [], 0

    @staticmethod
    def n(v):
        return f"{v * K:.2f}".rstrip("0").rstrip(".")

    def _attrs(self, kw):
        parts = []
        for key, value in kw.items():
            key = key.rstrip("_").replace("_", "-")
            if key in ("stroke-width", "font-size", "r", "rx"):
                value = self.n(value)
            elif key == "stroke-dasharray":
                value = " ".join(self.n(v) for v in value)
            parts.append(f'{key}="{value}"')
        return " ".join(parts)

    def open(self, name, clip=None):
        extra = f' clip-path="url(#{clip})"' if clip else ""
        self.out.append(f'<g id="{name}"{extra}>')

    def close(self):
        self.out.append("</g>")

    def clip_rect(self, x, y, w, h):
        self._clip += 1
        name = f"clip-{self._clip}"
        self.defs.append(f'<clipPath id="{name}"><rect x="{self.n(x)}" y="{self.n(y)}" '
                         f'width="{self.n(w)}" height="{self.n(h)}"/></clipPath>')
        return name

    def image(self, x, y, w, h, uri):
        self.out.append(f'<image x="{self.n(x)}" y="{self.n(y)}" width="{self.n(w)}" '
                        f'height="{self.n(h)}" preserveAspectRatio="none" href="{uri}"/>')

    def poly(self, pts, closed=True, **kw):
        d = "M" + " L".join(f"{self.n(x)} {self.n(y)}" for x, y in pts) + (" Z" if closed else "")
        kw.setdefault("fill", "none")
        self.out.append(f'<path d="{d}" {self._attrs(kw)}/>')

    def line(self, x0, y0, x1, y1, **kw):
        kw.setdefault("stroke_linecap", "round")
        self.out.append(f'<line x1="{self.n(x0)}" y1="{self.n(y0)}" x2="{self.n(x1)}" '
                        f'y2="{self.n(y1)}" {self._attrs(kw)}/>')

    def rect(self, x, y, w, h, **kw):
        kw.setdefault("fill", "none")
        self.out.append(f'<rect x="{self.n(x)}" y="{self.n(y)}" width="{self.n(w)}" '
                        f'height="{self.n(h)}" {self._attrs(kw)}/>')

    def circle(self, x, y, r, **kw):
        self.out.append(f'<circle cx="{self.n(x)}" cy="{self.n(y)}" r="{self.n(r)}" '
                        f'{self._attrs(kw)}/>')

    def text(self, x, y, content, size=TEXT_PT, anchor="start", fill=INK, weight="normal"):
        content = content.replace("&", "&amp;").replace("<", "&lt;")
        self.out.append(
            f'<text x="{self.n(x)}" y="{self.n(y)}" font-family="{FONT}" font-size="{self.n(size)}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{content}</text>')

    def arrow(self, x0, y0, x1, y1, color, width, head, casing=0.0):
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length < 1e-6:
            return
        ux, uy = dx / length, dy / length
        head = min(head, 0.6 * length)
        bx, by = x1 - ux * head, y1 - uy * head
        hw = head * 0.40
        tri = [(x1, y1), (bx - uy * hw, by + ux * hw), (bx + uy * hw, by - ux * hw)]
        if casing:
            self.line(x0, y0, bx, by, stroke="#FFFFFF", stroke_width=width + casing)
            self.poly(tri, fill="#FFFFFF", stroke="#FFFFFF", stroke_width=casing,
                      stroke_linejoin="round")
        self.line(x0, y0, bx + ux * 0.2, by + uy * 0.2, stroke=color, stroke_width=width)
        self.poly(tri, fill=color)


# ---------------------------------------------------------------- overlays
class View:
    """Maps 640-px frame coordinates into a picture placed at (x, y) with `scale` pt per px."""

    def __init__(self, x, y, scale, px0=0.0, py0=0.0):
        self.x, self.y, self.scale, self.px0, self.py0 = x, y, scale, px0, py0

    def __call__(self, px, py):
        return self.x + (px - self.px0) * self.scale, self.y + (py - self.py0) * self.scale

    def pts(self, points):
        return [self(px, py) for px, py in points]


def time_color(fraction):
    """Fig. 1(a)'s turbo 0.12..0.66, with 0 = now and 1 = +400 ms."""
    return TURBO_COLORS[int((0.12 + 0.54 * fraction) * 256) - 30]


def flow_shaft(svg, pts, width, head, border):
    """Time-coloured arrow along eight recorded 50 ms steps, ending at +400 ms."""
    end, prev = pts[-1], pts[-2]
    dx, dy = end[0] - prev[0], end[1] - prev[1]
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return
    ux, uy = dx / length, dy / length
    seg_lens = [math.dist(a, b) for a, b in zip(pts[:-1], pts[1:])]
    head = min(head, 0.9 * sum(seg_lens))
    neck = (end[0] - ux * head, end[1] - uy * head)
    nx, ny = -uy * head * 0.46, ux * head * 0.46
    tri = [end, (neck[0] + nx, neck[1] + ny), (neck[0] - nx, neck[1] - ny)]
    # Trim the shaft behind the arrowhead while preserving each point's time.
    shaft, times, acc = [pts[0]], [0.0], 0.0
    stop = sum(seg_lens) - head * 0.85
    for k, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        if acc + seg_lens[k] >= stop:
            t = (stop - acc) / max(seg_lens[k], 1e-9)
            shaft.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            times.append((k + t) / 8)
            break
        acc += seg_lens[k]
        shaft.append(b)
        times.append((k + 1) / 8)
    svg.poly(shaft, closed=False, stroke=FLOW_BORDER, stroke_width=width + border * 2,
             stroke_linecap="round", stroke_linejoin="round", stroke_opacity=0.82)
    svg.poly(tri, fill=FLOW_BORDER, stroke=FLOW_BORDER, stroke_width=border * 2,
             stroke_linejoin="round", stroke_opacity=0.82)
    for (a, b), (ta, tb) in zip(zip(shaft[:-1], shaft[1:]), zip(times[:-1], times[1:])):
        for j in range(3):                             # at least three pieces per 50 ms
            s0, s1 = j / 3, (j + 1) / 3
            p0 = (a[0] + (b[0] - a[0]) * s0, a[1] + (b[1] - a[1]) * s0)
            p1 = (a[0] + (b[0] - a[0]) * s1, a[1] + (b[1] - a[1]) * s1)
            svg.line(*p0, *p1, stroke=time_color(ta + (tb - ta) * (s0 + s1) / 2),
                     stroke_width=width, stroke_linecap="butt" if j else "round")
    svg.poly(tri, fill=time_color(1.0))


def draw_flow(svg, view, lattice, *, dot, casing, width, head, border):
    for sample in lattice:                              # static samples first, arrows above
        if not sample["moving"]:
            svg.circle(*view(*sample["src"]), dot * 0.7, fill="#FFFFFF", stroke=STATIC_EDGE,
                       stroke_width=casing * 1.1)
    for sample in lattice:
        if sample["moving"]:
            pts = [view(*sample["src"])] + view.pts(sample["track"])
            flow_shaft(svg, pts, width, head, border)
            svg.circle(*pts[0], dot * 0.8, fill="#FFFFFF", stroke=time_color(0.0),
                       stroke_width=casing * 1.3)


def draw_target(svg, view, overlay, *, lw, detail):
    """Target SE(3) forecast: silhouette at +400 ms, origin path with 50 ms ticks, pose frames."""
    outlines = overlay["outlines"]
    if detail:
        svg.poly(view.pts(outlines["0"]), stroke=TARGET, stroke_width=lw * 0.55,
                 stroke_linejoin="round")
    svg.poly(view.pts(outlines["8"]), stroke="#FFFFFF", stroke_width=lw * 1.7, stroke_linejoin="round",
             stroke_opacity=0.75)
    svg.poly(view.pts(outlines["8"]), fill=TARGET, fill_opacity=0.14, stroke=TARGET, stroke_width=lw,
             stroke_linejoin="round")
    if not detail:
        return
    path = view.pts(overlay["target_origin_px"])
    svg.poly(path, closed=False, stroke="#FFFFFF", stroke_width=lw * 1.9, stroke_linecap="round",
             stroke_linejoin="round")
    svg.poly(path, closed=False, stroke=TARGET, stroke_width=lw * 0.85, stroke_linecap="round",
             stroke_linejoin="round")
    for x, y in path[1:-1]:                              # the 50 ms horizons in between
        svg.circle(x, y, lw * 0.5, fill="#FFFFFF", stroke=TARGET, stroke_width=lw * 0.32)
    for key, weight in (("0", 0.72), ("8", 1.0)):
        triad = overlay["triads"][key]
        ox, oy = view(*triad["origin"])
        for tip, colour in zip(triad["tips"], AXES):
            svg.arrow(ox, oy, *view(*tip), colour, lw * weight, lw * 2.5 * weight,
                      casing=lw * 0.8 * weight)
    for key, weight in (("0", 0.72), ("8", 1.0)):
        svg.circle(*view(*overlay["triads"][key]["origin"]), lw * 1.05 * weight,
                   fill="#FFFFFF", stroke=TARGET, stroke_width=lw * 0.55 * weight)


def frame_border(svg, x, y, w, h):
    svg.rect(x, y, w, h, stroke=RULE, stroke_width=0.4)


def zoom_link(svg, full, zx, zy, zh):
    """Outline the enlarged region on the full frame and tie it to the enlarged picture."""
    x0, y0 = full(ZOOM_PX[0], ZOOM_PX[1])
    x1, y1 = full(ZOOM_PX[0] + ZOOM_PX[2], ZOOM_PX[1] + ZOOM_PX_H)
    svg.rect(x0, y0, x1 - x0, y1 - y0, stroke="#FFFFFF", stroke_width=1.1)
    svg.rect(x0, y0, x1 - x0, y1 - y0, stroke=INK, stroke_width=0.5)
    for (ax, ay), (bx, by) in (((x1, y0), (zx, zy)), ((x1, y1), (zx, zy + zh))):
        svg.line(ax, ay, bx, by, stroke=INK, stroke_width=0.35, stroke_opacity=0.75)


# ---------------------------------------------------------------- figure
def build():
    overlay = json.loads((ASSETS / "overlay.json").read_text(encoding="utf-8"))
    px = overlay["image_px"]
    now = Image.open(ASSETS / "frame_now.png").convert("RGB")
    futures = [Image.open(ASSETS / f"frame_p{t}.png").convert("RGB") for t in ("050", "200", "400")]
    lattice = overlay["lattice"]

    svg = Svg()
    head_y, pic_y = 7.8, 11.6
    check_y = pic_y + TOP_H + 7.1
    cross_y = check_y + 8.3
    hero_head = cross_y + 10.8
    hero_y = hero_head + 3.9
    height = hero_y + HERO_H + 0.5

    def comparison(x, positive, negative):
        y = check_y - 2.5
        svg.poly([(x + 0.7, y + 0.1), (x + 2.3, y + 1.8), (x + 5.5, y - 2.0)],
                 closed=False, stroke=CHECK, stroke_width=1.0, stroke_linecap="round",
                 stroke_linejoin="round")
        svg.text(x + 7.0, check_y, positive, size=COMPARISON_PT)
        y = cross_y - 2.5
        for direction in (1, -1):
            svg.line(x + 2.7 - 1.9 * direction, y - 1.9,
                     x + 2.7 + 1.9 * direction, y + 1.9,
                     stroke=TARGET, stroke_width=1.0)
        svg.text(x + 7.0, cross_y, negative, size=COMPARISON_PT)

    def pair(name, x, y, side, gap, full_image, zoom_image, stack=()):
        """Full frame and enlarged region; returns their views and the zoom clip."""
        zw = side * ZOOM_ASPECT
        zx = x + side + gap
        svg.open(name)
        off = 1.7
        inner = side - off * len(stack)
        for depth, image in enumerate(stack):               # earlier frames behind
            shift = off * (len(stack) - depth)
            svg.image(x + shift, y + off * len(stack) - shift, inner, inner, data_uri(image))
            frame_border(svg, x + shift, y + off * len(stack) - shift, inner, inner)
        fy = y + off * len(stack)
        svg.image(x, fy, inner, inner, data_uri(full_image))
        frame_border(svg, x, fy, inner, inner)
        svg.image(zx, y, zw, side, data_uri(zoom_image))
        full = View(x, fy, inner / px)
        zoom = View(zx, y, zw / ZOOM_PX[2], ZOOM_PX[0], ZOOM_PX[1])
        return full, zoom, (zx, y, zw, side)

    # ---- (a) Full-scene
    svg.text(0.2, head_y, "(a) Full-scene", size=HEAD_PT, weight="bold")
    small = [f.resize((240, 240), Image.LANCZOS) for f in futures]
    full, zoom, box = pair("a-full-scene", 0.0, pic_y, TOP_H, PAIR_GAP_TOP, futures[2].resize((320, 320), Image.LANCZOS),
                           zoom_crop(futures[2], 2.0), stack=small[:2])
    zoom_link(svg, full, box[0], box[1], box[3])
    frame_border(svg, *box)
    svg.close()
    comparison(0.0, "Whole scene", "Target pose implicit")

    # ---- (b) Target-centric predictors
    bx = W - HALF
    svg.text(bx + 0.2, head_y, "(b) Target-centric", size=HEAD_PT, weight="bold")
    full, zoom, box = pair("b-target-centric", bx, pic_y, TOP_H, PAIR_GAP_TOP,
                           now.resize((320, 320), Image.LANCZOS), zoom_crop(now, 2.0))
    draw_target(svg, full, overlay, lw=0.45, detail=False)
    zoom_link(svg, full, box[0], box[1], box[3])
    svg.open("b-target-futures", clip=svg.clip_rect(*box))
    draw_target(svg, zoom, overlay, lw=0.7, detail=True)
    svg.close()
    frame_border(svg, *box)
    svg.close()
    comparison(bx, "Target trajectory", "Surroundings omitted")

    # ---- (c) Role-aware
    svg.text(0.2, hero_head, "(c) Role-aware (FoveaWAM)", size=HEAD_PT, weight="bold")
    full, zoom, box = pair("c-foveawam", 0.0, hero_y, HERO_H, PAIR_GAP_HERO, now,
                           zoom_crop(now, 3.0))
    svg.open("c-flow-full", clip=svg.clip_rect(0.0, hero_y, HERO_H, HERO_H))
    draw_flow(svg, full, lattice, dot=0.62, casing=0.26, width=0.62, head=1.9, border=0.16)
    draw_target(svg, full, overlay, lw=0.5, detail=False)
    svg.close()
    zoom_link(svg, full, box[0], box[1], box[3])
    svg.open("c-zoom-overlays", clip=svg.clip_rect(*box))
    on_target = [s for s in lattice if s["instance"] == "target"]
    draw_flow(svg, zoom, [s for s in lattice if s["instance"] != "target"], dot=1.15, casing=0.42,
              width=0.95, head=3.0, border=0.22)
    draw_flow(svg, zoom, on_target, dot=1.15, casing=0.42, width=0.95, head=3.0, border=0.22)
    draw_target(svg, zoom, overlay, lw=0.95, detail=True)
    svg.close()
    frame_border(svg, *box)
    annotate(svg, zoom, overlay)
    svg.close()
    # Right-aligned time key on the (c) heading line, as in the approved D2 preview.
    x1 = W - 0.3
    svg.text(x1, hero_head, "+400 ms", size=COMPARISON_PT, anchor="end", fill=TIME_LABEL)
    ax1, ax0, y = x1 - 28.0, x1 - 50.0, hero_head - 2.4
    flow_shaft(svg, [(ax0 + (ax1 - ax0) * k / 8, y) for k in range(9)], 1.0, 3.0, 0.2)
    svg.circle(ax0, y, 0.95, fill="#FFFFFF", stroke=time_color(0.0), stroke_width=0.42)
    svg.text(ax0 - 2.0, hero_head, "0", size=COMPARISON_PT, anchor="end", fill=TIME_LABEL)
    return svg, height


def annotate(svg, zoom, overlay):
    """Direct labels in the wording of Fig. 1, set between lattice rows so no sample is hidden."""
    rows = sorted({round(s["src"][1], 2) for s in overlay["lattice"]})
    inside = [zoom(0, r)[1] for r in rows if ZOOM_PX[1] < r < ZOOM_PX[1] + ZOOM_PX_H]
    # target label between the third and fourth visible rows, right of the +400 ms silhouette
    right = max(x for x, _ in overlay["outlines"]["8"])
    top = min(y for _, y in overlay["outlines"]["8"])
    lx = zoom(right, 0)[0] + 13.0
    ly = inside[2] + 8.0
    svg.line(zoom(right, 0)[0] + 1.2, zoom(0, top)[1] + 6.5, lx - 1.6, ly - 2.4,
             stroke=TARGET, stroke_width=0.5)
    svg.text(lx, ly, "Target SE(3)", fill=TARGET, weight="bold")
    # flow label between the first and second rows, left of the first robot arrow
    x0, y0, w = ZOOM_PX
    moving = [s for s in overlay["lattice"] if s["moving"] and s["instance"] != "target"
              and x0 < s["src"][0] < x0 + w and y0 < s["src"][1] < y0 + ZOOM_PX_H]
    first = min(moving, key=lambda s: s["src"][0])
    (sx, sy), (ex, ey) = zoom(*first["src"]), zoom(*first["end"])
    fy = inside[0] + 12.3
    mx = sx + (ex - sx) * (fy - 2.4 - sy) / (ey - sy)     # where the arrow crosses the text line
    svg.line(mx - 2.0, fy - 2.4, mx - 8.0, fy - 2.4, stroke=FLOW_LABEL, stroke_width=0.5)
    svg.text(mx - 9.6, fy, "Sparse 3D flow", fill=FLOW_LABEL, weight="bold", anchor="end")


def write(path):
    svg, height = build()
    h_units = int(math.ceil(height * K))
    doc = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {h_units}" '
           f'width="900" height="{h_units}">',
           "<defs>", *svg.defs, "</defs>",
           f'<rect width="900" height="{h_units}" fill="#FFFFFF"/>', *svg.out, "</svg>"]
    Path(path).write_text("\n".join(doc) + "\n", encoding="utf-8")
    return h_units


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true", help="print PDF and PNG with Chromium")
    args = parser.parse_args()
    svg_path = HERE / "paradigms.svg"
    h_units = write(svg_path)
    print(json.dumps({"svg": svg_path.name, "viewbox": [900, h_units],
                      "size_in": [3.25, round(3.25 * h_units / 900, 3)]}))
    if args.render:
        sys.path.insert(0, str(HERE.parents[1] / "scripts"))
        from common import svg_to_pdf
        with tempfile.TemporaryDirectory() as tmp:
            svg_to_pdf(svg_path, HERE / "paradigms.pdf", preview_dir=tmp)
            shutil.copyfile(Path(tmp) / "paradigms.png", HERE / "paradigms.png")


if __name__ == "__main__":
    main()
