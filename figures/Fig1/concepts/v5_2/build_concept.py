"""Fig. 1 design concept v5.2: a layout study for the redesigned teaser, not a paper asset.

Scene graphics are vector schematics (no recording, label or model output). Panel (c) plots the
Table 1 baselines exactly as ../../build_fig1.py parses them, plus the placeholder FoveaWAM point in
../../data/ours.json. Colors follow Fig. 2 (target teal, scene flow amber, action purple) and the
latency figure (ours as a crimson star).

    ../../../../.venv/Scripts/python.exe build_concept.py

Writes fig1_concept_v52.pdf / .svg / .png (600 dpi) and layout_report.json.
"""
from pathlib import Path
import json
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))
from build_fig1 import FAMILY, table_rows  # noqa: E402  (same Table 1 parser as the current figure)

W, H = 6.875, 2.75
FS, TFS = 7, 8.5
C = dict(ink='#283340', muted='#687580', line='#8D99A3', faint='#DDE3E7', floor='#E2E7EA',
         disk='#D3DADE', disk_side='#B6C0C6', target='#358C8A', target_top='#E3F1EC',
         target_left='#B5D7CC', target_right='#CCE5DF', world='#AD7A36', world_fill='#FCF6EA',
         act='#8266A7', act_fill='#F3EFF8', ours='#B53058', base='#9AA4AB')
COL_A, COL_B, COL_C = 0.0, 1.42, 5.24     # left edges of panels (a), (b), (c), inches
B_RIGHT = 5.05


# ---------------------------------------------------------------- primitives (inch coordinates)
def box(ax, x, y, w, h, fc='white', ec=C['line'], lw=0.6, r=0.04, ls='-', z=1.0, alpha=1.0):
    patch = FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}', fc=fc, ec=ec,
                           lw=lw, ls=ls, zorder=z, alpha=alpha)
    ax.add_patch(patch)
    return patch


def arrow(ax, p, q, color=C['muted'], lw=0.7, ls='-', z=3.0, rad=0.0, head=1.0, alpha=1.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=f'-|>,head_length={2.4 * head},head_width={1.4 * head}',
                                 color=color, lw=lw, ls=ls, zorder=z, shrinkA=0, shrinkB=0, alpha=alpha,
                                 connectionstyle=f'arc3,rad={rad}'))


def text(ax, x, y, s, size=FS, color=C['ink'], ha='left', va='center', weight='normal', z=8.0):
    return ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, fontweight=weight, zorder=z)


def iso(gx, gy, gz, s):
    """Ground-plane unit coordinates -> screen offset (inches) for a cube of edge s."""
    return np.array([0.50 * gx - 0.40 * gy, 0.22 * gx + 0.20 * gy + 0.56 * gz]) * s


