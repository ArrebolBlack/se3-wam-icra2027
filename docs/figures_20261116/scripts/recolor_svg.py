"""Preview palette v2 ('foveal colour') on the real figure SVGs. Preview only, not the production pipeline."""
import re, io, base64, sys
import numpy as np
from PIL import Image

INK = "#1A1A1A"
T, T_DK, T_LT = "#C0263A", "#8C1526", "#E3949C"
FLOW, FLOW_DK = "#2A2A2A", "#1A1A1A"
G = {"g70": "#4D4D4D", "g55": "#6E6E6E", "g45": "#8C8C8C", "g35": "#A6A6A6", "g25": "#BFBFBF",
     "g15": "#D6D6D6", "g08": "#EBEBEB", "g04": "#F5F5F5"}
T_HUE = 352.0  # degrees, for re-hued ghosts in renders


def rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 1e-6, (mx - mn) / (mx + 1e-9), 0)
    return h, s, mx


def hsv2rgb(h, s, v):
    h = (h % 360) / 60; i = np.floor(h).astype(int) % 6; f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(h.shape + (3,))
    for k, (r, g, b) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[m] = np.stack([r[m], g[m], b[m]], -1)
    return out


def win(h, lo, hi, soft=10):
    return np.minimum(np.clip((h - (lo - soft)) / soft, 0, 1), np.clip(((hi + soft) - h) / soft, 0, 1))


def process_image(im, kind):
    rgba = im.convert("RGBA"); alpha = np.asarray(rgba)[..., 3]
    a = np.asarray(rgba.convert("RGB")).astype(float) / 255
    h, s, v = rgb2hsv(a)
    if kind == "mild":
        wg = win(h, 80, 170) * np.clip((s - 0.15) / 0.12, 0, 1)
        out = hsv2rgb(h, s * (1 - wg * 0.22), np.clip(v * (1 + wg * 0.03), 0, 1))
        out = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
        out.putalpha(Image.fromarray(alpha)); return out
    if kind == "photo":
        s2 = s * 0.85  # global grade only, no local edits on the real photo
        out = hsv2rgb(h, s2, v)
    else:
        # conveyor green: keep green, cut saturation
        wg = win(h, 80, 170) * np.clip((s - 0.15) / 0.12, 0, 1)
        s2 = s * (1 - wg * 0.66)
        v2 = v * (1 - wg * 0.06)
        # translucent blue past-pose ghosts -> target hue (not on the protocol panels)
        wb = win(h, 200, 235) * np.clip((s - 0.36) / 0.06, 0, 1) * np.clip((v - 0.48) / 0.06, 0, 1)
        if kind in ("panel", "render_keep"):
            wb = wb * 0
        # slate-blue table tops -> neutral dark grey
        wt = win(h, 195, 235) * np.clip((s - 0.1) / 0.06, 0, 1) * (1 - wb)
        s2 = s2 * (1 - wt * 0.92)
        h2 = h
        s2 = s2 * (1 - wb * 0.85)
        v2 = v2 * (1 - wb) + np.clip(v2 * 1.1, 0, 1) * wb
        out = hsv2rgb(h2, s2, v2)
    out = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    out.putalpha(Image.fromarray(alpha))
    return out


def recolor_images(svg, kind):
    def rep(m):
        fmt, b = m.group(1), m.group(2)
        im = Image.open(io.BytesIO(base64.b64decode(b)))
        k = kind(im) if callable(kind) else kind
        out = process_image(im, k)
        buf = io.BytesIO()
        if fmt == "jpeg":
            out.convert("RGB").save(buf, "JPEG", quality=92)
        else:
            out.save(buf, "PNG")
        return f'href="data:image/{fmt};base64,{base64.b64encode(buf.getvalue()).decode()}"'
    return re.sub(r'href="data:image/(\w+);base64,([^"]*)"', rep, svg)


def remap(svg, mapping):
    for k, v in mapping.items():
        svg = re.sub(re.escape(k), v, svg, flags=re.I)
    return svg


AXES_RGB = {"#D62728": "#D62728", "#2CA02C": "#2CA02C", "#1F77B4": "#1F77B4"}
AXES_MONO = {"#D62728": INK, "#2CA02C": INK, "#1F77B4": INK}


def do_fig1(src, dst, axes):
    s = open(src).read()
    cut = s.find('<g id="B_Native_Chart"')
    A, B = s[:cut], s[cut:]
    A = remap(A, {"#2859A3": FLOW, "#214B8A": FLOW_DK, "#A92466": T, "#912054": T_DK,
                  "#B85A88": T_LT, "#253436": INK, **axes})
    A = recolor_images(A, "photo")
    B = remap(B, {"#2859A3": G["g55"], "#75538E": "#2E2E2E", "#947035": G["g35"], "#A92466": T,
                  "#912054": T_DK, "#B85A88": G["g45"], "#000000": INK, "#E6EBED": G["g08"],
                  "#84939A": G["g45"]})
    open(dst, "w").write(A + B)


def do_paradigms(src, dst, axes):
    s = open(src).read()
    s = remap(s, {"#2859A3": FLOW, "#214B8A": FLOW_DK, "#A92466": T, "#912054": T_DK,
                  "#C4262E": G["g45"], "#A9AFB5": G["g25"], **axes})
    s = recolor_images(s, "render")
    open(dst, "w").write(s)


def do_otb(src, dst):
    s = open(src).read()
    m = {"#2859A3": T, "#7191BF": T_LT, "#87A6D0": T_LT, "#5277AE": T,
         "#596873": G["g70"], "#1F2328": INK, "#263441": INK,
         "#244574": INK, "#215852": INK, "#564171": INK, "#B25244": INK, "#6D4916": INK, "#823D37": INK,
         "#EDF2FA": "#FFFFFF", "#EDF6F4": "#FFFFFF", "#F3EFF8": "#FFFFFF", "#FAEEEA": "#FFFFFF",
         "#FBF4E6": "#FFFFFF", "#F4F5F5": "#FFFFFF",
         "#B9CAE5": G["g15"], "#B7D6CF": G["g15"], "#D4C7E4": G["g15"], "#E7C4BD": G["g15"],
         "#E7D2A6": G["g15"], "#CFD4D8": G["g15"],
         "#829FD3": G["g55"], "#DDB05E": G["g35"], "#76ADA8": G["g25"], "#A993C8": G["g15"], "#DC9085": G["g08"],
         "#FAE9EB": "#FFFFFF", "#E7F3EB": "#FFFFFF", "#AE2632": G["g45"], "#176541": T}
    s = remap(s, m)
    s = recolor_images(s, lambda im: "panel" if im.size == (428, 372) else "render")
    open(dst, "w").write(s)


if __name__ == "__main__":
    do_fig1("fig1.svg", "fig1_v2.svg", AXES_RGB)
    do_paradigms("paradigms.svg", "paradigms_v2_rgbaxes.svg", AXES_RGB)
    do_paradigms("paradigms.svg", "paradigms_v2_monoaxes.svg", AXES_MONO)
    do_otb("ontimebench.svg", "ontimebench_v2.svg")
