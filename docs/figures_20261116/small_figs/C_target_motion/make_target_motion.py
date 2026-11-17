"""Target motion during inference (OnTimeBench, Native).

The default figure shows continuous d = v * L, using task-family speed ranges
and measured method p95 time-to-action. It is a constant-speed scale estimate,
not measured displacement or a grasp-tolerance threshold.

Historical executor-time variants use:
    first executed command   age a_first = k * Delta_a (+ d_task),  k = ceil(L / Delta_a)
    later commands of chunk  age up to (2k - 1) * Delta_a (+ d_task) under steady replanning
    target travel            d = v * a
Executor: appendix/benchmark.tex ("Executor").  Speeds: tables/task_definitions.tex.
Latencies (RTX 5090, batch 1, 900 samples; p50/p95/max): results/realtime_c/table1-20261104.json.
check_against_logged_ages() asserts that the executor's logged p95 action age equals (2k-1)*Delta_a
for the two methods that log it (FoveaWAM, pi0.5+SE(3)), at native latency and with +150 ms.

Usage:
    python make_target_motion.py --font Arial
    python make_target_motion.py --variant all --font Arial
"""
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TABLE1 = ROOT / 'results' / 'realtime_c' / 'table1-20261104.json'
COLORS = json.loads((ROOT / 'figures' / 'method_colors.json').read_text(encoding='utf-8'))['methods']

DELTA = 50.0  # ms, control period
# Linear speed ranges (m/s), tables/task_definitions.tex. Pass is angular (deg/s).
FAMILIES = [  # name, v_min, v_max, d_task (ms), colour (core palette, as in Fig. 4)
    ('Capture', 0.55, 1.14, 0.0, '#E69F00'),
    ('Impact', 0.12, 0.14, 50.0, '#C0263A'),
    ('Grasp', 0.03, 0.20, 0.0, '#2859A3'),
    ('Place', 0.03, 0.06, 0.0, '#2E8540'),
]
PASS = ('Pass', 2.5, 7.5, 0.0, '#9467BD')
FIG4A_SPEED = 0.9  # m/s: Fig. 4(a), 18 cm in 200 ms; inside the Capture range 0.55-1.14

KEYS = {
    'act': 'ACT', 'dp': 'DP', 'pi05': 'π0.5', 'pi05_se3': 'π0.5+SE(3)',
    'dynamicvla': 'DynamicVLA', 'puma': 'PUMA', 'openwam_official': 'OpenWAM-α',
    'openwam': 'OpenWAM-α (off)', 'dynamicwam': 'DynamicWAM',
    'dynamicwam_se3': 'DynamicWAM+SE(3)', 'se3_wam': 'FoveaWAM',
}
MATH = {'π0.5': r'$\pi_{0.5}$', 'π0.5+SE(3)': r'$\pi_{0.5}$+SE(3)',
        'OpenWAM-α': r'OpenWAM-$\alpha$', 'OpenWAM-α (off)': r'OpenWAM-$\alpha$ (off)'}
OURS = 'FoveaWAM'
OURS_RED = '#D62728'

SIZE = dict(label=7.0, title=8.0, minor=6.5)
LW = dict(axis=0.55, line=0.85, ours=1.2, grid=0.35)
GRID = '#E5E5E5'
TEXT = '#1A1A1A'
GREY = '#6E6E6E'


def tex(name):
    return MATH.get(name, name)


def k_of(ms):
    return math.ceil(ms / DELTA - 1e-9)


def load_latency():
    out = {}
    for r in json.loads(TABLE1.read_text(encoding='utf-8'))['rows']:
        d = out.setdefault(KEYS[r['method']], dict(
            p50=r['measured_5090_p50_ms'], p95=r['measured_5090_p95_ms'],
            max=r['measured_5090_maximum_ms'], age={}))
        d['age'][r['protocol']] = r['action_age_p95_ms']
    assert len(out) == 11, sorted(out)
    return out


def check_against_logged_ages(lat):
    for m in ('FoveaWAM', 'π0.5+SE(3)'):
        for proto, extra in (('native', 0.0), ('plus150ms', 150.0)):
            k = k_of(lat[m]['p95'] + extra)
            logged = lat[m]['age'][proto]
            assert abs(logged - (2 * k - 1) * DELTA) < 1e-6, (m, proto, k, logged)