def cube(ax, base, s, phi=0.0, solid=True, alpha=1.0, z=5.0, ls='-'):
    rot = np.array([[np.cos(phi), -np.sin(phi)], [np.sin(phi), np.cos(phi)]])

    def corner(a, b, c):
        g = rot @ np.array([a - 0.5, b - 0.5])
        return np.asarray(base) + iso(g[0], g[1], c, s)

    if solid:  # phi = 0 view: top and the two front faces are visible
        for face, fc in (([(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)], C['target_left']),
                         ([(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], C['target_right']),
                         ([(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], C['target_top'])):
            ax.add_patch(Polygon([corner(*v) for v in face], closed=True, fc=fc, ec=C['target'], lw=0.7,
                                 alpha=alpha, zorder=z, joinstyle='round'))
    else:
        verts = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
        for i, u in enumerate(verts):
            for v in verts[i + 1:]:
                if sum(p != q for p, q in zip(u, v)) == 1:
                    ax.plot(*zip(corner(*u), corner(*v)), color=C['target'], lw=0.65, alpha=alpha, ls=ls,
                            zorder=z, solid_capstyle='round')
    return corner(0.5, 0.5, 0.5), corner(0.5, 0.5, 1.0)


def gripper(ax, x, tip_y, s, alpha=1.0, z=7.0, color=C['act']):
    w, fh, st = 0.62 * s, 0.55 * s, 0.55 * s
    ax.plot([x - w / 2, x - w / 2, x + w / 2, x + w / 2], [tip_y, tip_y + fh, tip_y + fh, tip_y],
            color=color, lw=1.4, alpha=alpha, zorder=z, solid_capstyle='round', solid_joinstyle='round')
    ax.plot([x, x], [tip_y + fh, tip_y + fh + st], color=color, lw=2.0, alpha=alpha, zorder=z,
            solid_capstyle='butt')
    ax.add_patch(Rectangle((x - 0.2 * s, tip_y + fh + st), 0.4 * s, 0.2 * s, fc=color, ec='none', alpha=alpha,
                           zorder=z))
    return np.array([x, tip_y + fh + st + 0.2 * s])


def mini_scene(ax, x, y, w, h, mode, theta, z=2.0):
    """Thumbnail of the same schematic scene: 'rgb', 'depth', or 'gray' (video-WAM pixels)."""
    pal = dict(rgb=dict(bg='#E7ECEF', disk='#CBD5DB', side='#AEBBC3', cube=C['target'], edge=C['line'], grip=C['act']),
               depth=dict(bg='#56626A', disk='#99A5AC', side='#7A868D', cube='#DCE2E5', edge='#4A555C', grip='#C5CCD1'),
               gray=dict(bg='#EEF0F1', disk='#D6DBDE', side='#C1C7CB', cube='#9FA8AE', edge='#B4BBC0', grip='#98A0A6'))[mode]
    clip = box(ax, x, y, w, h, fc=pal['bg'], ec=pal['edge'], lw=0.5, r=0.025, z=z)
    cx, cy = x + 0.5 * w, y + 0.33 * h
    t = np.deg2rad(theta)
    px, py = cx + 0.27 * w * np.cos(t), cy + 0.09 * h * np.sin(t)
    gx, gy = x + 0.64 * w, y + 0.60 * h
    artists = [Ellipse((cx, cy - 0.05 * h), 0.84 * w, 0.34 * h, fc=pal['side'], ec='none', zorder=z + 0.1),
               Ellipse((cx, cy), 0.84 * w, 0.34 * h, fc=pal['disk'], ec='none', zorder=z + 0.2),
               Rectangle((px - 0.06 * w, py), 0.12 * w, 0.15 * h, fc=pal['cube'], ec='none', zorder=z + 0.3)]
    for a in artists:
        ax.add_patch(a)
        a.set_clip_path(clip)
    lines = ax.plot([gx - 0.07 * w, gx - 0.07 * w, gx + 0.07 * w, gx + 0.07 * w],
                    [gy, gy + 0.13 * h, gy + 0.13 * h, gy], color=pal['grip'], lw=0.8, zorder=z + 0.4)
    lines += ax.plot([gx, gx], [gy + 0.13 * h, y + h], color=pal['grip'], lw=1.0, zorder=z + 0.4)
    for line in lines:
        line.set_clip_path(clip)


def title(ax, x, s, sub):
    text(ax, x, H - 0.03, s, size=TFS, weight='bold', va='top')
    text(ax, x, H - 0.215, sub, color=C['muted'], va='top')


# ---------------------------------------------------------------- (a) video WAMs
def panel_a(ax):
    title(ax, COL_A, '(a) Video WAMs', 'Forecast every pixel')
    for i, (dx, dy) in enumerate(((0.10, 0.08), (0.05, 0.04), (0.0, 0.0))):
        mini_scene(ax, COL_A + dx, 1.98 + dy, 0.46, 0.33, 'gray', theta=170 + 12 * i, z=2 + i)
    text(ax, COL_A + 0.28, 1.90, 'Frames', ha='center', color=C['muted'])
    arrow(ax, (COL_A + 0.58, 2.17), (COL_A + 0.67, 2.17))
    box(ax, COL_A + 0.69, 2.02, 0.56, 0.30, fc='#F1F3F4', ec=C['line'], r=0.05, z=2)
    text(ax, COL_A + 0.97, 2.17, 'WAM', weight='bold', ha='center')
    arrow(ax, (COL_A + 0.82, 2.02), (COL_A + 0.50, 1.62), rad=-0.15)
    arrow(ax, (COL_A + 1.10, 2.02), (COL_A + 1.10, 1.47))
    for i, (dx, dy) in enumerate(((0.12, 0.10), (0.06, 0.05), (0.0, 0.0))):
        mini_scene(ax, COL_A + dx, 1.04 + dy, 0.62, 0.44, 'gray', theta=205 + 30 * i, z=2 + i)
    for k in range(3):
        ax.add_patch(Rectangle((COL_A + 0.92 + 0.12 * k, 1.33), 0.09, 0.09, fc='#B9C0C5', ec='none', zorder=3))
    text(ax, COL_A + 1.10, 1.22, 'Actions', ha='center', color=C['muted'])
    text(ax, COL_A, 0.92, 'Future pixels', color=C['ink'])
    text(ax, COL_A, 0.74, 'Same fidelity for target,', color=C['muted'])
    text(ax, COL_A, 0.60, 'robot and background', color=C['muted'])


# ---------------------------------------------------------------- (b) FoveaWAM
def inputs_and_model(ax):
    title(ax, COL_B, '(b) FoveaWAM (ours)', 'Role-aware 4D geometry')
    y0, th = 2.05, 0.34
    mini_scene(ax, COL_B, y0, 0.46, th, 'rgb', theta=200)
    mini_scene(ax, COL_B + 0.50, y0, 0.46, th, 'depth', theta=200)
    text(ax, COL_B + 0.48, y0 - 0.075, 'One RGB-D frame', ha='center', color=C['muted'])
    hx = COL_B + 1.03
    box(ax, hx, y0, 0.62, th, fc='white', ec=C['line'], lw=0.5, r=0.025, z=2)
    for k in range(5):  # target SE(3) history: oldest faint, current solid
        phi = np.deg2rad(-60 + 15 * k)
        base = (hx + 0.08 + 0.115 * k, y0 + 0.08 + 0.05 * np.sin(np.pi * k / 4))
        cube(ax, base, 0.085, phi=phi, solid=(k == 4), alpha=0.35 + 0.16 * k, z=3)
    text(ax, hx + 0.31, y0 - 0.075, 'SE(3) history', ha='center', color=C['muted'])
    arrow(ax, (hx + 0.64, y0 + th / 2), (hx + 0.73, y0 + th / 2))

    mx, my, mw, mh = hx + 0.75, 1.93, 1.10, 0.52
    box(ax, mx, my, mw, mh, fc='#F7F9FA', ec=C['line'], lw=0.7, r=0.06, z=2)
    text(ax, mx + mw / 2, my + mh - 0.10, 'FoveaWAM', size=8, weight='bold', ha='center')
    box(ax, mx + 0.07, my + 0.07, 0.42, 0.20, fc=C['world_fill'], ec=C['world'], lw=0.6, r=0.03, z=3)
    text(ax, mx + 0.28, my + 0.17, 'World', ha='center', color=C['world'])
    box(ax, mx + 0.61, my + 0.07, 0.42, 0.20, fc=C['act_fill'], ec=C['act'], lw=0.6, r=0.03, z=3)
    text(ax, mx + 0.82, my + 0.17, 'Action', ha='center', color=C['act'])
    arrow(ax, (mx + 0.49, my + 0.17), (mx + 0.61, my + 0.17), color=C['ink'], lw=0.6)
    arrow(ax, (mx + mw + 0.02, my + mh / 2), (mx + mw + 0.10, my + mh / 2))
    tx = mx + mw + 0.13
    for dy, s, col in ((0.15, 'Target SE(3)', C['target']), (0.0, 'Scene flow', C['world']),
                       (-0.15, 'Action chunk', C['act'])):
        text(ax, tx, my + mh / 2 + dy, s, color=col)


def hero(ax, fig):
    x0, y0, w, h = COL_B, 0.47, B_RIGHT - COL_B, 1.36
    frame = box(ax, x0, y0, w, h, fc=C['floor'], ec=C['line'], lw=0.6, r=0.05, z=1)
    gx, gy = np.meshgrid(np.arange(x0 + 0.08, x0 + w - 0.04, 0.15), np.arange(y0 + 0.07, y0 + h - 0.04, 0.12))
    dots = ax.scatter(gx.ravel(), gy.ravel(), s=0.8, color='#A9B4BB', linewidths=0, zorder=1.2)
    dots.set_clip_path(frame)

    dcx, dcy, A, B, th = x0 + 1.66, y0 + 0.42, 1.40, 0.30, 0.06  # turntable (context body)
    ax.add_patch(Ellipse((dcx, dcy - th), 2 * A, 2 * B, fc=C['disk_side'], ec=C['line'], lw=0.5, zorder=2))
    ax.add_patch(Rectangle((dcx - A, dcy - th), 2 * A, th, fc=C['disk_side'], ec='none', zorder=2.05))
    ax.add_patch(Ellipse((dcx, dcy), 2 * A, 2 * B, fc=C['disk'], ec=C['line'], lw=0.5, zorder=2.1))

    # Fovea: everything outside the target's neighborhood is washed out (an edit, stated in INDEX.md).
    fx, fy, rx, ry = dcx - 0.25, dcy + 0.10, 1.25, 0.62
    xs, ys = np.linspace(x0, x0 + w, 400), np.linspace(y0, y0 + h, 160)
    X, Y = np.meshgrid(xs, ys)
    d = np.hypot((X - fx) / rx, (Y - fy) / ry)
    rgba = np.zeros(X.shape + (4,))
    rgba[..., :3] = 1.0
    rgba[..., 3] = np.clip((d - 0.75) / 0.6, 0, 1) * 0.8
    veil = ax.imshow(rgba, extent=(x0, x0 + w, y0, y0 + h), origin='lower', zorder=3.5, interpolation='bilinear')
    veil.set_clip_path(frame)
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect('auto')

    # Coarse scene flow on the turntable rim, drawn above the veil.
    ra, rb = 1.24, 0.255
    for deg in (28, 72, 116, 248, 292, 336):
        t = np.deg2rad(deg)
        p = np.array([dcx + ra * np.cos(t), dcy + rb * np.sin(t)])
        tan = np.array([-ra * np.sin(t), rb * np.cos(t)])
        q = p + 0.19 * tan / np.linalg.norm(tan)
        arrow(ax, tuple(p), tuple(q), color=C['world'], lw=1.0, z=4.5, head=1.1)

    # Target: capture tau (ghost), tau+L (solid, being grasped), forecasts to +400 ms.
    a, b, s = 0.98, 0.17, 0.25
    on = lambda deg: np.array([dcx + a * np.cos(np.deg2rad(deg)), dcy + b * np.sin(np.deg2rad(deg))])
    th_tau, step = 196.0, 14.0
    ghost_c, _ = cube(ax, on(th_tau) + [-0.04, 0], s, phi=np.deg2rad(-14), solid=False, alpha=0.5, ls=(0, (2, 1.5)), z=5)
    now_c, now_top = cube(ax, on(th_tau + step), s, solid=True, z=6)
    centers = [now_c] + [on(th_tau + step * k) + iso(0, 0, 0.5, s) for k in range(2, 9)]
    ax.plot(*np.array(centers).T, color=C['target'], lw=0.8, ls=(0, (1.5, 1.8)), zorder=4.8)
    ax.scatter(*np.array(centers[1:]).T, s=5, color=C['target'], edgecolors='white', linewidths=0.4, zorder=6.5)
    for k, alpha in ((4, 0.9), (8, 0.75)):
        _, top = cube(ax, on(th_tau + step * k), s, phi=np.deg2rad(step * (k - 1)), solid=False, alpha=alpha, z=5.5)
        text(ax, top[0], top[1] + 0.07, f'+{50 * k} ms', ha='center', va='bottom', color=C['target'])
    text(ax, ghost_c[0] - 0.15, ghost_c[1], 'capture τ', ha='right', color=C['muted'])

    # Action: gripper at its start (faint) and meeting the target at tau+L.
    grip_s = 0.38
    tip = now_c[1] - 0.04
    start_top = gripper(ax, now_c[0] + 1.05, y0 + 0.76, grip_s, alpha=0.3)
    now_grip = gripper(ax, now_c[0], tip, grip_s)
    arrow(ax, (start_top[0] - 0.14, start_top[1] - 0.05), (now_grip[0] + 0.10, now_grip[1] + 0.01),
          color=C['act'], lw=0.9, ls=(0, (3, 2)), rad=0.25, z=7, head=1.1)
    text(ax, now_c[0] - 0.17, tip + 0.30, 'τ+L', ha='right', color=C['act'], weight='bold')

    # Role legend, top right.
    lx, ly = x0 + w - 0.98, y0 + h - 0.15
    ax.add_patch(Rectangle((lx, ly - 0.035), 0.07, 0.07, fc=C['target_right'], ec=C['target'], lw=0.6, zorder=8))
    text(ax, lx + 0.11, ly, 'Target: precise', color=C['target'])
    arrow(ax, (lx - 0.01, ly - 0.15), (lx + 0.09, ly - 0.15), color=C['world'], lw=1.0, z=8, head=1.0)
    text(ax, lx + 0.11, ly - 0.15, 'Context: coarse', color=C['world'])
    ax.scatter([lx + 0.01, lx + 0.06], [ly - 0.30, ly - 0.30], s=1.2, color='#BFC8CE', zorder=8)
    text(ax, lx + 0.11, ly - 0.30, 'Rest: ignored', color=C['muted'])
    return x0, w


def ruler(ax, x0, w):
    t0, dt = x0 + 0.42, 0.38
    yt, yb, yl, ya = 0.355, 0.275, 0.195, 0.075
    ax.plot([t0 - 0.06, t0 + 8 * dt + 0.08], [yb, yb], color=C['line'], lw=0.6, zorder=2)
    for k in range(9):
        ax.plot([t0 + k * dt] * 2, [yb - 0.025, yb + 0.025], color=C['line'], lw=0.6, zorder=2)
    ax.scatter([t0 + k * dt for k in range(1, 9)], [yt] * 8, s=6, color=C['target'], edgecolors='white',
               linewidths=0.4, zorder=3)
    for k in range(1, 9):
        ax.add_patch(Rectangle((t0 + k * dt - 0.04, ya - 0.04), 0.08, 0.08, fc=C['act_fill'], ec=C['act'], lw=0.6, zorder=3))
    for k, s in ((0, 'τ'), (1, 'τ+L'), (4, '+200'), (8, '+400 ms')):
        text(ax, t0 + k * dt, yl, s, ha='center', color=C['ink'] if k < 2 else C['muted'])
    text(ax, x0, yt, 'Target', color=C['target'])
    text(ax, x0, ya, 'Action', color=C['act'])


# ---------------------------------------------------------------- (c) success vs latency
def panel_c(ax, fig, ours):
    title(ax, COL_C, '(c) Success vs. latency', 'Dynamic-14, native latency')
    left, bottom, top = COL_C + 0.33, 0.42, 2.22
    pa = fig.add_axes([left / W, bottom / H, (W - left - 0.05) / W, (top - bottom) / H])
    rows = table_rows()
    for family, marker, _ in FAMILY:
        pts = np.array([(r['p95'], r['sr']) for r in rows if r['family'] == family])
        pa.scatter(*pts.T, marker=marker, s=15, color=C['base'], edgecolors='white', linewidths=0.5, zorder=3,
                   label=family)
    pa.axvline(50, color=C['line'], lw=0.6, ls=(0, (3, 2)), zorder=1)
    pa.text(50 * 1.08, 69, 'control\nperiod', fontsize=FS, color=C['muted'], ha='left', va='top', linespacing=0.95)
    wam = [r for r in rows if r['family'] == 'Video WAM']
    best_wam = max(wam, key=lambda r: r['sr'])
    pa.annotate('', (ours['p95_ms'] * 1.12, ours['sr_native'] - 0.6), (best_wam['p95'] / 1.1, best_wam['sr'] + 0.3),
                arrowprops=dict(arrowstyle='-|>,head_length=0.35,head_width=0.18', color=C['ours'], lw=0.7,
                                ls=(0, (2.5, 1.5)), shrinkA=0, shrinkB=0))
    pa.text(np.sqrt(ours['p95_ms'] * best_wam['p95']), (ours['sr_native'] + best_wam['sr']) / 2 - 3.2,
            'N× faster', fontsize=FS, color=C['ours'], ha='center', va='top')
    pa.scatter([ours['p95_ms']], [ours['sr_native']], marker='*', s=75, color=C['ours'], edgecolors='white',
               linewidths=0.5, zorder=4)
    pa.text(ours['p95_ms'] / 1.25, ours['sr_native'] + 3.0, 'FoveaWAM', fontsize=FS, color=C['ours'],
            fontweight='bold', ha='right', va='bottom')
    if ours['status'] != 'final':
        pa.text(ours['p95_ms'] / 1.25, ours['sr_native'] + 2.6, '(placeholder)', fontsize=FS, color=C['muted'],
                ha='right', va='top')
    pa.set_xscale('log'); pa.set_xlim(3, 700); pa.set_ylim(10, 70)
    pa.set_xticks([10, 100], ['10', '100']); pa.set_xticks([], minor=True)
    pa.set_yticks([20, 40, 60])
    pa.set_xlabel('p95 time-to-action (ms)', fontsize=FS, labelpad=1.5, color=C['ink'])
    pa.set_ylabel('Success (%)', fontsize=FS, labelpad=1.5, color=C['ink'])
    pa.tick_params(labelsize=FS, length=2, width=0.4, pad=1.5, colors=C['ink'])
    for side in ('top', 'right'):
        pa.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        pa.spines[side].set_linewidth(0.4); pa.spines[side].set_color(C['line'])
    pa.legend(loc='lower left', fontsize=FS, frameon=False, handletextpad=0.1, borderaxespad=0.05,
              labelspacing=0.25, borderpad=0.05, handlelength=1.0)
    return [r for r in rows if r['family'] != 'ours']


def main():
    plt.rcParams.update({'font.family': 'Arial', 'font.size': FS, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
                         'axes.unicode_minus': True})
    ours = json.loads((ROOT.parents[1] / 'data' / 'ours.json').read_text(encoding='utf-8'))
    fig = plt.figure(figsize=(W, H), facecolor='white', dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    panel_a(ax)
    inputs_and_model(ax)
    x0, w = hero(ax, fig)
    ruler(ax, x0, w)
    for x in (COL_B - 0.10, COL_C - 0.12):
        ax.plot([x, x], [0.06, H - 0.06], color=C['faint'], lw=0.6, zorder=0.5)
    plotted = panel_c(ax, fig, ours)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    sizes, overflow = [], []
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text():
            sizes.append(t.get_fontsize())
            bb = t.get_window_extent(renderer)
            if bb.x0 < -0.5 or bb.y0 < -0.5 or bb.x1 > fig.bbox.width + 0.5 or bb.y1 > fig.bbox.height + 0.5:
                overflow.append(t.get_text())
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(ROOT / f'fig1_concept_v52.{ext}', dpi=600, facecolor='white')
    plt.close(fig)
    report = dict(width_in=W, height_in=H, min_font_pt=min(sizes), max_font_pt=max(sizes), out_of_canvas=overflow,
                  ours=ours, table_rows=[dict(method=r['method'], family=r['family'], sr_native=r['sr'],
                                              p95_ms=r['p95']) for r in plotted])
    (ROOT / 'layout_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('width_in', 'height_in', 'min_font_pt', 'out_of_canvas')}))


if __name__ == '__main__':
    main()
