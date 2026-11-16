#!/usr/bin/env python3
"""Recolour Fig. 4 (OnTimeBench overview) to the 2026-11-16 paper palette.

Interim step: rewrites the colours of figures/Fig4/ontimebench.svg and adjusts the
embedded renders in place. The final version should change the Blender materials
(conveyor green, slate table tops) and re-render instead of post-processing pixels.

Usage (from the repo root):
    python tmp/palette_20261116/recolor_fig4.py figures/Fig4/ontimebench.svg out.svg
Needs numpy and Pillow.
"""
import base64
import io
import re
import sys

import numpy as np
from PIL import Image

# ---- core palette (docs: claude/palette_spec_20261116.md in the claude.ai project)
RED, BLUE, GREEN, AMBER, PURPLE = "#C0263A", "#2859A3", "#2E8540", "#E69F00", "#9467BD"
INK = "#1A1A1A"
BLUE_LIGHT = "#7191BF"          # past-pose contours (unchanged from the original)

# family -> colour (frames and donut)
FAMILY = {"grasp": BLUE, "place": GREEN, "pass": PURPLE, "capture": AMBER, "impact": RED}

# old hex -> new hex
MAP = {
    # object motion stays blue; rotation cue joins it
    "#2859A3": BLUE, "#7191BF": BLUE_LIGHT, "#87A6D0": BLUE_LIGHT, "#5277AE": BLUE, "#596873": BLUE,
    # striker arrows -> ink
    "#B25244": INK, "#263441": INK,
    # titles and labels -> ink
    "#1F2328": INK, "#244574": INK, "#215852": INK, "#564171": INK, "#6D4916": INK, "#823D37": INK,
    # card fills -> white
    "#EDF2FA": "#FFFFFF", "#EDF6F4": "#FFFFFF", "#F3EFF8": "#FFFFFF", "#FAEEEA": "#FFFFFF",
    "#FBF4E6": "#FFFFFF", "#F4F5F5": "#FFFFFF",
    # card frames -> family colour; legend card frame -> light grey
    "#B9CAE5": FAMILY["grasp"], "#B7D6CF": FAMILY["place"], "#D4C7E4": FAMILY["pass"],
    "#E7D2A6": FAMILY["capture"], "#E7C4BD": FAMILY["impact"], "#CFD4D8": "#D6D6D6",
    # donut segments -> family colour
    "#829FD3": FAMILY["grasp"], "#76ADA8": FAMILY["place"], "#A993C8": FAMILY["pass"],
    "#DDB05E": FAMILY["capture"], "#DC9085": FAMILY["impact"],
    # (a): drop the pill fills; pause = red (wrong), advance = green (right)
    "#FAE9EB": "#FFFFFF", "#E7F3EB": "#FFFFFF", "#AE2632": RED, "#176541": GREEN,
}

CONVEYOR_DESAT = 0.0            # reverted 2026-11-16: the glare came from belt specular, not colour; fix in Blender (specular 0.15)
PROTOCOL_PANEL_PX = (428, 372)  # the two images in panel (a)


# ---- colour helpers
def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 1e-6, (mx - mn) / (mx + 1e-9), 0)
    return h, s, mx


def hsv2rgb(h, s, v):
    h = (h % 360) / 60
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(h.shape + (3,))
    for k, (r, g, b) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[m] = np.stack([r[m], g[m], b[m]], -1)
    return out


def window(h, lo, hi, soft=10):
    return np.minimum(np.clip((h - (lo - soft)) / soft, 0, 1), np.clip(((hi + soft) - h) / soft, 0, 1))


def adjust_render(im, panel):
    """Conveyor green -25 % saturation; slate-blue table tops -> neutral dark grey.

    Translucent blue past-pose ghosts are protected; the blue sphere in the Pass tiles is left
    alone because only images dominated by slate are treated."""
    rgba = im.convert("RGBA")
    alpha = np.asarray(rgba)[..., 3]
    a = np.asarray(rgba.convert("RGB")).astype(float) / 255
    h, s, v = rgb2hsv(a)
    wg = window(h, 80, 170) * np.clip((s - 0.15) / 0.12, 0, 1)
    s2 = s * (1 - wg * CONVEYOR_DESAT)
    slate = (window(h, 195, 235) * ((s > 0.12) & (s < 0.5) & (v < 0.7))).mean()
    if panel or slate > 0.12:
        ghost = 0 if panel else window(h, 200, 235) * np.clip((s - 0.36) / 0.06, 0, 1) * np.clip((v - 0.48) / 0.06, 0, 1)
        wt = window(h, 195, 235) * np.clip((s - 0.1) / 0.06, 0, 1) * (1 - ghost)
        s2 = s2 * (1 - wt * 0.9)
    out = Image.fromarray((np.clip(hsv2rgb(h, s2, v), 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(Image.fromarray(alpha))
    return out


def main(src, dst):
    s = open(src, encoding="utf-8").read()
    # the first two uses of #176541 are the 18 cm displacement arrow and its label: object motion -> blue
    idx = [m.start() for m in re.finditer("#176541", s)]
    for i in reversed(idx[:2]):
        s = s[:i] + BLUE + s[i + 7:]
    for old, new in MAP.items():
        s = re.sub(re.escape(old), new, s, flags=re.I)

    def rep(m):
        im = Image.open(io.BytesIO(base64.b64decode(m.group(2))))
        out = adjust_render(im, im.size == PROTOCOL_PANEL_PX)
        buf = io.BytesIO()
        out.save(buf, "PNG")
        return f'href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"'

    s = re.sub(r'href="data:image/(\w+);base64,([^"]*)"', rep, s)
    open(dst, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