def k_groups(lat):
    groups = {}
    for m, d in lat.items():
        groups.setdefault(k_of(d['p95']), []).append(m)
    return {k: sorted(v, key=lambda m: lat[m]['p95']) for k, v in sorted(groups.items())}


def setup_font(font):
    if font not in {f.name for f in font_manager.fontManager.ttflist}:
        raise SystemExit(f'Font {font!r} is not installed; pass --font with an installed font.')
    plt.rcParams.update({
        'font.family': [font], 'font.size': SIZE['label'], 'mathtext.fontset': 'custom',
        'mathtext.rm': font, 'mathtext.it': f'{font}:italic', 'mathtext.bf': f'{font}:bold',
        'mathtext.cal': font, 'mathtext.sf': font,
        'axes.linewidth': LW['axis'], 'xtick.major.width': LW['axis'], 'ytick.major.width': LW['axis'],
        'xtick.minor.width': LW['axis'] * 0.8, 'ytick.minor.width': LW['axis'] * 0.8,
        'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'xtick.minor.size': 1.5,
        'ytick.minor.size': 1.5, 'xtick.labelsize': SIZE['label'], 'ytick.labelsize': SIZE['label'],
        'axes.labelsize': SIZE['label'], 'axes.edgecolor': TEXT, 'text.color': TEXT,
        'xtick.color': TEXT, 'ytick.color': TEXT, 'axes.labelcolor': TEXT,
        'pdf.fonttype': 42, 'svg.fonttype': 'none', 'savefig.dpi': 300,
    })


