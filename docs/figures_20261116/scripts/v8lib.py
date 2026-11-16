import re, io, base64, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import recolor_svg as R
RED, BLUE, GREEN, AMBER, PURPLE = "#C0263A", "#2859A3", "#2E8540", "#E69F00", "#9467BD"
BLUE_L = "#7191BF"
F = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 38)

def proc(im, gsat, grey_tables, panel):
    rgba = im.convert("RGBA"); alpha = np.asarray(rgba)[..., 3]
    a = np.asarray(rgba.convert("RGB")).astype(float) / 255
    h, s, v = R.rgb2hsv(a)
    wg = R.win(h, 80, 170) * np.clip((s - 0.15) / 0.12, 0, 1)
    s2 = s * (1 - wg * gsat)
    slate = (R.win(h, 195, 235) * ((s > 0.12) & (s < 0.5) & (v < 0.7))).mean()
    if grey_tables and (panel or slate > 0.12):
        ghost = 0 if panel else R.win(h, 200, 235) * np.clip((s - 0.36) / 0.06, 0, 1) * np.clip((v - 0.48) / 0.06, 0, 1)
        wt = R.win(h, 195, 235) * np.clip((s - 0.1) / 0.06, 0, 1) * (1 - ghost)
        s2 = s2 * (1 - wt * 0.9)
    out = R.hsv2rgb(h, s2, v)
    out = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA"); out.putalpha(Image.fromarray(alpha))
    return out

def build(out, gsat=0.0, grey_tables=False, impact=RED, adv=GREEN, dpi=300, striker="#1A1A1A"):
    s = open("ontimebench.svg").read()
    idx = [m.start() for m in re.finditer("#176541", s)]
    for i in reversed(idx[:2]):
        s = s[:i] + BLUE + s[i + 7:]
    fam = (BLUE, GREEN, PURPLE, AMBER, impact)
    mp = {"#176541": adv, "#AE2632": RED, "#2859A3": BLUE, "#7191BF": BLUE_L, "#87A6D0": BLUE_L, "#5277AE": BLUE, "#596873": BLUE,
          "#1F2328": "#1A1A1A", "#263441": striker,
          "#244574": "#1A1A1A", "#215852": "#1A1A1A", "#564171": "#1A1A1A", "#B25244": striker, "#6D4916": "#1A1A1A", "#823D37": "#1A1A1A",
          "#EDF2FA": "#FFFFFF", "#EDF6F4": "#FFFFFF", "#F3EFF8": "#FFFFFF", "#FAEEEA": "#FFFFFF", "#FBF4E6": "#FFFFFF", "#F4F5F5": "#FFFFFF",
          "#B9CAE5": fam[0], "#B7D6CF": fam[1], "#D4C7E4": fam[2], "#E7D2A6": fam[3], "#E7C4BD": fam[4], "#CFD4D8": "#D6D6D6",
          "#829FD3": fam[0], "#76ADA8": fam[1], "#A993C8": fam[2], "#DDB05E": fam[3], "#DC9085": fam[4],
          "#FAE9EB": "#FFFFFF", "#E7F3EB": "#FFFFFF"}
    s = R.remap(s, mp)
    if gsat or grey_tables:
        def rep(m):
            fmt, b = m.group(1), m.group(2)
            im = Image.open(io.BytesIO(base64.b64decode(b)))
            o = proc(im, gsat, grey_tables, im.size == (428, 372))
            buf = io.BytesIO(); o.save(buf, "PNG")
            return f'href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"'
        s = re.sub(r'href="data:image/(\w+);base64,([^"]*)"', rep, s)
    open(out + ".svg", "w").write(s)
    subprocess.run(["rsvg-convert", "-d", str(dpi), "-p", str(dpi), out + ".svg", "-o", out + ".png"], check=True)
    return Image.open(out + ".png").convert("RGB")

def grid(items, out, ncol):
    w = max(i.width for _, i in items); h = max(i.height for _, i in items)
    nrow = (len(items) + ncol - 1) // ncol
    can = Image.new("RGB", (ncol * (w + 40), nrow * (h + 70)), "white"); d = ImageDraw.Draw(can)
    for k, (t, im) in enumerate(items):
        x, y = (k % ncol) * (w + 40), (k // ncol) * (h + 70)
        d.text((x, y + 10), t, font=F, fill=(25, 25, 25)); can.paste(im, (x, y + 65))
    can.save(out)

