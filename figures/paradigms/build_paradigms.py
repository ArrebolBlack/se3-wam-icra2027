#!/usr/bin/env python3
"""Build Fig. 2 (label fig:paradigms): forecast precision allocated by role.

One recorded scene (t5_replan, frame 29, agent view) is shown as three forecasts. Every panel
pairs the full frame with the same enlarged region around the target and the gripper:
  (a) Video WAMs     - the recorded future frames themselves; nothing is explicit
  (b) Target-centric - observation history and target SE(3) futures only
  (c) FoveaWAM       - the same context, sparse 3D flow and the target SE(3) futures

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
TARGET = "#A92466"            # Fig. 1 target colour
TARGET_DK = "#912054"
FLOW = "#2859A3"              # Fig. 1 flow colour
FLOW_DK = "#214B8A"
AXES = ("#D62728", "#2CA02C", "#1F77B4")   # pose axes x, y, z
BAD = "#C4262E"
RULE = "#A9AFB5"

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


def draw_flow(svg, view, lattice, *, dot, casing, width, head):
    for sample in lattice:                              # static samples first, arrows above
        if not sample["moving"]:
            svg.circle(*view(*sample["src"]), dot, fill=FLOW, stroke="#FFFFFF", stroke_width=casing)
    for sample in lattice:
        if sample["moving"]:
            x0, y0 = view(*sample["src"])
            svg.arrow(x0, y0, *view(*sample["end"]), FLOW, width, head, casing=casing * 2.6)
            svg.circle(x0, y0, dot, fill=FLOW, stroke="#FFFFFF", stroke_width=casing)


def draw_target(svg, view, overlay, *, lw, detail):
    """Target SE(3) forecast: silhouette at +400 ms, origin path with 50 ms ticks, pose frames."""
    outlines = overlay["outlines"]
    if detail:
        svg.poly(view.pts(outlines["0"]), stroke=TARGET_DK, stroke_width=lw * 0.55,
                 stroke_linejoin="round")
    svg.poly(view.pts(outlines["8"]), stroke="#FFFFFF", stroke_width=lw * 1.7, stroke_linejoin="round",
             stroke_opacity=0.75)
    svg.poly(view.pts(outlines["8"]), fill=TARGET, fill_opacity=0.14, stroke=TARGET, stroke_width=lw,
             stroke_linejoin="round")
    if not detail:
        return
    path = view.pts(overlay["target_origin_px"])
    svg.poly(path, closed=False, stroke="#FFFFFF", stroke_width=lw * 1.7, stroke_linecap="round",
             stroke_linejoin="round")
    svg.poly(path, closed=False, stroke=INK, stroke_width=lw * 0.7, stroke_linecap="round",
             stroke_linejoin="round")
    for x, y in path[1:-1]:                              # the 50 ms horizons in between
        svg.circle(x, y, lw * 0.5, fill="#FFFFFF", stroke=INK, stroke_width=lw * 0.32)
    for key, weight in (("0", 0.72), ("8", 1.0)):
        triad = overlay["triads"][key]
        ox, oy = view(*triad["origin"])
        for tip, colour in zip(triad["tips"], AXES):
            svg.arrow(ox, oy, *view(*tip), colour, lw * weight, lw * 2.5 * weight,
                      casing=lw * 0.8 * weight)
        svg.circle(ox, oy, lw * 0.95 * weight, fill=INK, stroke="#FFFFFF", stroke_width=lw * 0.4)


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
    history = [
        Image.open(ASSETS / f"frame_m{t}.png").convert("RGB").resize((240, 240), Image.LANCZOS)
        for t in ("350", "200")
    ]
    lattice = overlay["lattice"]

    svg = Svg()
    head_y, pic_y = 7.8, 11.6
    comparison_y = pic_y + TOP_H + 8.6
    hero_head = comparison_y + 14.0
    hero_y = hero_head + 3.9
    height = hero_y + HERO_H + 0.5

    def comparison(x, positive, cross_x, negative):
        y = comparison_y - 2.5
        svg.poly([(x + 0.7, y + 0.1), (x + 2.3, y + 1.8), (x + 5.5, y - 2.0)],
                 closed=False, stroke=INK, stroke_width=1.0, stroke_linecap="round",
                 stroke_linejoin="round")
        svg.text(x + 7.0, comparison_y, positive, size=COMPARISON_PT)
        for direction in (1, -1):
            svg.line(cross_x + 2.7 - 1.9 * direction, y - 1.9,
                     cross_x + 2.7 + 1.9 * direction, y + 1.9,
                     stroke=BAD, stroke_width=1.0)
        svg.text(cross_x + 6.6, comparison_y, negative, size=COMPARISON_PT)

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

    # ---- (a) Video WAMs
    svg.text(0.2, head_y, "(a) Video WAMs", size=HEAD_PT, weight="bold")
    small = [f.resize((240, 240), Image.LANCZOS) for f in futures]
    full, zoom, box = pair("a-video-wams", 0.0, pic_y, TOP_H, PAIR_GAP_TOP, futures[2].resize((320, 320), Image.LANCZOS),
                           zoom_crop(futures[2], 2.0), stack=small[:2])
    zoom_link(svg, full, box[0], box[1], box[3])
    frame_border(svg, *box)
    svg.close()
    comparison(0.0, "Whole scene", 48.0, "Target pose implicit")

    # ---- (b) Target-centric predictors
    bx = W - HALF
    svg.text(bx + 0.2, head_y, "(b) Target-centric", size=HEAD_PT, weight="bold")
    full, zoom, box = pair("b-target-centric", bx, pic_y, TOP_H, PAIR_GAP_TOP,
                           now.resize((320, 320), Image.LANCZOS), zoom_crop(now, 2.0), stack=history)
    draw_target(svg, full, overlay, lw=0.45, detail=False)
    zoom_link(svg, full, box[0], box[1], box[3])
    svg.open("b-target-futures", clip=svg.clip_rect(*box))
    draw_target(svg, zoom, overlay, lw=0.7, detail=True)
    svg.close()
    frame_border(svg, *box)
    svg.close()
    comparison(bx, "Target trajectory", bx + 58.8, "Context omitted")

    # ---- (c) FoveaWAM
    svg.text(0.2, hero_head, "(c) FoveaWAM", size=HEAD_PT, weight="bold")
    full, zoom, box = pair("c-foveawam", 0.0, hero_y, HERO_H, PAIR_GAP_HERO, now,
                           zoom_crop(now, 3.0))
    svg.open("c-flow-full", clip=svg.clip_rect(0.0, hero_y, HERO_H, HERO_H))
    draw_flow(svg, full, lattice, dot=0.62, casing=0.26, width=0.55, head=1.7)
    draw_target(svg, full, overlay, lw=0.5, detail=False)
    svg.close()
    zoom_link(svg, full, box[0], box[1], box[3])
    svg.open("c-zoom-overlays", clip=svg.clip_rect(*box))
    on_target = [s for s in lattice if s["instance"] == "target"]
    draw_flow(svg, zoom, [s for s in lattice if s["instance"] != "target"], dot=1.15, casing=0.42,
              width=0.9, head=2.9)
    draw_target(svg, zoom, overlay, lw=0.95, detail=True)
    draw_flow(svg, zoom, on_target, dot=1.15, casing=0.42, width=0.9, head=2.9)   # the one sample on it
    svg.close()
    frame_border(svg, *box)
    annotate(svg, zoom, overlay)
    svg.close()
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
             stroke=TARGET_DK, stroke_width=0.5)
    svg.text(lx, ly, "Target SE(3)", fill=TARGET_DK, weight="bold")
    # flow label between the first and second rows, left of the first robot arrow
    x0, y0, w = ZOOM_PX
    moving = [s for s in overlay["lattice"] if s["moving"] and s["instance"] != "target"
              and x0 < s["src"][0] < x0 + w and y0 < s["src"][1] < y0 + ZOOM_PX_H]
    first = min(moving, key=lambda s: s["src"][0])
    (sx, sy), (ex, ey) = zoom(*first["src"]), zoom(*first["end"])
    fy = inside[0] + 12.3
    mx = sx + (ex - sx) * (fy - 2.4 - sy) / (ey - sy)     # where the arrow crosses the text line
    svg.line(mx - 2.0, fy - 2.4, mx - 8.0, fy - 2.4, stroke=FLOW_DK, stroke_width=0.5)
    svg.text(mx - 9.6, fy, "Sparse 3D flow", fill=FLOW_DK, weight="bold", anchor="end")


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