def style(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.tick_params(pad=1.5)


def fmt_cm(x):
    return f'{x:.1f}' if x < 9.95 else f'{x:.0f}'


# ------------------------------------------------------------- A: staircase over latency
def variant_staircase(lat, out):
    fig = plt.figure(figsize=(3.25, 2.10))
    ax = fig.add_axes([0.13, 0.165, 0.69, 0.585])
    style(ax)
    xs = [i * 0.25 for i in range(1, 801)]  # (0, 200] ms
    for name, vlo, vhi, dtask, col in FAMILIES:
        lo = [vlo * (k_of(x) * DELTA + dtask) / 10 for x in xs]
        hi = [vhi * (k_of(x) * DELTA + dtask) / 10 for x in xs]
        ax.fill_between(xs, lo, hi, color=col, alpha=0.22, lw=0)
        ax.plot(xs, hi, color=col, lw=LW['line'])
        ax.plot(xs, lo, color=col, lw=LW['line'] * 0.6)
    ax.plot([2, 200], [1.14 * 2 / 10, 1.14 * 200 / 10], color=GREY, lw=0.6, ls=(0, (2.5, 1.5)))
    ax.text(118, 1.14 * 118 / 10 * 0.80, r'$v_{\max}L$', color=GREY, fontsize=SIZE['minor'],
            ha='left', va='top', rotation=0)
    ax.set_yscale('log')
    ax.set_ylim(0.1, 40)
    ax.set_xlim(0, 200)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.set_yticks([0.1, 1, 10])
    ax.set_yticklabels(['0.1', '1', '10'])
    ax.set_xlabel('Time-to-action $L$ (ms)', labelpad=1.5)
    ax.set_ylabel('Target travel (cm)', labelpad=1.5)
    ax.grid(True, axis='y', which='major', color=GRID, lw=LW['grid'])
    for b in (50, 100, 150):
        ax.axvline(b, color=GREY, lw=0.45, ls=(0, (1, 1.5)), zorder=0)
    ylab = {'Capture': 14, 'Impact': 3.6, 'Grasp': 1.9, 'Place': 0.62}
    for name, *_, col in FAMILIES:
        ax.text(204, ylab[name], name, color=col, fontsize=SIZE['label'], va='center', ha='left',
                fontweight='bold', clip_on=False)
    # method p95 rug above the plot
    top = fig.add_axes([0.13, 0.765, 0.69, 0.22], sharex=ax)
    top.set_axis_off()
    top.set_ylim(0, 1)
    for m, d in lat.items():
        if d['p95'] <= 200:
            top.plot([d['p95']] * 2, [0, 0.13], color=OURS_RED if m == OURS else TEXT,
                     lw=LW['ours'] if m == OURS else 0.6, solid_capstyle='butt')
    rows = [  # x, lines (bottom first)
        (11, ['ACT', r'$\mathbf{FoveaWAM}$']),
        (80, [r'$\pi_{0.5}$+SE(3), DynamicVLA', r'$\pi_{0.5}$, PUMA, DP,']),
        (152, [r'OpenWAM-$\alpha$', 'DynamicWAM(+SE(3)),']),
    ]
    for x, lines in rows:
        for j, t in enumerate(lines):
            top.text(x, 0.20 + 0.33 * j, t, fontsize=SIZE['minor'], ha='center', va='bottom',
                     color=OURS_RED if 'Fovea' in t else TEXT)
    ax.annotate(r'OpenWAM-$\alpha$ (off): $L$=466 ms', xy=(200, 0.13), xytext=(196, 0.13),
                fontsize=SIZE['minor'], color=GREY, ha='right', va='center',
                arrowprops=dict(arrowstyle='->', color=GREY, lw=0.5))
    save(fig, out, 'cand_A_staircase')


# ------------------------------------------------------------- D: per-method dumbbell
def variant_dumbbell(lat, out):
    order = sorted(lat, key=lambda m: lat[m]['p95'])
    n = len(order)
    fig = plt.figure(figsize=(3.25, 2.12))
    l, b, h = 0.305, 0.135, 0.625
    w1, gap, w2 = 0.47, 0.025, 0.175
    ax = fig.add_axes([l, b, w1, h])
    ax2 = fig.add_axes([l + w1 + gap, b, w2, h], sharey=ax)
    for a, lim in zip((ax, ax2), [(0, 260), (440, 1000)]):
        style(a)
        a.set_xlim(*lim)
        a.grid(True, axis='x', color=GRID, lw=LW['grid'])
        a.set_axisbelow(True)
    ax.set_xticks([0, 50, 100, 150, 200, 250])
    ax.set_xticklabels(['0', '', '100', '', '200', ''])
    ax2.set_xticks([500, 750])
    ax2.spines['left'].set_visible(False)
    ax2.tick_params(axis='y', left=False, labelleft=False)
    kw = dict(color=TEXT, clip_on=False, lw=LW['axis'])
    ax.plot([0.985, 1.015], [-0.035, 0.035], transform=ax.transAxes, **kw)
    ax2.plot([-0.04, 0.04], [-0.035, 0.035], transform=ax2.transAxes, **kw)
    ax.set_ylim(n - 0.4, -0.6)
    ax.set_yticks(range(n))
    ax.set_yticklabels([tex(m) for m in order])
    ax.tick_params(axis='y', length=0)
    for t, m in zip(ax.get_yticklabels(), order):
        if m == OURS:
            t.set_color(OURS_RED)
            t.set_fontweight('bold')
    for i, m in enumerate(order):
        d = lat[m]
        col = COLORS[m]
        k = k_of(d['p95'])
        first, last = k * DELTA, (2 * k - 1) * DELTA
        lw = LW['ours'] if m == OURS else LW['line']
        for a in (ax, ax2):
            if last > first:
                a.add_patch(Rectangle((first, i - 0.17), last - first, 0.34, color=col, alpha=0.28,
                                      lw=0, zorder=2))
            a.plot([d['p95'], first], [i, i], color=col, lw=lw, zorder=3, solid_capstyle='butt')
            a.plot(d['p95'], i, 'o', ms=3.2, mfc='white', mec=col, mew=0.8, zorder=4)
            a.plot(first, i, 'o', ms=3.4, mfc=col, mec=col, mew=0.8, zorder=4)
            logged = d['age'].get('native')
            if logged is not None:
                a.plot(logged, i, marker='|', ms=6.5, mew=0.9, color=TEXT, zorder=5)
    fig.text(l + (w1 + gap + w2) / 2, 0.005, 'Time since capture (ms)', ha='center',
             va='bottom', fontsize=SIZE['label'])
    to_cm = lambda x: x * FIG4A_SPEED / 10
    to_ms = lambda c: c * 10 / FIG4A_SPEED
    for a, ticks in ((ax, [0, 5, 10, 15, 20]), (ax2, [50, 75])):
        sec = a.secondary_xaxis('top', functions=(to_cm, to_ms))
        sec.set_xticks(ticks)
        sec.tick_params(pad=1, labelsize=SIZE['minor'], colors=GREY, length=2, width=LW['axis'])
        sec.spines['top'].set_color(GREY)
        sec.spines['top'].set_linewidth(LW['axis'])
    fig.text(l + (w1 + gap + w2) / 2, b + h + 0.068,
             'Travel of the Fig. 4(a) ball at 0.9 m/s (cm)',
             ha='center', va='bottom', fontsize=SIZE['minor'], color=GREY)
    hdl = [Line2D([], [], marker='o', ls='', ms=3.2, mfc='white', mec=TEXT, mew=0.8),
           Line2D([], [], marker='o', ls='', ms=3.4, mfc=TEXT, mec=TEXT),
           Rectangle((0, 0), 1, 1, color=TEXT, alpha=0.28, lw=0),
           Line2D([], [], marker='|', ls='', ms=6.5, mew=0.9, color=TEXT)]
    labs = ['p95 $L$', r'first command', 'later commands', 'logged p95 age']
    fig.legend(hdl, labs, loc='upper center', bbox_to_anchor=(0.5, 1.0), ncol=4,
               frameon=False, fontsize=SIZE['minor'], handlelength=0.9, handletextpad=0.35,
               columnspacing=0.9, borderaxespad=0.1)
    save(fig, out, 'cand_D_dumbbell')


# ------------------------------------------------------------- C: annotated matrix
def variant_matrix(lat, out):
    groups = k_groups(lat)
    fig = plt.figure(figsize=(3.25, 1.48))
    ax = fig.add_axes([0.215, 0.025, 0.78, 0.685])
    fams = FAMILIES + [PASS]
    nr, nc = len(fams), len(groups)
    ax.set_xlim(0, nc)
    ax.set_ylim(nr, 0)
    ax.set_axis_off()
    lo_log, hi_log = math.log10(0.2), math.log10(60)
    for j, k in enumerate(groups):
        for i, (name, vlo, vhi, dtask, col) in enumerate(fams):
            age = k * DELTA + dtask
            if name == 'Pass':
                lo, hi = vlo * age / 1000, vhi * age / 1000
                s = f'{lo:.1f}–{hi:.1f}' if lo >= 0.95 else f'{lo:.2f}–{hi:.2f}'
                shade = 0.0
            else:
                lo, hi = vlo * age / 10, vhi * age / 10
                s = f'{fmt_cm(lo)}–{fmt_cm(hi)}'
                shade = max(0.0, min(1.0, (math.log10(hi) - lo_log) / (hi_log - lo_log)))
            fc = plt.cm.Greys(0.04 + 0.5 * shade)
            ax.add_patch(Rectangle((j, i), 1, 1, fc=fc, ec='white', lw=1.0))
            ax.text(j + 0.5, i + 0.53, s, ha='center', va='center', fontsize=SIZE['minor'],
                    color='white' if shade > 0.8 else TEXT)
    for i, (name, *_, col) in enumerate(fams):
        unit = '(deg)' if name == 'Pass' else '(cm)'
        ax.text(-0.08, i + 0.53, f'{name} {unit}', ha='right', va='center',
                fontsize=SIZE['label'], color=col, fontweight='bold')
    short = {1: 'ACT,\nFoveaWAM', 2: '5 methods,\n60–97 ms', 3: 'Dynamic-\nWAM',
             4: 'OpenWAM-$\\alpha$,\nDynWAM+S.', 10: 'OpenWAM-\n$\\alpha$ (off)'}
    for j, k in enumerate(groups):
        ax.text(j + 0.5, -0.12, short[k], ha='center', va='bottom', fontsize=SIZE['minor'],
                color=GREY, linespacing=1.05)
        ax.text(j + 0.5, -1.05, f'$k$ = {k}\n{k * int(DELTA)} ms', ha='center', va='bottom',
                fontsize=SIZE['label'], fontweight='bold', linespacing=1.0)
    save(fig, out, 'cand_C_matrix')


def save(fig, out, stem):
    out.mkdir(parents=True, exist_ok=True)
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(out / f'{stem}.{ext}', dpi=300)
    svg_path = out / f'{stem}.svg'
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text(encoding='utf-8').splitlines())
                        + '\n', encoding='utf-8', newline='\n')
    w, h = fig.get_size_inches()
    print(f'{stem}: {w * 72:.0f} x {h * 72:.0f} pt')
    plt.close(fig)


