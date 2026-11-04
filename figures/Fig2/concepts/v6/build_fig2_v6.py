"""Fig. 2 concept v6: FoveaWAM architecture, (a) training view, (b) mask, (c) inference.

One scene description produces native-text SVG and vector PDF, as in
../../build_fig2.py. The RGB-D thumbnails are a recorded simulator observation
(t1_belt teacher data, agentview RGB and metric depth of the same frame); every
other drawing is a schematic, not a model output. Run from the repository root:
  python figures/Fig2/concepts/v6/build_fig2_v6.py
"""
from pathlib import Path
from math import atan2, cos, sin
from html import escape
import base64
import json
import os

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

OUT = Path(__file__).resolve().parent
NAME = 'fig2_concept_v6'
W, H = 1500, 650
WIDTH_PT = 6.875 * 72  # CVPR double-column text width.
SCALE = WIDTH_PT / W
FONT_DIR = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
FONTS = {'r': 'FigArial', 'b': 'FigArialBold', 'i': 'FigArialItalic'}
for key, file in [('r', 'arial.ttf'), ('b', 'arialbd.ttf'), ('i', 'ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(FONTS[key], str(FONT_DIR / file)))

# Palette shared with Fig. 1 v5.2: target teal, world/context ochre, action purple.
C = dict(ink='#283340', muted='#687580', faint='#E5EAED', line='#8D99A3',
         target='#358C8A', target_fill='#CCE5DF', target_pale='#EAF4F0',
         world='#AD7A36', world_fill='#FCF6EA', world_mid='#E9CC93', patch='#F3E4C8',
         world_edge='#CCB17C', robot='#8B9CA7', robot_fill='#DDE3E7',
         act='#8266A7', act_fill='#F3EFF8', act_mid='#CFBFE4', act_edge='#B8A4CE',
         panel='#F7F9FA', panel_edge='#B8C3CA', attn='#EAF0F3', attn_edge='#A5B5C0',
         white='#FFFFFF')

svg, texts, groups = [], [], []
pdf = canvas.Canvas(str(OUT / f'{NAME}.pdf'), pagesize=(WIDTH_PT, H * SCALE), pageCompression=1)
pdf.setTitle('FoveaWAM - Fig. 2 method architecture (concept v6)')
pdf.setAuthor('')
pdf.scale(SCALE, SCALE)
_rich_id = [0]


def group(name):
    svg.append(f'<g id="{escape(name)}">')
    groups.append(name)


def end():
    svg.append('</g>')
    groups.pop()


def paint(fill=None, stroke=None, sw=2, dash=None):
    if fill: pdf.setFillColor(HexColor(fill))
    if stroke: pdf.setStrokeColor(HexColor(stroke))
    pdf.setLineWidth(sw)
    pdf.setDash(dash or [])


def attrs(fill=None, stroke=None, sw=2, dash=None):
    v = f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'
    if dash: v += ' stroke-dasharray="' + ' '.join(map(str, dash)) + '"'
    return v


def rect(x, y, w, h, fill=None, stroke=None, sw=2, r=0, dash=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {attrs(fill, stroke, sw, dash)}/>')
    paint(fill, stroke, sw, dash)
    if r: pdf.roundRect(x, H-y-h, w, h, r, stroke=int(bool(stroke)), fill=int(bool(fill)))
    else: pdf.rect(x, H-y-h, w, h, stroke=int(bool(stroke)), fill=int(bool(fill)))


def poly(points, fill=None, stroke=None, sw=2, close=False, dash=None):
    tag = 'polygon' if close else 'polyline'
    ps = ' '.join(f'{x:.3f},{y:.3f}' for x, y in points)
    svg.append(f'<{tag} points="{ps}" {attrs(fill, stroke, sw, dash)} stroke-linejoin="round" stroke-linecap="round"/>')
    paint(fill, stroke, sw, dash)
    p = pdf.beginPath(); p.moveTo(points[0][0], H-points[0][1])
    for x, y in points[1:]: p.lineTo(x, H-y)
    if close: p.close()
    pdf.setLineJoin(1); pdf.setLineCap(1)
    pdf.drawPath(p, stroke=int(bool(stroke)), fill=int(bool(fill)))


def arrow(points, color=None, sw=2.4, dash=None, head=9):
    color = color or C['ink']
    x, y = points[-1]; px, py = points[-2]; ang = atan2(y-py, x-px)
    # Stop the shaft inside the head so dashed shafts do not poke through it.
    shaft = points[:-1] + [(x - head*.6*cos(ang), y - head*.6*sin(ang))]
    poly(shaft, stroke=color, sw=sw, dash=dash)
    poly([(x, y), (x-head*cos(ang)+head*.45*sin(ang), y-head*sin(ang)-head*.45*cos(ang)),
          (x-head*cos(ang)-head*.45*sin(ang), y-head*sin(ang)+head*.45*cos(ang))],
         fill=color, close=True)


def circle(x, y, r, fill=None, stroke=None, sw=2):
    svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" {attrs(fill, stroke, sw)}/>')
    paint(fill, stroke, sw)
    pdf.circle(x, H-y, r, stroke=int(bool(stroke)), fill=int(bool(fill)))


def image(x, y, w, h, path, stroke=None):
    data = base64.b64encode(Path(path).read_bytes()).decode('ascii')
    svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none" '
               f'href="data:image/png;base64,{data}"/>')
    pdf.drawImage(str(path), x, H-y-h, w, h)
    if stroke: rect(x, y, w, h, None, stroke, 1.4)


def _check(font, t):
    missing = [ch for ch in t if ord(ch) not in pdfmetrics.getFont(font).face.charToGlyph]
    if missing: raise ValueError(f'Font lacks glyphs {missing} in {t!r}')


def rich(x, y, segs, size=22, color=None, anchor='start'):
    """Native text spans. A segment is (text, kind[, color]); kind is r/b/i or s/si (subscript)."""
    _rich_id[0] += 1
    parts = []
    for seg in segs:
        t, kind = seg[0], seg[1]
        col = seg[2] if len(seg) > 2 else (color or C['ink'])
        sub = kind.startswith('s')
        style = 'i' if kind in ('i', 'si') else 'b' if kind == 'b' else 'r'
        fs = size * .7 if sub else size
        font = FONTS[style]; _check(font, t)
        parts.append((t, font, style, fs, col, size * .22 if sub else 0, pdfmetrics.stringWidth(t, font, fs)))
    width = sum(p[-1] for p in parts)
    cursor = x if anchor == 'start' else x - width if anchor == 'end' else x - width/2
    for t, font, style, fs, col, dy, pw in parts:
        texts.append(dict(text=t, x=cursor, y=y+dy-fs*.75, width=pw, height=fs*.95,
                          group='/'.join(groups), rid=_rich_id[0]))
        weight = 700 if style == 'b' else 400
        italic = ' font-style="italic"' if style == 'i' else ''
        svg.append(f'<text x="{cursor:.2f}" y="{y+dy:.2f}" font-family="Arial, Helvetica, sans-serif" '
                   f'font-size="{fs:.2f}" font-weight="{weight}"{italic} fill="{col}">{escape(t)}</text>')
        pdf.setFillColor(HexColor(col)); pdf.setFont(font, fs)
        pdf.drawString(cursor, H-(y+dy), t)
        cursor += pw
    return width


def text(x, y, t, size=22, color=None, bold=False, anchor='start', italic=False):
    return rich(x, y, [(t, 'b' if bold else 'i' if italic else 'r')], size, color, anchor)


def vtext(x, y, t, size=19, color=None):
    """Text rotated by 90 degrees, centred on (x, y)."""
    color = color or C['muted']; _check(FONTS['r'], t)
    svg.append(f'<text x="{x}" y="{y}" transform="rotate(-90 {x} {y})" text-anchor="middle" '
               f'font-family="Arial, Helvetica, sans-serif" font-size="{size}" fill="{color}">{escape(t)}</text>')
    pdf.saveState(); pdf.translate(x, H-y); pdf.rotate(90)
    pdf.setFillColor(HexColor(color)); pdf.setFont(FONTS['r'], size)
    pdf.drawCentredString(0, 0, t); pdf.restoreState()


def tokenrow(x, y, n, w=22, h=26, gap=6, fill=None, stroke=None, dot=None):
    for i in range(n):
        rect(x+i*(w+gap), y, w, h, fill, stroke, 1.3, r=3)
        if dot: circle(x+i*(w+gap)+w/2, y+h/2, 3.2, dot)
    return x + n*(w+gap) - gap


def bracket(x0, x1, y, color=None):
    poly([(x0, y-6), (x0, y), (x1, y), (x1, y-6)], stroke=color or C['line'], sw=1.4)


def head(xc, y, label, color, fill, edge, w=176, dash=None):
    poly([(xc-w/2+12, y+24), (xc+w/2-12, y+24), (xc+w/2, y), (xc-w/2, y)], fill, edge, 1.5, True, dash)
    text(xc, y+18, label, 19, color, anchor='middle')


def cube(x, y, s=28, col=None, angle=0, fills=None, dash=None):
    col = col or C['target']
    f1, f2, f3 = fills or ('#D9E9E3', '#B5D7CC', '#ECF5F0')
    a = (s*cos(angle), s*sin(angle)); b = (s*.62*cos(angle-2.15), s*.62*sin(angle-2.15)); c = (0, -s*.84)
    pt = lambda i, j, k: (x+i*a[0]+j*b[0]+k*c[0], y+i*a[1]+j*b[1]+k*c[1])
    poly([pt(0, 0, 0), pt(1, 0, 0), pt(1, 0, 1), pt(0, 0, 1)], f1, col, 1.4, True, dash)
    poly([pt(0, 0, 0), pt(0, 1, 0), pt(0, 1, 1), pt(0, 0, 1)], f2, col, 1.4, True, dash)
    poly([pt(0, 0, 1), pt(1, 0, 1), pt(1, 1, 1), pt(0, 1, 1)], f3, col, 1.4, True, dash)


def triad(x, y, s=22, color=None, angle=0):
    color = color or C['target']
    for a, l in [(angle, 1), (angle-1.5708, .85), (angle+2.45, .62)]:
        arrow([(x, y), (x+s*l*cos(a), y+s*l*sin(a))], color, 1.7, head=5)
    circle(x, y, 2.2, color)


def grip(x, y, s=1, col=None):
    col = col or C['act']
    poly([(x-17*s, y-10*s), (x+17*s, y-10*s)], stroke=col, sw=3*s)
    poly([(x-15*s, y-10*s), (x-15*s, y+12*s), (x-7*s, y+17*s)], stroke=col, sw=3*s)
    poly([(x+15*s, y-10*s), (x+15*s, y+12*s), (x+7*s, y+17*s)], stroke=col, sw=3*s)
    poly([(x, y-27*s), (x, y-10*s)], stroke=col, sw=4*s)


# Column centres of (a): scene-flow readout over the patches, target readout over M,
# action readout over A, so each readout sits directly above the tokens it reads.
XF, XM, XA = 225, 735, 955
rect(0, 0, W, H, C['white'])

# ---------------------------------------------------------------- (a) readouts
group('a-title')
rich(14, 31, [('(a) ', 'b'), ('FoveaWAM', 'b'), ('  ·  training', 'r', C['muted'])], 27)
end()

group('a-training-only-readouts')
rect(30, 50, 836, 218, None, C['line'], 1.5, r=10, dash=[7, 5])
label = 'Role-aware 4D supervision · training only'
lw = pdfmetrics.stringWidth(label, FONTS['b'], 20)
rect(453 - lw/2 - 10, 38, lw + 20, 24, C['white'])
text(453, 57, label, 20, C['muted'], True, 'middle')

# Sparse scene flow: a patch-point plane; target and gripper points move, the rest is static.
text(XF, 90, 'Sparse 3D scene flow', 23, C['world'], True, 'middle')
pts = {}
for r in range(4):
    for c in range(10):
        pts[r, c] = (98 + c*24 + r*15, 182 - r*13 - c*2.4)
for r in range(4): poly([pts[r, c] for c in range(10)], stroke='#EDE3D2', sw=1)
for c in range(10): poly([pts[r, c] for r in range(4)], stroke='#EDE3D2', sw=1)
moving_target = {(0, 5), (0, 6), (1, 5), (1, 6), (2, 6)}
moving_robot = {(2, 2), (3, 2), (3, 3), (2, 3)}
occluded = {(2, 7), (3, 7)}
for (r, c), (x, y) in pts.items():
    if (r, c) in occluded:
        circle(x, y, 2.6, C['white'], '#C9B38A', 1.2)
    elif (r, c) not in moving_target | moving_robot:
        circle(x, y, 2.1, '#D2BF9C')
cube(238, 166, 24, C['target'], -.1)
grip(165, 128, .62, C['robot'])
for (r, c) in sorted(moving_target):
    x, y = pts[r, c]; circle(x, y-14, 2.4, C['world'])
    arrow([(x, y-14), (x+21, y-18)], C['world'], 1.9, head=6)
for (r, c) in sorted(moving_robot):
    x, y = pts[r, c]; circle(x, y-6, 2.4, C['world'])
    arrow([(x, y-6), (x+13, y-15)], C['world'], 1.9, head=6)
text(XF, 207, '196 patch points × 8 horizons', 20, C['muted'], anchor='middle')
text(XF, 230, '3D displacement + visibility', 20, C['muted'], anchor='middle')
head(XF, 240, 'Linear · per patch', C['world'], C['world_fill'], C['world_edge'])
rich(XF+100, 258, [('L', 'i'), ('F', 'si')], 23, C['world'])

# Target SE(3): one rigid body moves and rotates along the forecast horizons.
text(XM, 90, 'Target SE(3) trajectory', 23, C['target'], True, 'middle')
traj = [(636, 182), (697, 171), (758, 159), (818, 140)]
poly(traj, stroke='#B7D6CC', sw=2, dash=[5, 4])
for i, (x, y) in enumerate(traj):
    cube(x, y, 21, C['target'], -.1 - i*.2)
    triad(x - 4, y + 4, 19, C['target'], -.1 - i*.2)
rich(XM, 207, [('(', 'r'), ('d', 'i'), ('h', 'si'), (', ', 'r'), ('φ', 'i'), ('h', 'si'),
               (')  ·  ', 'r'), ('h', 'i'), (' = 1…8', 'r')], 20, C['muted'], 'middle')
text(XM, 230, '50–400 ms after capture', 20, C['muted'], anchor='middle')
head(XM, 240, 'Linear · mean(M)', C['target'], C['target_pale'], '#77AEA0')
rich(XM+100, 258, [('L', 'i'), ('P', 'si')], 23, C['target'])
end()

group('a-action-readout')
text(XA, 90, 'Action chunk', 23, C['act'], True, 'middle')
path = [(885 + i*20, 176 - 30*sin(i*.24)) for i in range(8)]
poly(path, stroke=C['act_mid'], sw=2.2)
for i, (x, y) in enumerate(path):
    circle(x, y, 3.4, C['act'])
    if i in (0, 4, 7): grip(x, y - 10, .55, C['act'])
rich(XA, 207, [('a', 'i'), ('j', 'si'), (' at ', 'r'), ('τ', 'i'), (' + ', 'r'), ('j', 'i'), ('Δ', 'r'),
               ('a', 'si')], 20, C['muted'], 'middle')
rich(XA, 230, [('j', 'i'), (' = 0…7', 'r')], 20, C['muted'], 'middle')
head(XA, 240, 'Velocity head', C['act'], C['act_fill'], C['act_edge'], w=150)
rich(XA+82, 258, [('L', 'i'), ('A', 'si')], 23, C['act'])
end()

# ---------------------------------------------------------------- (a) backbone
group('a-backbone')
rect(38, 279, 1015, 124, C['white'], '#D5DCE1', 1.3, r=9)
rect(30, 286, 1015, 124, C['panel'], C['panel_edge'], 1.6, r=9)
text(1053, 357, '×24', 25, C['muted'], True)
rect(45, 299, 812, 44, C['world_fill'], C['world_edge'], 1.5, r=6)
text(451, 330, 'World FFN', 24, C['world'], True, 'middle')
rect(870, 299, 160, 44, C['act_fill'], C['act_edge'], 1.5, r=6)
text(950, 330, 'Action FFN', 24, C['act'], True, 'middle')
rect(45, 357, 985, 40, C['attn'], C['attn_edge'], 1.5, r=6)
rich(537, 384, [('Masked self-attention', 'b'), ('  ·  shared Q, K, V, O over both streams', 'r', C['muted'])],
     22, C['ink'], 'middle')
for x, col in [(XF, C['world']), (XM, C['world']), (XA, C['act'])]:
    arrow([(x, 357), (x, 345)], col, 1.8, head=6)
# Readouts: dashed = training only, solid = used at inference.
arrow([(XF, 279), (XF, 266)], C['world'], 2.2, [5, 4], 8)
arrow([(XM, 279), (XM, 266)], C['target'], 2.2, [5, 4], 8)
arrow([(XA, 279), (XA, 266)], C['act'], 2.4, None, 8)
for x, col in [(227, C['world']), (469, C['target']), (569, C['robot']), (XM, C['world']), (XA, C['act'])]:
    arrow([(x, 433), (x, 413)], col, 2.2, head=8)
end()

# ---------------------------------------------------------------- (a) tokens
group('a-tokens')
TY = 434
end_p = tokenrow(45, TY, 10, 24, 26, 6, C['patch'], C['world'])
text(end_p + 8, TY + 20, '…', 22, C['world'])
tokenrow(386, TY, 1, 24, 26, 6, C['patch'], C['world'])
tokenrow(430, TY, 3, 22, 26, 6, C['target_fill'], C['target'])
tokenrow(530, TY, 3, 22, 26, 6, C['robot_fill'], C['robot'])
tokenrow(652, TY, 6, 22, 26, 6, C['white'], C['world'], dot=C['world_mid'])
tokenrow(877, TY, 8, 16, 26, 4, C['act_mid'], C['act'])
bracket(40, 612, 472); bracket(648, 822, 472); bracket(873, 1037, 472)
rich(40, 496, [('Scene S', 'b'), (' · 212 tokens', 'r', C['muted'])], 21, C['ink'])
rich(648, 496, [('Summary M', 'b', C['world']), (' · 16', 'r', C['muted'])], 21)
rich(873, 496, [('Action A', 'b', C['act']), (' · 8', 'r', C['muted'])], 21)
end()

# ---------------------------------------------------------------- (a) inputs
group('a-inputs')
image(40, 514, 82, 82, OUT / 'assets' / 'rgb.png', '#B8C3CA')
image(128, 514, 82, 82, OUT / 'assets' / 'depth.png', '#B8C3CA')
text(81, 616, 'RGB', 19, C['muted'], anchor='middle')
text(169, 616, 'Depth', 19, C['muted'], anchor='middle')
text(125, 640, 'Current RGB-D only', 20, C['ink'], True, 'middle')
arrow([(212, 555), (232, 555)], C['line'], 2, head=7)
rect(236, 514, 176, 82, C['white'], C['panel_edge'], 1.5, r=6)
text(324, 545, 'Frozen MAE', 21, C['ink'], True, 'middle')
text(324, 571, '+ XYZ · 3D RoPE', 19, C['muted'], anchor='middle')
text(324, 616, '14 × 14 patches', 19, C['muted'], anchor='middle')
hist = [(440, 578), (462, 571), (484, 565), (505, 553)]
poly(hist, stroke='#A1C9C0', sw=1.8)
for i, (x, y) in enumerate(hist): triad(x, y, 17, C['target'], -.25 + i*.15)
text(469, 616, 'Target SE(3)', 19, C['target'], True, 'middle')
text(469, 640, '8-step history', 19, C['muted'], anchor='middle')
for i, (x, y) in enumerate([(548, 584), (574, 574), (600, 562)]):
    grip(x, y, .5, ['#B3BDC4', '#9AA8B1', '#7F8E99'][i])
text(575, 616, 'Robot', 19, C['robot'], True, 'middle')
text(575, 640, '8 states', 19, C['muted'], anchor='middle')
rich(XA, 546, [('Noisy chunk ', 'r'), ('a', 'i'), ('u', 'si')], 20, C['act'], 'middle')
rich(XA, 572, [('flow time ', 'r'), ('u', 'i'), (' → AdaLN', 'r')], 19, C['muted'], 'middle')
rich(852, 630, [('L', 'i'), (' = ', 'r'), ('L', 'i'), ('A', 'si'), (' + ', 'r'), ('λ', 'i'), ('F', 'si'),
                ('L', 'i'), ('F', 'si'), (' + ', 'r'), ('λ', 'i'), ('P', 'si'), ('L', 'i'), ('P', 'si'),
                (' + ', 'r'), ('λ', 'i'), ('aux', 's'), ('L', 'i'), ('aux', 's')], 21, C['muted'], 'middle')
end()

poly([(1100, 14), (1100, 640)], stroke=C['faint'], sw=1.6)

# ---------------------------------------------------------------- (b) mask
group('b-attention-mask')
rich(1120, 31, [('(b) ', 'b'), ('Attention mask', 'b')], 27)
mx, my, cs = 1238, 96, 50
text(mx + 1.5*cs, 66, 'keys', 19, C['muted'], anchor='middle')
vtext(1180, my + 1.5*cs, 'queries')
names = [('S', C['ink']), ('M', C['world']), ('A', C['act'])]
for i, (l, col) in enumerate(names):
    text(mx + i*cs + cs/2, my - 9, l, 22, col, True, 'middle')
    text(mx - 12, my + i*cs + 33, l, 22, col, True, 'end')
allowed = {(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)}
for r in range(3):
    for c in range(3):
        fill = (C['world_mid'] if r < 2 else C['act_mid']) if (r, c) in allowed else C['white']
        rect(mx + c*cs, my + r*cs, cs, cs, fill, '#ACBAC4', 1.2)
text(1305, 276, 'The world stream never reads A or u', 19, C['muted'], anchor='middle')
text(1305, 300, 'A reads S and M in every layer', 19, C['muted'], anchor='middle')
end()

# ---------------------------------------------------------------- (c) inference
group('c-cached-inference')
rich(1120, 352, [('(c) ', 'b'), ('Cached inference', 'b')], 27)
rect(1140, 370, 330, 42, C['world_fill'], C['world_edge'], 1.5, r=6)
rich(1305, 398, [('World stream', 'b', C['world']), ('  ·  once per query', 'r', C['muted'])], 21, anchor='middle')
arrow([(1305, 412), (1305, 432)], C['line'], 2, head=7)
rect(1180, 434, 250, 32, C['white'], C['line'], 1.4, r=5, dash=[4, 3])
rich(1305, 456, [('Cache ', 'b'), ('K', 'i'), (', ', 'r'), ('V', 'i'), (' of S and M', 'r')], 19, C['ink'], 'middle')
arrow([(1305, 466), (1305, 486)], C['act'], 2, head=7)
rect(1140, 488, 290, 42, C['act_fill'], C['act_edge'], 1.5, r=6)
rich(1285, 516, [('Action stream', 'b', C['act']), ('  ·  reads cache', 'r', C['muted'])], 21, anchor='middle')
arrow([(1430, 519), (1456, 519), (1456, 499), (1432, 499)], C['act'], 1.9, head=7)
text(1462, 515, '×5', 20, C['act'], True)
arrow([(1285, 530), (1285, 548)], C['act'], 2, head=7)
tokenrow(1176, 550, 8, 22, 22, 6, C['act_mid'], C['act'])
rich(1305, 596, [('a', 'i'), ('0', 's'), ('…', 'r'), ('a', 'i'), ('7', 's'), (' indexed from capture ', 'r'),
                 ('τ', 'i')], 19, C['muted'], 'middle')
head(1172, 612, '', C['muted'], C['white'], C['line'], w=52, dash=[4, 3])
poly([(1150, 638), (1194, 610)], stroke=C['line'], sw=1.6)
text(1210, 630, 'Forecast heads skipped', 19, C['muted'])
end()

assert not groups
pdf.showPage(); pdf.save()

description = ('FoveaWAM method architecture (concept v6). (a) Training view: current RGB-D patches with '
               'XYZ and 3D RoPE, target SE(3) history and robot history form scene tokens S; 16 learned summary '
               'tokens M and 8 noisy action tokens A share masked self-attention with separate world and action '
               'FFNs over 24 layers. Training-only linear heads read sparse 3D scene flow from patch states and the '
               'target SE(3) trajectory from mean(M); a velocity head reads A. (b) Attention mask S->S, M->S,M, '
               'A->S,M,A. (c) Inference: the world stream runs once, its keys and values are cached, and the action '
               'stream integrates 5 Euler steps; forecast heads are skipped.')
document = (f'<svg xmlns="http://www.w3.org/2000/svg" width="174.625mm" height="{H/W*174.625:.6f}mm" '
            f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">\n'
            '<title id="title">FoveaWAM Fig. 2 concept v6</title>\n'
            f'<desc id="desc">{escape(description)}</desc>\n' + '\n'.join(svg) + '\n</svg>\n')
(OUT / f'{NAME}.svg').write_text(document, encoding='utf-8')

# Layout checks: every text box inside the canvas and no two text runs overlapping.
outside = [t for t in texts if t['x'] < 0 or t['x']+t['width'] > W or t['y'] < 0 or t['y']+t['height'] > H]
overlaps = []
for i, a in enumerate(texts):
    for b in texts[i+1:]:
        if a['rid'] == b['rid'] or not a['text'].strip() or not b['text'].strip(): continue
        if (a['x'] < b['x']+b['width'] and b['x'] < a['x']+a['width'] and
                a['y'] < b['y']+b['height'] and b['y'] < a['y']+a['height']):
            overlaps.append((a['text'], b['text']))
report = dict(pdf=str(OUT / f'{NAME}.pdf'), width_mm=174.625, height_mm=round(H/W*174.625, 2),
              text_objects=len(texts), minimum_text_pt=round(min(t['height']/.95 for t in texts if t['text'].strip()
                                                              and t['height'] > 15) * SCALE, 2),
              outside=[t['text'] for t in outside], overlaps=overlaps)
(OUT / 'layout_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=False))
