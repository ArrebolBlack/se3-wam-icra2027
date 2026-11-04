"""Draw Fig. 1 (teaser) from data/ (real ConMoto frame + training labels) and Table 1.

Run from this directory with the paper environment (requirements.txt at the repo root):

    ../../.venv/Scripts/python.exe build_fig1.py

Writes fig1.pdf (paper), fig1.svg (editable), fig1.png (600 dpi preview) and layout_report.json.
"""
from pathlib import Path
import json
import re

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.text import Text
from PIL import Image

ROOT = Path(__file__).resolve().parent
TABLE = ROOT.parents[1] / 'tables' / 'main_results.tex'
CORAL, TEAL = '#D85A30', '#1D9E75'
INK, GREY, MID, LIGHT = '#222222', '#555555', '#8C8C8C', '#C8C8C8'
W, H, GAP = 6.875, 2.4, 0.15
A_W = (W - GAP) * 0.6
FS, TITLE_FS = 7, 8
FLOW_MIN_M = 0.010          # below this 400 ms displacement a patch is drawn as a near-zero dot
AXIS_M = (0.028, 0.012, 0.008)  # drawn length of the target x/y/z axes (graphic only)
SCENE_CROP = (0, 224, 6, 206)   # x0, x1, y0, y1 in the 224 px frame: trims wall and floor edges only
FAMILY = [('Reactive', 'o', ('ACT', 'DP ')), ('VLA', '^', ('$\\pi_{0.5}$', 'DynamicVLA', 'PUMA')),
          ('Video WAM', 's', ('OpenWAM', 'DynamicWAM'))]


def table_rows():
    rows = []
    for line in TABLE.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.rstrip().rstrip('\\').split('&')]
        if len(cells) != 9 or cells[0].startswith('\\tablelang') or cells[0] == '':
            continue
        name = re.sub(r'\s*\\cite\{[^}]*\}', '', cells[0])
        value = lambda c: re.sub(r'\\(best|second)cell\{([^}]*)\}', r'\2', c)
        family = next((f for f, _, keys in FAMILY if any((name + ' ').startswith(k) for k in keys)), None)
        if name.startswith('\\ours'):
            rows.append(dict(method=name, family='ours', sr=None, p95=None, pending='\\resultplaceholder' in line))
        elif family:
            rows.append(dict(method=name, family=family, sr=float(value(cells[5])), p95=float(value(cells[8]))))
    return rows


def axes_in(fig, x, y, w, h):
    return fig.add_axes([x / W, y / H, w / W, h / H])


def casing(width):
    return [pe.Stroke(linewidth=width, foreground='white'), pe.Normal()]


def project(points, camera, intrinsic):
    cam = (points - camera[:3, 3]) @ camera[:3, :3]
    uv = cam @ intrinsic.T
    return uv[..., :2] / uv[..., 2:3]


def smooth_mask(mask, up=4):
    """Pixel mask -> softened field on an up-sampled grid, so the outline is not a pixel staircase."""
    field = np.kron(mask.astype(float), np.ones((up, up)))
    kernel = np.ones(up + 1) / (up + 1)
    for axis in (0, 1):
        field = np.apply_along_axis(lambda v: np.convolve(v, kernel, mode='same'), axis, field)
    coords = (np.arange(mask.shape[0] * up) + 0.5) / up - 0.5
    return coords, field


def outline(ax, mask, halo=None, fill=None, **kw):
    coords, field = smooth_mask(mask)
    if fill:
        ax.contourf(coords, coords, field, levels=[0.5, 2], **fill)
    contour = ax.contour(coords, coords, field, levels=[0.5], **kw)
    if halo:
        contour.set_path_effects(casing(halo))
    return contour