# ------------------------------------------------------------- E: original layout, executor time base
XMAX_E, YMAX_E = 250, 36


def variant_linear(lat, out, stem='cand_E_linear', exact=True):
    """Layout of panel_displacement.png (linear y, family bands, method lines at p95);
    travel uses the executor time k*Delta (exact=True) instead of v*L."""
    fig = plt.figure(figsize=(3.25, 2.20))
    ax = fig.add_axes([0.105, 0.155, 0.725, 0.825])
    style(ax)
    xs = [i * 0.25 for i in range(1, int(XMAX_E * 4) + 1)]
    t = (lambda x: k_of(x) * DELTA) if exact else (lambda x: x)
    for name, vlo, vhi, dtask, col in FAMILIES[::-1]:
        lo = [vlo * (t(x) + dtask) / 10 for x in xs]
        hi = [vhi * (t(x) + dtask) / 10 for x in xs]
        ax.fill_between(xs, lo, hi, color=col, alpha=0.25, lw=0)
        ax.plot(xs, hi, color=col, lw=LW['line'])
        ax.plot(xs, lo, color=col, lw=LW['line'] * 0.6)
    ax.set_xlim(0, XMAX_E)
    ax.set_ylim(0, YMAX_E)
    ax.set_xticks([0, 50, 100, 150, 200, 250])
    ax.set_yticks([0, 10, 20, 30])
    ax.set_xlabel('Inference latency (ms)', labelpad=1.5)
    ax.set_ylabel('Target travel before execution (cm)', labelpad=1.5)
    ax.grid(True, axis='y', color=GRID, lw=LW['grid'])
    ax.set_axisbelow(True)
    # method lines at p95; labels per cluster
    for m, d in lat.items():
        if d['p95'] > XMAX_E:
            continue
        ours = m == OURS
        ax.axvline(d['p95'], color=TEXT if ours else GREY, lw=LW['ours'] if ours else 0.6,
                   ls='-' if ours else (0, (2.5, 1.5)), zorder=1)
    rot = [  # x of text anchor, text, ha, bold  (rotated, read bottom-up, hanging from the top)
        (3.6, 'ACT', 'right', False), (12.6, 'FoveaWAM', 'right', True),
        (58.6, '$\\pi_{0.5}$, PUMA,\n$\\pi_{0.5}$+SE(3)', 'right', False),
        (71.0, 'DP', 'left', False), (95.0, 'DynamicVLA', 'right', False),
        (147.2, 'DynamicWAM', 'right', False),
    ]
    for x, s_, ha, bold in rot:
        ax.text(x, YMAX_E - 0.4, s_, rotation=90, ha=ha, va='top', fontsize=SIZE['minor'],
                color=TEXT if bold else GREY, fontweight='bold' if bold else 'normal',
                linespacing=1.0, rotation_mode='anchor' if False else 'default')
    ax.text(155.5, YMAX_E - 0.6, 'OpenWAM-$\\alpha$,\nDynamicWAM+SE(3)', ha='left', va='top',
            fontsize=SIZE['minor'], color=GREY, linespacing=1.0)
    ylab = {'Capture': 21.0, 'Impact': 5.8, 'Grasp': 3.2, 'Place': 0.9}
    if not exact:
        ylab.update({'Capture': 21.0, 'Impact': 5.0, 'Grasp': 2.9, 'Place': 0.9})
    for name, *_, col in FAMILIES:
        ax.text(XMAX_E * 1.012, ylab[name], name, color=col, fontsize=SIZE['label'], va='center', ha='left',
                fontweight='bold', clip_on=False)
    ax.annotate(r'OpenWAM-$\alpha$ (off): 466 ms', xy=(XMAX_E, 7.0), xytext=(XMAX_E - 3, 7.0),
                fontsize=SIZE['minor'], color=GREY, ha='right', va='center',
                arrowprops=dict(arrowstyle='->', color=GREY, lw=0.5))
    save(fig, out, stem)


