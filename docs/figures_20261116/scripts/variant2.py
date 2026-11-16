import sys, math
sys.argv = [sys.argv[0]] + sys.argv[1:]
cmap_name, lo, hi, out, axes = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
import variant  # noqa: builds assets + defines col/draw_flow, writes a first version
import build_paradigms as bp
col = variant.col
AX = {"rviz": ("#FF0000", "#00FF00", "#0000FF"), "blender": ("#FF3352", "#8BDC00", "#2890FF"), "tab": ("#D62728", "#2CA02C", "#1F77B4")}
if axes in AX:
    bp.AXES = AX[axes]
elif axes == "red":
    bp.AXES = ("#8C1526", "#8C1526", "#8C1526")
def draw_flow(svg, view, lattice, *, dot, casing, width, head):
    for s in lattice:
        if not s["moving"]:
            svg.circle(*view(*s["src"]), dot * 0.75, fill="#FFFFFF", stroke="#595959", stroke_width=casing * 0.9)
    for s in lattice:
        if not s["moving"]:
            continue
        (x0, y0), (x1, y1) = view(*s["src"]), view(*s["end"])
        n = 8
        pts = [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n + 1)]
        svg.line(x0, y0, x1, y1, stroke="#FFFFFF", stroke_width=dot * 1.9, stroke_opacity=0.85)
        for k in range(n):
            (ax, ay), (ex, ey) = pts[k], pts[k + 1]
            svg.line(ax, ay, ex, ey, stroke=col(k / (n - 1)), stroke_width=width * 0.75, stroke_linecap="round")
        for k, (x, y) in enumerate(pts):
            svg.circle(x, y, dot * (0.55 if 0 < k < n else 0.8), fill=col(max(0, k - 1) / (n - 1)))
bp.draw_flow = draw_flow
bp.write(out)