def draw_triads(ax, lab, lw=0.8):
    cam, K = lab['world_from_camera_cv'], lab['camera_intrinsics']
    pos, rot = lab['target_position_world_m'][1:], lab['target_rotation_world'][1:]
    origin = project(pos, cam, K)
    colors = (CORAL, GREY, MID)
    segments = []
    for h in range(len(pos)):
        for axis in range(3):
            tip = project(pos[h] + rot[h][:, axis] * AXIS_M[axis], cam, K)
            segments.append((h, axis, origin[h], tip))
    # Thin casings first so that eight overlapping triads stay separable, not a white blob.
    for _, _, o, t in segments:
        ax.plot(*zip(o, t), color='white', lw=lw + 0.7, alpha=0.8, solid_capstyle='round', zorder=4)
    for h, axis, o, t in segments:
        ax.plot(*zip(o, t), color=colors[axis], lw=lw if axis == 0 else lw * 0.75,
                alpha=1 - 0.45 * h / (len(pos) - 1), solid_capstyle='round', zorder=5)
    ax.scatter(*origin.T, s=2.5, color=CORAL, edgecolors='white', linewidths=0.3, zorder=6)
    return origin


def panel_a(fig, rgb, lab, src):
    fig.text(0, (H - 0.03) / H, '(a) Precise where contact demands it', fontsize=TITLE_FS,
             fontweight='bold', va='top', ha='left')
    img_y, img_h = 0.52, 1.66
    x0, x1, y0, y1 = SCENE_CROP
    scene_w = img_h * (x1 - x0) / (y1 - y0)
    scene = axes_in(fig, 0, img_y, scene_w, img_h)
    extent = (-0.5, 223.5, 223.5, -0.5)
    scene.imshow(rgb, extent=extent, interpolation='bilinear')
    scene.set_xlim(x0 - 0.5, x1 - 0.5); scene.set_ylim(y1 - 0.5, y0 - 0.5)

    src_px, end = lab['source_px_xy'], lab['flow_end_px'][:, -1]
    mag = np.linalg.norm(lab['flow_robot_base_m'][:, -1], axis=-1)
    moving = lab['flow_valid'][:, -1] & (mag >= FLOW_MIN_M)
    still = ~moving
    scene.scatter(*src_px[still].T, s=1.6, color='#D4D4D4', edgecolors='#4A4A4A', linewidths=0.25, zorder=3)
    for (sx, sy), (ex, ey) in zip(src_px[moving], end[moving]):
        scene.add_patch(FancyArrowPatch((sx, sy), (ex, ey), arrowstyle='-|>,head_length=2.2,head_width=1.3',
                                        color=TEAL, lw=0.8, shrinkA=0, shrinkB=0, zorder=4,
                                        path_effects=casing(1.8)))
    scene.scatter(*src_px[moving].T, s=2.2, color=TEAL, edgecolors='white', linewidths=0.3, zorder=5)
    outline(scene, lab['target_mask_tau'], halo=1.5, colors=CORAL, linewidths=0.7, zorder=6)

    # Zoom on the target: same frame, same pixel coordinates.
    pos_px = project(lab['target_position_world_m'], lab['world_from_camera_cv'], lab['camera_intrinsics'])
    ys, xs = np.nonzero(lab['target_mask_tau'] | lab['target_mask_tau_plus_L'])
    zoom_x0 = scene_w + 0.12
    zoom_w = A_W - zoom_x0
    aspect = zoom_w / img_h
    cx = (min(xs.min(), pos_px[:, 0].min()) + max(xs.max(), pos_px[:, 0].max())) / 2 + 2
    cy = (min(ys.min(), pos_px[:, 1].min()) + max(ys.max(), pos_px[:, 1].max())) / 2
    zh = 31.0
    zw = zh * aspect
    zx0, zy0 = cx - zw / 2, cy - zh / 2
    zoom = axes_in(fig, zoom_x0, img_y, zoom_w, img_h)
    zoom.imshow(rgb, extent=extent, interpolation='bilinear')
    zoom.set_xlim(zx0, zx0 + zw); zoom.set_ylim(zy0 + zh, zy0)
    ghost = outline(zoom, lab['target_mask_tau_plus_L'], colors=CORAL, linewidths=1.2, alpha=0.55, zorder=2)
    ghost.set_path_effects([pe.Stroke(linewidth=2.6, foreground='white', alpha=0.5), pe.Normal()])
    outline(zoom, lab['target_mask_tau'], halo=1.9, colors=CORAL, linewidths=0.9, zorder=3)
    origin = draw_triads(zoom, lab)
    horizons = src['horizons_ms']
    # Name the first and last horizon beside the trajectory, on the side away from the x axes.
    along = (origin[-1] - origin[0]) / np.linalg.norm(origin[-1] - origin[0])
    normal = np.array([along[1], -along[0]])
    for idx, back, lift in ((0, -1, 3.2), (len(origin) - 1, 1, 2.4)):
        xy = origin[idx] + normal * lift + along * back * 1.2
        zoom.text(*xy, f'{horizons[idx]} ms', fontsize=FS, color=INK, ha='center', va='center', zorder=7,
                  path_effects=casing(1.8))
    for ax in (scene, zoom):
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_linewidth(0.4); s.set_color(GREY)
    scene.add_patch(Rectangle((zx0, zy0), zw, zh, fill=False, ec='white', lw=1.4, zorder=7))
    scene.add_patch(Rectangle((zx0, zy0), zw, zh, fill=False, ec=INK, lw=0.5, zorder=8))
    for (px, py), top in (((zx0 + zw, zy0), 1), ((zx0 + zw, zy0 + zh), 0)):
        p = fig.transFigure.inverted().transform(scene.transData.transform((px, py)))
        q = (zoom_x0 / W, (img_y + top * img_h) / H)
        fig.add_artist(Line2D([p[0], q[0]], [p[1], q[1]], color=GREY, lw=0.4, ls=(0, (2, 1.5))))
    timeline(fig)
    legend_a(fig)