# ------------------------------------------------------------- FINAL: continuous v*L (concept figure)
FINAL_STYLE = {  # family: (band alpha, draw order); narrow families on top so they stay legible
    'Capture': (0.20, 1), 'Grasp': (0.16, 2), 'Place': (0.42, 3), 'Impact': (0.55, 4),
}
GUIDE = '#BDBDBD'


def variant_header(lat, out, stem='cand_F_header'):
    """Target travel d = v * L during an inference latency L, per task family; method p95 marked.
    Continuous approximation chosen for presentation (consistent with Fig. 4(a)); because the executor
    hands over at the next 50 ms boundary, v*L is a lower bound on the motion a command must bridge."""
    xmax, ymax = 200, 24
    W, H = 3.25, 2.28
    fig = plt.figure(figsize=(W, H))
    left, right, bottom, head = 0.40, 0.56, 0.34, 0.64       # inches
    ax = fig.add_axes([left / W, bottom / H, (W - left - right) / W, (H - bottom - head) / H])
    hx = fig.add_axes([left / W, (H - head) / H, (W - left - right) / W, (head - 0.02) / H], sharex=ax)
    style(ax)
    hx.set_axis_off()
    hx.set_ylim(0, 1)

    xs = [0.0, float(xmax)]
    for name, vlo, vhi, dtask, col in sorted(FAMILIES, key=lambda f: FINAL_STYLE[f[0]][1]):
        alpha, z = FINAL_STYLE[name]
        ax.fill_between(xs, [vlo * x / 10 for x in xs], [vhi * x / 10 for x in xs],
                        color=col, alpha=alpha, lw=0, zorder=2 + z * 0.1)
        ax.plot(xs, [vhi * x / 10 for x in xs], color=col, lw=LW['line'], zorder=3 + z * 0.1,
                solid_capstyle='butt')
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_xlabel('Inference latency (ms)', labelpad=1.5)
    ax.set_ylabel('Target travel (cm)', labelpad=2.0)

    # guides: light lines through the plot, short ticks in the header
    for m, d in lat.items():
        if d['p95'] > xmax:
            continue
        ours = m == OURS
        ax.axvline(d['p95'], color=TEXT if ours else GUIDE, lw=0.9 if ours else 0.5, zorder=5 if ours else 1)
        hx.plot([d['p95']] * 2, [0, 0.07], color=TEXT if ours else GREY, lw=0.9 if ours else 0.6,
                solid_capstyle='butt', clip_on=False)
    # rotated labels centred over their ticks (x = text centre)
    rot = [
        (5.8, 'ACT', False), (15.6, 'FoveaWAM', True),
        (56.8, r'$\pi_{0.5}$, PUMA,' + '\n' + r'$\pi_{0.5}$+SE(3)', False),
        (71.2, 'DP', False), (97.3, 'DynamicVLA', False),
    ]
    for x, s_, bold in rot:
        hx.text(x, 0.11, s_, rotation=90, ha='center', va='bottom', fontsize=SIZE['minor'],
                color=TEXT if bold else GREY, fontweight='bold' if bold else 'normal', linespacing=1.0,
                clip_on=False)
    hx.text(156, 0.11, 'DynamicWAM (+SE(3)),\nOpenWAM-$\\alpha$', ha='left', va='bottom',
            fontsize=SIZE['minor'], color=GREY, linespacing=1.05, clip_on=False)

    # Fig. 4(a) example on the right edge
    y4 = FIG4A_SPEED * 200 / 10
    ax.plot(200, y4, 'o', ms=3.6, mfc='white', mec=TEXT, mew=0.7, zorder=6, clip_on=False)
    ax.text(194, y4, 'Fig. 4(a)', ha='right', va='center', fontsize=SIZE['minor'], color=TEXT)

    # family labels at the right edge, with speed ranges
    ylab = {'Capture': 16.5, 'Grasp': 4.9, 'Impact': 2.85, 'Place': 0.8}
    for name, vlo, vhi, dtask, col in FAMILIES:
        y = ylab[name]
        ax.text(xmax + 6, y, name, color=col, fontsize=SIZE['label'], va='center', ha='left',
                fontweight='bold', clip_on=False)
    save(fig, out, stem)

