"""Build colour-preview variants of Fig. 2 (paradigms) from the real assets."""
import sys, json, math, shutil
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
sys.path.insert(0, "/home/claude/src")
from recolor_svg import process_image

HERE = Path(__file__).parent
cmap_name, lo, hi, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
# desaturated conveyor frames
A = HERE / "assets"; A.mkdir(exist_ok=True)
shutil.copy(HERE / "assets_raw/overlay.json", A / "overlay.json")
for f in ["frame_now", "frame_p050", "frame_p200", "frame_p400"]:
    process_image(Image.open(HERE / f"assets_raw/{f}.png"), "render").convert("RGB").save(A / f"{f}.png")

import build_paradigms as bp
bp.ASSETS = A
bp.TARGET, bp.TARGET_DK = "#C0263A", "#8C1526"
bp.BAD = "#8C8C8C"
bp.RULE = "#B3B3B3"
cm = matplotlib.colormaps[cmap_name]
def col(t):
    r, g, b, _ = cm(lo + (hi - lo) * t)
    return "#%02X%02X%02X" % (int(r * 255), int(g * 255), int(b * 255))
bp.FLOW_DK = "#1A1A1A"
bp.FLOW = "#1A1A1A"

def draw_flow(svg, view, lattice, *, dot, casing, width, head):
    for s in lattice:
        if not s["moving"]:
            svg.circle(*view(*s["src"]), dot * 0.8, fill="#FFFFFF", stroke="#4D4D4D", stroke_width=casing * 0.9)
    for s in lattice:
        if not s["moving"]:
            continue
        (x0, y0), (x1, y1) = view(*s["src"]), view(*s["end"])
        n = 8
        pts = [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n + 1)]
        L = math.hypot(x1 - x0, y1 - y0)
        hd = min(head, 0.45 * L)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        bx, by = x1 - ux * hd, y1 - uy * hd
        svg.line(x0, y0, bx, by, stroke="#FFFFFF", stroke_width=width + casing * 2.2)
        hw = hd * 0.42
        tri = [(x1, y1), (bx - uy * hw, by + ux * hw), (bx + uy * hw, by - ux * hw)]
        svg.poly(tri, fill="#FFFFFF", stroke="#FFFFFF", stroke_width=casing * 2, stroke_linejoin="round")
        for k in range(n):
            ax, ay = pts[k]; ex, ey = pts[k + 1]
            if k == n - 1:
                ex, ey = bx + ux * 0.2, by + uy * 0.2
            svg.line(ax, ay, ex, ey, stroke=col(k / (n - 1)), stroke_width=width, stroke_linecap="butt")
        svg.poly(tri, fill=col(1.0))
        svg.circle(x0, y0, dot, fill=col(0.0), stroke="#FFFFFF", stroke_width=casing)
bp.draw_flow = draw_flow
h = bp.write(out)
print(out, h, [col(t) for t in (0, .5, 1)])