def timeline(fig):
    ax = axes_in(fig, 0, 0.17, A_W, 0.31)
    ax.set_xlim(0, A_W); ax.set_ylim(0, 0.31); ax.axis('off')
    y, t0, t1 = 0.20, 0.75, 2.95
    ax.plot([0.08, t0], [y, y], color=GREY, lw=0.6)
    ax.plot([t0, t1], [y, y], color=GREY, lw=0.6, ls=(0, (3, 2)))
    ax.annotate('', (A_W - 0.05, y), (t1, y), arrowprops=dict(arrowstyle='-|>,head_length=0.35,head_width=0.18',
                                                             color=GREY, lw=0.6, shrinkA=0, shrinkB=0))
    for t in (t0, t1):
        ax.plot([t, t], [y - 0.045, y + 0.045], color=INK, lw=0.7)
    ax.text((t0 + t1) / 2, y + 0.035, 'inference $L$', fontsize=FS, ha='center', va='bottom', color=INK)
    sw = 0.15
    for t, label, solid in ((t0, 'capture $\\tau$', True), (t1, 'execution $\\tau{+}L$', False)):
        ax.add_patch(Rectangle((t - 0.36, y - 0.17), sw, 0.085, fc='none', ec=CORAL,
                               lw=0.9 if solid else 1.2, alpha=1 if solid else 0.55))
        ax.text(t - 0.36 + sw + 0.05, y - 0.128, label, fontsize=FS, ha='left', va='center', color=INK)
    ax.text(0.08, y + 0.035, 'time', fontsize=FS, ha='left', va='bottom', color=GREY)


def legend_a(fig):
    ax = axes_in(fig, 0, 0.0, A_W, 0.15)
    ax.set_xlim(0, A_W); ax.set_ylim(0, 0.15); ax.axis('off')
    y = 0.07
    ox = 0.10
    for (dx, dy), c in (((0.17, -0.02), CORAL), ((0.05, 0.05), GREY), ((0.0, 0.04), MID)):
        ax.plot([ox, ox + dx], [y - 0.02, y - 0.02 + dy], color=c, lw=0.9 if c == CORAL else 0.7,
                solid_capstyle='round')
    ax.scatter([ox], [y - 0.02], s=2.5, color=CORAL, edgecolors='white', linewidths=0.3, zorder=3)
    ax.text(ox + 0.24, y, 'Target SE(3), 8 horizons', fontsize=FS, va='center', ha='left', color=INK)
    ax2 = 2.15
    ax.annotate('', (ax2 + 0.2, y), (ax2, y), arrowprops=dict(arrowstyle='-|>,head_length=0.3,head_width=0.15',
                                                               color=TEAL, lw=0.9, shrinkA=0, shrinkB=0))
    ax.text(ax2 + 0.28, y, 'Sparse 3D flow', fontsize=FS, va='center', ha='left', color=INK)