# ------------------------------------------------------------- FINAL v3: methods as marks on the Capture band
CAP = FAMILIES[0]
MARKS = [  # (members sharing one mark, label)
    (['ACT'], 'ACT'),
    (['FoveaWAM'], 'FoveaWAM'),
    (['π0.5', 'PUMA', 'π0.5+SE(3)'], '$\\pi_{0.5}$, PUMA,\n$\\pi_{0.5}$+SE(3)'),
    (['DP'], 'DP'),
    (['DynamicVLA'], 'DynamicVLA'),
    (['DynamicWAM', 'OpenWAM-α', 'DynamicWAM+SE(3)'], 'DynamicWAM (+SE(3)),\nOpenWAM-$\\alpha$'),
    (['OpenWAM-α (off)'], 'OpenWAM-$\\alpha$ (off)'),
]


def _bands(ax, x0, x1, log=False):
    n = 60 if log else 2
    xs = [x0 * (x1 / x0) ** (i / (n - 1)) for i in range(n)] if log else [x0, x1]
    for name, vlo, vhi, dtask, col in sorted(FAMILIES, key=lambda f: FINAL_STYLE[f[0]][1]):
        alpha, z = FINAL_STYLE[name]
        ax.fill_between(xs, [vlo * x / 10 for x in xs], [vhi * x / 10 for x in xs],
                        color=col, alpha=alpha, lw=0, zorder=2 + z * 0.1)
        ax.plot(xs, [vhi * x / 10 for x in xs], color=col, lw=LW['line'], zorder=3 + z * 0.1,
                solid_capstyle='butt')


def _marks(ax, lat, place, xmax):
    _, vlo, vhi, _, _ = CAP
    for members, label in MARKS:
        if label not in place:
            continue
        ps = [lat[m]['p95'] for m in members]
        x = sum(ps) / len(ps)
        if x > xmax:
            continue
        ours = members == [OURS]
        col = TEXT if ours else GREY
        y0, y1 = vlo * x / 10, vhi * x / 10
        ax.plot([x, x], [y0, y1], color=col, lw=1.8 if ours else 1.1, solid_capstyle='butt', zorder=6)
        ax.plot(x, y1, 'o', ms=3.6 if ours else 2.8, mfc=col, mec='white', mew=0.5, zorder=7)
        lx, ly, ha, va = place[label]
        ax.annotate(label, xy=(x, y1), xytext=(lx, ly), ha=ha, va=va,
                    fontsize=SIZE['label'] if ours else SIZE['minor'], color=col,
                    fontweight='bold' if ours else 'normal', linespacing=1.0, zorder=7,
                    arrowprops=dict(arrowstyle='-', color=col, lw=0.45, shrinkA=1.0, shrinkB=2.2))


def _family_labels(ax, x, ylab, log=False):
    for name, *_, col in FAMILIES:
        ax.text(x, ylab[name], name, color=col, fontsize=SIZE['label'], va='center', ha='left',
                fontweight='bold', clip_on=False)


def variant_final(lat, out, stem='target_motion'):
    """Refine the user-selected original: family bands and vertical latency guides.

    Five representative guides use individual methods' exact p95; every guide
    is labelled. The full method comparison belongs to Table 1. Continuous v*L is a lower-bound
    scale estimate under the stated speed approximation and handover clock.
    """
    xmax, ymax = 200, 26
    W, H = 3.25, 2.10
    left, right, bottom, top = 0.39, 0.55, 0.34, 0.06
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([left / W, bottom / H, (W - left - right) / W, (H - bottom - top) / H])
    style(ax)

    # Wide bands first, narrow bands above them; both edges show the speed range.
    band_alpha = {'Capture': 0.16, 'Grasp': 0.12, 'Place': 0.20, 'Impact': 0.28}
    for name, vlo, vhi, _, col in sorted(FAMILIES, key=lambda f: FINAL_STYLE[f[0]][1]):
        z = FINAL_STYLE[name][1]
        xs = [0, xmax]
        lo, hi = [0, vlo * xmax / 10], [0, vhi * xmax / 10]
        ax.fill_between(xs, lo, hi, color=col, alpha=band_alpha[name], lw=0, zorder=2 + z * 0.1)
        ax.plot(xs, hi, color=col, lw=0.85, zorder=3 + z * 0.1, solid_capstyle='butt')
        ax.plot(xs, lo, color=col, lw=0.40, alpha=0.85, zorder=3 + z * 0.1,
                solid_capstyle='butt')

    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_xlabel('Inference latency (ms)', labelpad=1.5)
    ax.set_ylabel('Target travel (cm)', labelpad=2.0)
    # One representative per latency cluster; keep ACT as the fastest reference.
    guide_methods = ('ACT', OURS, 'π0.5', 'DynamicVLA', 'OpenWAM-α')
    for name in guide_methods:
        data = lat[name]
        ours = name == OURS
        top_y = 25.5
        ax.plot([data['p95']] * 2, [0, top_y], color=TEXT if ours else '#A6A6A6',
                lw=0.85 if ours else 0.40, ls=(0, (2.4, 1.8)), zorder=1,
                solid_capstyle='butt', dash_capstyle='butt')

    method_labels = [
        (lat['ACT']['p95'] + 1.3, 25.3, 'ACT', 'left', False),
        (lat[OURS]['p95'] + 1.7, 25.3, OURS, 'left', True),
        (57.2, 25.3, r'$\pi_{0.5}$', 'right', False),
        (lat['DynamicVLA']['p95'] + 1.8, 25.3, 'DynamicVLA', 'left', False),
        (147.2, 25.3, r'OpenWAM-$\alpha$', 'right', False),
    ]
    for x, y, label, ha, ours in method_labels:
        ax.text(x, y, label, rotation=90, ha=ha, va='top', linespacing=1.05,
                fontsize=SIZE['label'] if ours else SIZE['minor'],
                color=TEXT if ours else GREY, fontweight='bold' if ours else 'normal', zorder=5)

    family_labels = {'Capture': (16.9, 16.9), 'Grasp': (4.0, 5.3),
                     'Impact': (2.8, 3.0), 'Place': (1.2, 0.75)}
    for name, *_, col in FAMILIES:
        anchor_y, label_y = family_labels[name]
        label_col = '#B37C00' if name == 'Capture' else col
        ax.annotate(name, xy=(xmax, anchor_y), xytext=(xmax + 6, label_y),
                    color=label_col, fontsize=SIZE['label'], fontweight='normal',
                    ha='left', va='center', annotation_clip=False,
                    arrowprops=dict(arrowstyle='-', color=col, lw=0.45, shrinkA=0, shrinkB=0))
    save(fig, out, stem)