def panel_b(fig, ours):
    bx = A_W + GAP
    fig.text(bx / W, (H - 0.03) / H, '(b) Success vs. latency', fontsize=TITLE_FS, fontweight='bold',
             va='top', ha='left')
    left, bottom = 0.40, 0.36
    ax = axes_in(fig, bx + left, bottom, W - bx - left - 0.04, H - bottom - 0.30)
    rows = table_rows()
    for family, marker, _ in FAMILY:
        pts = np.array([(r['p95'], r['sr']) for r in rows if r['family'] == family])
        ax.scatter(*pts.T, marker=marker, s=16, color='#8A8A8A', edgecolors='white', linewidths=0.5,
                   zorder=3, label=family)
    ax.axvline(50, color=GREY, lw=0.6, ls=(0, (3, 2)), zorder=1)
    ax.text(50 * 1.08, 69.5, 'control period', fontsize=FS, color=GREY, ha='left', va='top')
    ax.scatter([ours['p95_ms']], [ours['sr_native']], s=46, color=CORAL, edgecolors='white', linewidths=0.6, zorder=4)
    ax.text(ours['p95_ms'] / 1.2, ours['sr_native'], 'FoveaWAM', fontsize=FS, color=CORAL, fontweight='bold',
            ha='right', va='center')
    if ours['status'] != 'final':
        ax.text(ours['p95_ms'] / 1.2, ours['sr_native'] - 4.2, '(placeholder)', fontsize=FS, color=GREY,
                ha='right', va='center')
    ax.set_xscale('log')
    ax.set_xlim(3, 700); ax.set_ylim(10, 70)
    ax.set_xticks([10, 100], ['10', '100']); ax.set_xticks([], minor=True)
    ax.set_yticks([20, 40, 60])
    ax.set_xlabel('p95 time-to-action (ms, log)', fontsize=FS, labelpad=2)
    ax.set_ylabel('SR at native latency (%)', fontsize=FS, labelpad=2)
    ax.tick_params(labelsize=FS, length=2, width=0.4, pad=1.5, colors=INK)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_linewidth(0.4)
    ax.legend(loc='lower left', fontsize=FS, frameon=False, handletextpad=0.2, borderaxespad=0.1,
              labelspacing=0.3, borderpad=0.1, handlelength=1.0)
    return [r for r in rows if r['family'] != 'ours']


def main():
    plt.rcParams.update({'font.family': 'Arial', 'font.size': FS, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
                         'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',
                         'axes.unicode_minus': True})
    src = json.loads((ROOT / 'data' / 'source.json').read_text(encoding='utf-8'))
    ours = json.loads((ROOT / 'data' / 'ours.json').read_text(encoding='utf-8'))
    lab = dict(np.load(ROOT / 'data' / 'labels.npz'))
    rgb = np.asarray(Image.open(ROOT / 'data' / 'frame_tau_rgb.png').convert('RGB'))
    fig = plt.figure(figsize=(W, H), facecolor='white', dpi=150)
    panel_a(fig, rgb, lab, src)
    plotted = panel_b(fig, ours)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    sizes, overflow = [], []
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text():
            sizes.append(t.get_fontsize())
            b = t.get_window_extent(renderer)
            if b.x0 < -0.5 or b.y0 < -0.5 or b.x1 > fig.bbox.width + 0.5 or b.y1 > fig.bbox.height + 0.5:
                overflow.append(t.get_text())
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(ROOT / f'fig1.{ext}', dpi=600, facecolor='white')
    plt.close(fig)
    report = dict(width_in=W, height_in=H, panel_a_width_in=round(A_W, 3), panel_gap_in=GAP,
                  min_font_pt=min(sizes), max_font_pt=max(sizes), out_of_canvas=overflow,
                  tau_frame=src['tau_frame_index'], tau_plus_L_frame=src['tau_plus_L_frame_index'],
                  latency_ms=src['latency_ms_rounded'], ours=ours,
                  table_rows=[dict(method=r['method'], family=r['family'], sr_native=r['sr'], p95_ms=r['p95'])
                              for r in plotted])
    try:
        import pymupdf
        page = pymupdf.open(ROOT / 'fig1.pdf')[0]
        report.update(pdf_size_pt=[round(v, 2) for v in page.rect[2:]], pdf_fonts=sorted({f[3] for f in page.get_fonts()}),
                      pdf_raster_images=len(page.get_images()))
    except ImportError:
        pass
    (ROOT / 'layout_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