def variant_loglog(lat, out, stem='cand_G_loglog'):
    """Log-log axes: the families become parallel strips, all eleven methods fit, nothing is squashed."""
    x0, x1, y0, y1 = 3.0, 700.0, 0.05, 100.0
    W, H = 3.25, 2.05
    left, right, bottom, top = 0.42, 0.56, 0.34, 0.06
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([left / W, bottom / H, (W - left - right) / W, (H - bottom - top) / H])
    style(ax)
    _bands(ax, x0, x1, log=True)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_xticks([5, 10, 50, 100, 500])
    ax.set_xticklabels(['5', '10', '50', '100', '500'])
    ax.set_yticks([0.1, 1, 10, 100])
    ax.set_yticklabels(['0.1', '1', '10', '100'])
    ax.minorticks_off()
    ax.set_xlabel('Inference latency (ms, log)', labelpad=1.5)
    ax.set_ylabel('Target travel (cm, log)', labelpad=2.0)
    place = {
        'ACT': (4.2, 3.0, 'center', 'bottom'),
        'FoveaWAM': (13.0, 7.0, 'center', 'bottom'),
        MARKS[2][1]: (40.0, 22.0, 'center', 'bottom'),
        'DP': (85.0, 13.0, 'left', 'bottom'),
        'DynamicVLA': (97.3, 42.0, 'center', 'bottom'),
        MARKS[5][1]: (150.0, 75.0, 'right', 'bottom'),
        MARKS[6][1]: (466.3, 75.0, 'right', 'bottom'),
    }
    _marks(ax, lat, place, x1)
    y4 = FIG4A_SPEED * 200 / 10
    ax.plot(200, y4, 'o', ms=3.6, mfc='white', mec=TEXT, mew=0.7, zorder=8)
    ax.annotate('Fig. 4(a)', xy=(200, y4), xytext=(260, 6.0), ha='left', va='center',
                fontsize=SIZE['minor'], color=TEXT,
                arrowprops=dict(arrowstyle='-', color=TEXT, lw=0.45, shrinkA=1.0, shrinkB=2.5))
    _family_labels(ax, x1 * 1.08, {'Capture': 60.0, 'Grasp': 9.0, 'Impact': 5.2, 'Place': 2.4})
    save(fig, out, stem)

VARIANTS = {'final': variant_final, 'loglog': variant_loglog, 'header': variant_header, 'linear': variant_linear, 'staircase': variant_staircase, 'dumbbell': variant_dumbbell, 'matrix': variant_matrix}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--variant', default='final', choices=['all', *VARIANTS])
    p.add_argument('--font', default='Arial')
    p.add_argument('--lang', default='en', choices=['en', 'zh'])
    p.add_argument('--output-dir', default=None, help='default: . for final, candidates/ otherwise')
    a = p.parse_args()
    if a.lang != 'en':
        raise SystemExit('The Chinese version is produced after the English figure is approved.')
    setup_font(a.font)
    lat = load_latency()
    check_against_logged_ages(lat)
    out = Path(a.output_dir) if a.output_dir else (HERE if a.variant == 'final' else HERE / 'candidates')
    for name, fn in VARIANTS.items():
        if a.variant == name or (a.variant == 'all' and name != 'final'):
            fn(lat, out)


if __name__ == '__main__':
    main()
